package yuca.linux.drive;

import java.util.EnumMap;

public enum DiskModel {
  DEFAULT(0, 0, 0, 0, 0),
  TOSHIBA_HDWE140(0.67, 7.22, 18.75, 7.22, 8.35),
  TOSHIBA_HDWR160(0.67, 7.22, 18.75, 7.22, 8.35),
  // (480GB) active read 2.9W, active write 2.3W, idle 1.3W, activeIdle = 2.9+1.3/2 = 2.1
  SAMSUNG_SSD_883_DCT(0.5, 0, 0, 1.3, 2.1);

  private final EnumMap<PowerMode, Double> power;

  DiskModel(double standby, double spindown, double spinup, double idle, double activeIdle) {
    this.power = new EnumMap<>(PowerMode.class);
    power.put(PowerMode.STANDBY, standby);
    power.put(PowerMode.NVCACHE_SPINDOWN, spindown);
    power.put(PowerMode.NVCACHE_SPINUP, spinup);
    power.put(PowerMode.IDLE, idle);
    power.put(PowerMode.ACTIVE_IDLE, activeIdle);
  }

  public double getPowerForMode(PowerMode mode) {
    return power.getOrDefault(mode, 0.0);
  }
}
