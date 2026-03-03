package yuca.linux.drive;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/** A sample of disk energy consumption since boot. */
public final class DiskDriveSample implements Comparable<DiskDriveSample> {
  private final Instant timestamp;
  private final ArrayList<DiskDriveReading> readings = new ArrayList<>();

  DiskDriveSample(Instant timestamp, Iterable<DiskDriveReading> readings) {
    this.timestamp = timestamp;
    readings.forEach(this.readings::add);
  }

  public Instant timestamp() {
    return timestamp;
  }

  public List<DiskDriveReading> data() {
    return new ArrayList<>(readings);
  }

  @Override
  public int compareTo(DiskDriveSample other) {
    return timestamp().compareTo(other.timestamp());
  }
}
