package yuca.linux.thermal;

public enum ThermalZoneKind {
  UNKNOWN_ZONE_KIND,
  PCH_LEWISBERG,
  X86_PKG_TEMP;

  static ThermalZoneKind parseZoneName(String zoneName) {
    switch (zoneName.toUpperCase()) {
      case "PCH_LEWISBERG":
        return ThermalZoneKind.PCH_LEWISBERG;
      case "X86_PKG_TEMP":
        return ThermalZoneKind.X86_PKG_TEMP;
      default:
        return ThermalZoneKind.UNKNOWN_ZONE_KIND;
    }
  }
}
