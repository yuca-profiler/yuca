package yuca.hdparm;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/** A sample of hdparm energy consumption since boot. */
public final class HdparmSample implements Comparable<HdparmSample> {
  private final Instant timestamp;
  private final ArrayList<HdparmReading> readings = new ArrayList<>();

  HdparmSample(Instant timestamp, Iterable<HdparmReading> readings) {
    this.timestamp = timestamp;
    readings.forEach(this.readings::add);
  }

  public Instant timestamp() {
    return timestamp;
  }

  public List<HdparmReading> data() {
    return new ArrayList<>(readings);
  }

  @Override
  public int compareTo(HdparmSample other) {
    return timestamp().compareTo(other.timestamp());
  }
}
