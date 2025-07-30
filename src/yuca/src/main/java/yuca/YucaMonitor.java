package yuca;

import java.util.Optional;
import yuca.signal.Report;
import yuca.signal.Signal;

/** A class to collect and provide yuca signals. */
public interface YucaMonitor {
  /** Starts monitoring. */
  void start();

  /** Stops monitoring and maybe return a report if there was any data. */
  Optional<Report> stop();

  Signal convertToEmissions(Signal signal);
}
