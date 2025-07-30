package yuca.benchmarks;

import java.util.ArrayList;
import org.renaissance.Plugin;
import yuca.YucaMonitor;
import yuca.benchmarks.util.YucaUtil;
import yuca.signal.Report;

public final class YucaRenaissancePlugin
    implements Plugin.BeforeBenchmarkTearDownListener,
        Plugin.AfterOperationSetUpListener,
        Plugin.BeforeOperationTearDownListener {
  private final YucaMonitor yuca = YucaUtil.createYuca();
  private final ArrayList<Report> reports = new ArrayList<>();

  @Override
  public void afterOperationSetUp(String benchmark, int opIndex, boolean isLastOp) {
    yuca.start();
  }

  @Override
  public void beforeOperationTearDown(String benchmark, int opIndex, long durationNanos) {
    yuca.stop().ifPresent(reports::add);
    YucaUtil.summary(reports.get(reports.size() - 1));
  }

  @Override
  public void beforeBenchmarkTearDown(String benchmark) {
    YucaUtil.writeReports(reports);
    reports.clear();
  }
}
