package yuca.benchmarks.util;

import static yuca.benchmarks.util.LoggerUtil.getLogger;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Level;
import java.util.logging.Logger;
import yuca.YucaApplicationMonitor;
import yuca.YucaEndToEndMonitor;
import yuca.YucaMonitor;
import yuca.signal.Component;
import yuca.signal.Report;
import yuca.signal.Signal;

public final class YucaUtil {
  private static final Logger logger = getLogger();
  private static final int CPU_COUNT = Runtime.getRuntime().availableProcessors();

  private static final int DEFAULT_PERIOD_MS = 10;
  private static final String OUTPUT_PATH = System.getProperty("yuca.benchmarks.output", "/tmp");
  private static final AtomicInteger counter = new AtomicInteger(0);
  private static final ScheduledExecutorService executor =
      Executors.newSingleThreadScheduledExecutor(
          r -> {
            Thread t = new Thread(r, "yuca-sampling-thread");
            t.setDaemon(true);
            return t;
          });

  public static YucaMonitor createYuca() {
    String period = System.getProperty("yuca.benchmarks.period", "10");
    int periodMillis = DEFAULT_PERIOD_MS;
    try {
      periodMillis = Integer.parseInt(period);
    } catch (Exception e) {
      logger.log(Level.INFO, String.format("ignoring bad period (%s) for new Yuca", period), e);
      return new YucaApplicationMonitor(DEFAULT_PERIOD_MS, ProcessHandle.current().pid(), executor);
    }
    if (periodMillis < 0) {
      logger.info(String.format("rejecting negative period (%d) for new Yuca", periodMillis));
      return new YucaApplicationMonitor(DEFAULT_PERIOD_MS, ProcessHandle.current().pid(), executor);
    }
    if (periodMillis == 0) {
      logger.info(
          String.format(
              "creating end to end Yuca monitor with period of %d milliseconds", periodMillis));
      return new YucaEndToEndMonitor();
    }
    logger.info(String.format("creating Yuca with period of %d milliseconds", periodMillis));
    return new YucaApplicationMonitor(periodMillis, ProcessHandle.current().pid(), executor);
  }

  public static Path outputPath() {
    return Path.of(
        OUTPUT_PATH,
        String.format("yuca-%d-%d.pb", ProcessHandle.current().pid(), counter.getAndIncrement()));
  }

  public static void summary(Report report) {
    logger.info("Yuca report summary:");
    for (Component component : report.getComponentList()) {
      if (component.getComponentType().equals("linux_process")) {
        for (Signal signal : component.getSignalList()) {
          switch (signal.getUnit()) {
            case GRAMS_OF_CO2:
              logger.info(String.format(" - %.4f grams of CO2", sumSignal(signal, 1)));
              break;
            case JIFFIES:
              logger.info(
                  String.format(
                      " - %.4f%s of cycles",
                      100 * sumSignal(signal, CPU_COUNT) / signal.getIntervalCount(), '%'));
              break;
            case JOULES:
              logger.info(String.format(" - %.4f joules", sumSignal(signal, 1)));
              break;
            default:
              continue;
          }
        }
      }
    }
  }

  public static void writeReports(List<Report> reports) {
    logger.info("writing yuca reports");
    for (Report report : reports) {
      Path outputPath = YucaUtil.outputPath();
      try (OutputStream outputStream = Files.newOutputStream(outputPath)) {
        report.writeTo(outputStream);
        logger.info(String.format("wrote report to %s", outputPath));
      } catch (IOException e) {
        logger.log(Level.WARNING, "unable to write yuca report!", e);
      }
    }
  }

  private static double sumSignal(Signal signal, int factor) {
    return signal.getIntervalList().stream()
        .mapToDouble(
            interval ->
                interval.getDataList().stream().mapToDouble(d -> d.getValue()).sum() / factor)
        .sum();
  }
}
