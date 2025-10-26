package yuca.benchmarks;

import org.dacapo.harness.Callback;
import org.dacapo.harness.CommandLineArgs;
import yuca.YucaMonitor;
import yuca.benchmarks.util.YucaUtil;
import yuca.signal.Report;

public class YucaDacapoCallback extends Callback {
  private final YucaMonitor yuca = YucaUtil.createYuca();
  // private final ArrayList<Report> reports = new ArrayList<>();

  private int iteration = 0;

  public YucaDacapoCallback(CommandLineArgs args) {
    super(args);
  }

  @Override
  public void start(String benchmark) {
    yuca.start();
    super.start(benchmark);
  }

  @Override
  public void complete(String benchmark, boolean valid, boolean warmup) {
    super.complete(benchmark, valid, warmup);
    yuca.stop()
        .ifPresent(
            report -> {
              YucaUtil.summary(report);
              YucaUtil.writeReport(
                  report.toBuilder()
                      .addMetadata(
                          Report.Metadata.newBuilder()
                              .setName("iteration")
                              .setValue(Integer.toString(iteration++)))
                      .addMetadata(Report.Metadata.newBuilder().setName("suite").setValue("dacapo"))
                      .addMetadata(
                          Report.Metadata.newBuilder().setName("workload").setValue(benchmark))
                      .build());
            });
  }

  // @Override
  // public boolean runAgain() {
  //   // if we have run every iteration, dump the data and terminate
  //   if (!super.runAgain()) {
  //     YucaUtil.writeReports(reports);
  //     reports.clear();
  //     return false;
  //   } else {
  //     return true;
  //   }
  // }
}
