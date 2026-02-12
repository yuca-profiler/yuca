package yuca.hdparm;

import java.util.EnumMap;

// device to powermode
public final class DrivePowerTable {

    private final EnumMap<PowerMode, Double> POWER_DRAW_MAP; 

    public DrivePowerTable(EnumMap<PowerMode, Double> power_draw_map) {
        this.POWER_DRAW_MAP = power_draw_map;
    }

    public double wattsFor(PowerMode mode) {
        return POWER_DRAW_MAP.getOrDefault(mode, 0.0);
    }
}