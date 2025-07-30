package yuca.benchmarks;

import java.util.ArrayList;
import org.dacapo.harness.Callback;
import org.dacapo.harness.CommandLineArgs;
import yuca.YucaMonitor;
import yuca.benchmarks.util.YucaUtil;
import yuca.signal.Report;

public class YucaDacapoCallback extends Callback {
  private final YucaMonitor yuca = YucaUtil.createYuca();
  private final ArrayList<Report> reports = new ArrayList<>();

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
    yuca.stop().ifPresent(reports::add);
    YucaUtil.summary(reports.get(reports.size() - 1));
  }

  @Override
  public boolean runAgain() {
    // if we have run every iteration, dump the data and terminate
    if (!super.runAgain()) {
      YucaUtil.writeReports(reports);
      reports.clear();
      return false;
    } else {
      return true;
    }
  }
}
