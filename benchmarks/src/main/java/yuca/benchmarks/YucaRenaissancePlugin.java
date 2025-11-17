package yuca.benchmarks;

import java.util.UUID;
import org.renaissance.Plugin;
import yuca.YucaMonitor;
import yuca.benchmarks.util.YucaUtil;
import yuca.signal.Report;

public final class YucaRenaissancePlugin
    implements Plugin.AfterOperationSetUpListener, Plugin.BeforeOperationTearDownListener {
  private static final UUID INSTANCE_ID = UUID.randomUUID();

  private final YucaMonitor yuca = YucaUtil.createYuca();

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
                              .setName("instance")
                              .setValue(INSTANCE_ID.toString()))
                      .addMetadata(
                          Report.Metadata.newBuilder().setName("suite").setValue("renaissance"))
                      .addMetadata(
                          Report.Metadata.newBuilder().setName("workload").setValue(benchmark))
                      .addMetadata(
                          Report.Metadata.newBuilder()
                              .setName("iteration")
                              .setValue(Integer.toString(opIndex)))
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
