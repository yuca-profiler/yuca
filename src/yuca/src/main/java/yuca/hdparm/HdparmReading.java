package yuca.hdparm;

/** A reading from a hdparm energy system. */
public final class HdparmReading {
  // TODO: immutable data structures are "safe" as public
  // powermode domain
  public final String device;
  // powermode reading
  public final PowerMode mode;

  HdparmReading(String device, PowerMode mode) {
    this.device = device;
    this.mode = mode;
  }
}
