package yuca;

import static java.util.stream.Collectors.toList;
import static yuca.util.DataOperations.forwardApply;
import static yuca.util.DataOperations.forwardPartialAlign;

import java.util.List;
import java.util.Optional;
import java.util.concurrent.ScheduledExecutorService;
import java.util.logging.Logger;
import yuca.emissions.EmissionsConverter;
import yuca.emissions.LocaleEmissionsConverters;
import yuca.linux.freq.CpuFreq;
import yuca.linux.freq.CpuFrequencySample;
import yuca.linux.jiffies.EflectAccounting;
import yuca.linux.jiffies.JiffiesAccounting;
import yuca.linux.jiffies.ProcStat;
import yuca.linux.jiffies.ProcTask;
import yuca.linux.jiffies.ProcessSample;
import yuca.linux.jiffies.SystemSample;
import yuca.linux.thermal.SysThermal;
import yuca.linux.thermal.ThermalZonesSample;
import yuca.signal.Component;
import yuca.signal.Report;
import yuca.signal.Signal;
import yuca.signal.SignalInterval;
import yuca.signal.SignalInterval.SignalData;
import yuca.signal.SignalInterval.Timestamp;
import yuca.util.LoggerUtil;
import yuca.util.SamplingFuture;
import yuca.util.Timestamps;

/** A class to collect and provide yuca signals. */
public final class YucaApplicationMonitor implements YucaMonitor {
  private static final Logger logger = LoggerUtil.getLogger();

  private static final String OS_NAME = System.getProperty("os.name", "unknown");
  private static final String PROC_STAT = "/proc/stat";

  // TODO: do we need to wire this back in?
  private final RaplSource raplSource = RaplSource.getRaplSource();
  private final EmissionsConverter converter = LocaleEmissionsConverters.forDefaultLocale();
  private final int periodMillis;
  private final long processId;
  private final ScheduledExecutorService executor;

  private boolean isRunning = false;
  private SamplingFuture<MonotonicTimeSample> monotonicTimeFuture;
  private SamplingFuture<ProcessSample> processFuture;
  private SamplingFuture<SystemSample> systemFuture;
  private SamplingFuture<Optional<?>> raplFuture;
  private SamplingFuture<ThermalZonesSample> systemTemperatureFuture;
  private SamplingFuture<CpuFrequencySample> frequencyFuture;

  public YucaApplicationMonitor(
      int periodMillis, long processId, ScheduledExecutorService executor) {
    this.periodMillis = periodMillis;
    this.processId = processId;
    this.executor = executor;
  }

  /** Starts the sampling futures is we aren't already running. */
  @Override
  public void start() {
    synchronized (this) {
      if (!isRunning && ProcessHandle.of(processId).isPresent()) {
        logger.info(
            String.format("starting yuca for process %d at %d ms", processId, periodMillis));
        monotonicTimeFuture =
            SamplingFuture.fixedPeriodMillis(MonotonicTimeSample::new, periodMillis, executor);
        // TODO: there's a conceptual hole here if
        processFuture =
            SamplingFuture.fixedPeriodMillis(
                () -> ProcTask.sampleTasksFor(processId), periodMillis, executor);
        systemFuture =
            SamplingFuture.fixedPeriodMillis(ProcStat::sampleCpus, periodMillis, executor);
        raplFuture =
            SamplingFuture.fixedPeriodMillis(raplSource.source::get, periodMillis, executor);
        systemTemperatureFuture =
            SamplingFuture.fixedPeriodMillis(SysThermal::sample, periodMillis, executor);
        frequencyFuture = SamplingFuture.fixedPeriodMillis(CpuFreq::sample, periodMillis, executor);
        isRunning = true;
      }
    }
  }

