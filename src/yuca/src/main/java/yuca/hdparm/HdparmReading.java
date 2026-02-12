package yuca.hdparm;

/** A reading from a hdparm energy system. */
public final class HdparmReading {
  // TODO: immutable data structures are "safe" as public
  // powermode domain
  public final String device;
  // powermode domain model name
  public final String model;
  // powermode reading
  public final PowerMode mode;
  //energy value
  public final double watts;

  HdparmReading(String device, String model, PowerMode mode, double watts) {
    this.device = device;
    this.model = model;
    this.mode = mode;
    this.watts = watts;
  }
}
