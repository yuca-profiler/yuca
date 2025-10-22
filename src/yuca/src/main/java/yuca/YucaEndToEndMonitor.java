package yuca;

import static java.util.stream.Collectors.toList;
import static yuca.util.DataOperations.forwardApply;

import java.util.List;
import java.util.Optional;
import java.util.logging.Logger;
import yuca.emissions.EmissionsConverter;
import yuca.emissions.LocaleEmissionsConverters;
import yuca.linux.jiffies.ProcStat;
import yuca.linux.jiffies.SystemSample;
import yuca.signal.Component;
import yuca.signal.Report;
import yuca.signal.Signal;
import yuca.signal.SignalInterval;
import yuca.signal.SignalInterval.SignalData;
import yuca.signal.SignalInterval.Timestamp;
import yuca.util.LoggerUtil;
import yuca.util.Timestamps;

/** A class to collect and provide yuca signals for single sampling. */
public final class YucaEndToEndMonitor implements YucaMonitor {
  private static final Logger logger = LoggerUtil.getLogger();

  private static final String OS_NAME = System.getProperty("os.name", "unknown");
  private static final String PROC_STAT = "/proc/stat";

  // TODO: do we need to wire this back in?
  private final RaplSource raplSource = RaplSource.getRaplSource();
  private final EmissionsConverter converter = LocaleEmissionsConverters.forDefaultLocale();

  private MonotonicTimeSample monotonicTimeStart;
  private MonotonicTimeSample monotonicTimeEnd;
  private SystemSample systemStart;
  private SystemSample systemEnd;
  private Optional<?> raplStart;
  private Optional<?> raplEnd;

  /** Starts the sampling. */
  @Override
  public void start() {
    logger.info("starting yuca");

    monotonicTimeStart = new MonotonicTimeSample();
    systemStart = ProcStat.sampleCpus();
    raplStart = raplSource.source.get();
  }

  /**
   * Stops the sampling and merges the data they collected into a {@link YucaReport}. Returns an
   * empty {@link Optional} if yuca wasn't running.
   */
  @Override
  public Optional<Report> stop() {
    logger.info("stopping yuca");

    monotonicTimeEnd = new MonotonicTimeSample();
    systemEnd = ProcStat.sampleCpus();
    raplEnd = raplSource.source.get();

    Component.Builder systemComponent =
        Component.newBuilder().setComponentType("linux_system").setComponentId(OS_NAME);

    // physical signals
    logger.info("creating monotonic time signal");
    createPhysicalSignal(
            forwardApply(
                List.of(monotonicTimeStart, monotonicTimeEnd),
                YucaEndToEndMonitor::monotonicTimeDifference),
            Signal.Unit.NANOSECONDS,
            "clock_gettime(CLOCK_MONOTONIC, &ts)")
        .ifPresent(systemComponent::addSignal);

    Optional<Signal> raplEnergy =
        createPhysicalSignal(
            forwardApply(
                List.of(raplStart, raplEnd).stream()
                    .filter(Optional::isPresent)
                    .map(Optional::get)
                    .collect(toList()),
                raplSource::difference),
            Signal.Unit.JOULES,
            raplSource.name);
    raplEnergy.ifPresent(systemComponent::addSignal);
    logger.info("creating system jiffies signal");

    Optional<Signal> systemJiffies =
        createPhysicalSignal(
            forwardApply(List.of(systemStart, systemEnd), ProcStat::between),
            Signal.Unit.JIFFIES,
            PROC_STAT);
    systemJiffies.ifPresent(systemComponent::addSignal);

    // virtual signals
    if (raplEnergy.isEmpty()) {
      logger.info("not creating rapl emissions: no rapl energy");
    } else {
      logger.info("creating rapl emissions signal");
      systemComponent.addSignal(convertToEmissions(raplEnergy.get()));
    }

    Report.Builder report = Report.newBuilder();
    if (systemComponent.getSignalCount() > 0) {
      report.addComponent(systemComponent);
    }
    if (report.getComponentCount() > 0) {
      return Optional.of(report.build());
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
