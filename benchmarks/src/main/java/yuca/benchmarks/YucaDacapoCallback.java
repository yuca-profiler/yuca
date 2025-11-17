package yuca.benchmarks;

import java.util.UUID;
import org.dacapo.harness.Callback;
import org.dacapo.harness.CommandLineArgs;
import yuca.YucaMonitor;
import yuca.benchmarks.util.YucaUtil;
import yuca.signal.Report;

public class YucaDacapoCallback extends Callback {
  private static final UUID INSTANCE_ID = UUID.randomUUID();

  private final YucaMonitor yuca = YucaUtil.createYuca();

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
                              .setName("instance")
                              .setValue(INSTANCE_ID.toString()))
                      .addMetadata(Report.Metadata.newBuilder().setName("suite").setValue("dacapo"))
                      .addMetadata(
                          Report.Metadata.newBuilder().setName("workload").setValue(benchmark))
                      .addMetadata(
                          Report.Metadata.newBuilder()
                              .setName("iteration")
                              .setValue(Integer.toString(iteration++)))
                      .addMetadata(
                          Report.Metadata.newBuilder()
                              .setName("profiler")
                              .setValue(yuca.getClass().getSimpleName()))
                      .addMetadata(
                          Report.Metadata.newBuilder()
                              .setName("period")
                              .setValue(Integer.toString(YucaUtil.getPeriod())))
                      .build());
            });
  }
}
