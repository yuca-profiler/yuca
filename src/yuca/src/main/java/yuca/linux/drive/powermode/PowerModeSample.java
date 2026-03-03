package yuca.linux.drive.powermode;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/**
 * A sample from disk drive's internal registers that represents the current Linux block device
 * powermode
 */
public final class PowerModeSample implements Comparable<PowerModeSample> {
  private final Instant timestamp;
  private final ArrayList<PowerModeReading> readings = new ArrayList<>();

  public PowerModeSample(Instant timestamp, Iterable<PowerModeReading> readings) {
    this.timestamp = timestamp;
    readings.forEach(this.readings::add);
  }

  public Instant timestamp() {
    return timestamp;
  }

  public List<PowerModeReading> data() {
    return new ArrayList<>(readings);
  }

  @Override
  public int compareTo(PowerModeSample other) {
    return timestamp().compareTo(other.timestamp());
  }
}
