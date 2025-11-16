package yuca.benchmarks;

import org.renaissance.Plugin;
import yuca.YucaMonitor;
import yuca.benchmarks.util.YucaUtil;
import yuca.signal.Report;

public final class YucaRenaissancePlugin
    implements Plugin.AfterOperationSetUpListener, Plugin.BeforeOperationTearDownListener {
  private final YucaMonitor yuca = YucaUtil.createYuca();

  // private final ArrayList<Report> reports = new ArrayList<>();

  @Override
  public void afterOperationSetUp(String benchmark, int opIndex, boolean isLastOp) {
    yuca.start();
  }

  @Override
  public void beforeOperationTearDown(String benchmark, int opIndex, long durationNanos) {
    yuca.stop()
        .ifPresent(
            report -> {
              YucaUtil.summary(report);
              YucaUtil.writeReport(
                  report.toBuilder()
                      .addMetadata(
                          Report.Metadata.newBuilder()
                              .setName("iteration")
                              .setValue(Integer.toString(opIndex)))
                      .addMetadata(
                          Report.Metadata.newBuilder().setName("suite").setValue("renaissance"))
                      .addMetadata(
                          Report.Metadata.newBuilder().setName("workload").setValue(benchmark))
                      .build());
            });
  }

  // @Override
  // public void beforeBenchmarkTearDown(String benchmark) {
  //   YucaUtil.writeReports(reports);
  //   reports.clear();
  // }
}
