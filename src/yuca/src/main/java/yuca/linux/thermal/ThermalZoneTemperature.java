package yuca.linux.thermal;

/** A reading from a thermal sysfs system. */
public final class ThermalZoneTemperature {
  // TODO: immutable data structures are "safe" as public
  public final int zone;
  public final ThermalZoneKind kind;
  public final int temperature;

  ThermalZoneTemperature(int zone, ThermalZoneKind kind, int temperature) {
    this.zone = zone;
    this.kind = kind;
    this.temperature = temperature;
  }
}