  /**
   * Stops the sampling futures and merges the data they collected into a {@link YucaReport}.
   * Returns an empty {@link Optional} if yuca wasn't running.
   */
  // TODO: this can throw if any of the futures are empty. i don't know how to handle this yet
  @Override
  public Optional<Report> stop() {
    synchronized (this) {
      if (isRunning) {
        logger.info("stopping yuca");
        isRunning = false;

        String procTask = String.format("/proc/%d/task", processId);
        Component.Builder processComponent =
            Component.newBuilder()
                .setComponentType("linux_process")
                .setComponentId(Long.toString(processId));
        Component.Builder systemComponent =
            Component.newBuilder().setComponentType("linux_system").setComponentId(OS_NAME);

        // physical signals
        logger.info("creating monotonic time signal");
        createPhysicalSignal(
                forwardApply(
                    monotonicTimeFuture.get(), YucaApplicationMonitor::monotonicTimeDifference),
                Signal.Unit.NANOSECONDS,
                "clock_gettime(CLOCK_MONOTONIC, &ts)")
            .ifPresent(systemComponent::addSignal);

        logger.info("creating rapl energy signal");
        Optional<Signal> raplEnergy =
            createPhysicalSignal(
                forwardApply(
                    raplFuture.get().stream()
                        .filter(Optional::isPresent)
                        .map(Optional::get)
                        .collect(toList()),
                    raplSource::difference),
                Signal.Unit.JOULES,
                raplSource.name);
        raplEnergy.ifPresent(systemComponent::addSignal);

        logger.info("creating process jiffies signal");
        Optional<Signal> processJiffies =
            createPhysicalSignal(
                forwardApply(processFuture.get(), ProcTask::between),
                Signal.Unit.JIFFIES,
                procTask);
        processJiffies.ifPresent(processComponent::addSignal);

        logger.info("creating system jiffies signal");
        Optional<Signal> systemJiffies =
            createPhysicalSignal(
                forwardApply(systemFuture.get(), ProcStat::between),
                Signal.Unit.JIFFIES,
                PROC_STAT);
        systemJiffies.ifPresent(systemComponent::addSignal);

        logger.info("creating cpu temperature signal");
        createPhysicalSignal(
                forwardApply(systemTemperatureFuture.get(), SysThermal::difference),
                Signal.Unit.CELSIUS,
                "/sys/class/thermal")
            .ifPresent(systemComponent::addSignal);

        logger.info("creating cpu frequency signal");
        createPhysicalSignal(
                forwardApply(frequencyFuture.get(), CpuFreq::difference),
                Signal.Unit.HERTZ,
                "/sys/devices/system/cpu/cpu_i/cpufreq")
            .ifPresent(systemComponent::addSignal);
        monotonicTimeFuture = null;
        systemTemperatureFuture = null;
        processFuture = null;
        systemFuture = null;
        raplFuture = null;
        frequencyFuture = null;

        // virtual signals
        if (raplEnergy.isEmpty()) {
          logger.info("not creating rapl emissions: no rapl energy");
        } else {
          logger.info("creating rapl emissions signal");
          systemComponent.addSignal(convertToEmissions(raplEnergy.get()));
        }

        if (processJiffies.isEmpty() && systemJiffies.isEmpty()) {
          logger.info("not creating linux process activity: no jiffies");
        } else {
          List<SignalInterval> activity =
              forwardPartialAlign(
                  processJiffies.get().getIntervalList(),
                  systemJiffies.get().getIntervalList(),
                  JiffiesAccounting::computeTaskActivity);
          if (activity.size() > 0) {
            logger.info("creating linux process activity signal");
            processComponent.addSignal(
                Signal.newBuilder()
                    .setUnit(Signal.Unit.ACTIVITY)
                    .addSource(procTask)
                    .addSource(PROC_STAT)
                    .addAllInterval(activity));
            if (raplEnergy.isPresent()) {
              logger.info("creating linux process energy signal");
              Signal processEnergy =
                  Signal.newBuilder()
                      .setUnit(Signal.Unit.JOULES)
                      .addSource(procTask)
                      .addSource(PROC_STAT)
                      .addSource("/sys/devices/virtual/powercap/intel-rapl")
                      .addAllInterval(
                          forwardPartialAlign(
                              activity,
                              raplEnergy.get().getIntervalList(),
                              EflectAccounting::computeTaskEnergy))
                      .build();
              processComponent.addSignal(processEnergy);

              logger.info("creating linux process emissions signal");
              processComponent.addSignal(convertToEmissions(processEnergy));
            } else {
              logger.info("not creating linux process energy: no rapl energy");
            }
          } else {
            logger.info("not creating linux process activity: no activity");
          }
        }
        Report.Builder report = Report.newBuilder();
        if (systemComponent.getSignalCount() > 0) {
          report.addComponent(systemComponent);
        }
        if (processComponent.getSignalCount() > 0) {
          report.addComponent(processComponent);
        }
        if (report.getComponentCount() > 0) {
          return Optional.of(report.build());
        }
      }
    }
    return Optional.empty();
  }

  @Override
  public Signal convertToEmissions(Signal signal) {
    return converter.convert(signal);
  }

  private Optional<Signal> createPhysicalSignal(
      List<SignalInterval> intervals, Signal.Unit unit, String source) {
    if (intervals.isEmpty()) {
      return Optional.empty();
    }
    return Optional.of(
        Signal.newBuilder().setUnit(unit).addSource(source).addAllInterval(intervals).build());
  }

  private static class MonotonicTimeSample {
    private final Timestamp timestamp;
    private final Timestamp monotonicTime;

    private MonotonicTimeSample() {
      this.timestamp = Timestamps.now();
      this.monotonicTime = Timestamps.monotonicTime();
    }
  }

  private static SignalInterval monotonicTimeDifference(
      MonotonicTimeSample first, MonotonicTimeSample second) {
    return SignalInterval.newBuilder()
        .setStart(first.timestamp)
        .setEnd(second.timestamp)
        .addData(
            SignalData.newBuilder()
                .setValue(
                    (double)
                        (1000000000 * first.monotonicTime.getSecs()
                            + first.monotonicTime.getNanos())))
        .build();
  }
}
