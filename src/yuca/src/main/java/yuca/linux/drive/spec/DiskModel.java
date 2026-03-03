package yuca.linux.drive.spec;

import java.util.Map;
import java.util.EnumMap;

public enum DiskModel {
    DEFAULT(0, 0, 0, 0, 0),
    TOSHIBA_HDWE140(0.67, 7.22, 18.75, 7.22, 8.35),
    TOSHIBA_HDWR160(0.67, 7.22, 18.75, 7.22, 8.35);
    
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