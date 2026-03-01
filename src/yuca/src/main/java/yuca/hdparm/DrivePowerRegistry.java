package yuca.hdparm;

import static java.util.stream.Collectors.toList;
import static yuca.util.LoggerUtil.getLogger;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.stream.Stream;

import java.util.Map;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import yuca.util.NativeUtils;
import java.util.logging.Logger;
import java.util.stream.Collectors;

import yuca.hdparm.PowerMode;

/** A class that creates a power draw intensity map from disk models. */
public final class DrivePowerRegistry {
    private static final Logger logger = getLogger();
    private static final String DEFAULT_SPECS_FILE = "/disks/DiskSpecs.csv";

    public static final Map<String, EnumMap<PowerMode, Double>> DEVICES_MP = getPowerDraw();

    /** Parses a csv like "MODEL,standby,NVcache_spindown,NVcache_spinup,idle,active_idle" */
    private static Map<String, EnumMap<PowerMode, Double>> parseCsv(List<String> lines){
        String[] header = lines.get(0).split(",");
        return lines.stream()
            .skip(1)
            .map(line -> line.split(","))
            .collect(Collectors.toMap(
                p -> p[0],
                p -> {
                    EnumMap<PowerMode, Double> mp = new EnumMap<>(PowerMode.class);
                    for(int i = 1; i < p.length; i++){
                        PowerMode mode = PowerMode.valueOf(header[i].toUpperCase());
                        mp.put(mode, Double.parseDouble(p[i]));
                    }
                    return mp;
                }
            ));
    }

    /** TODO: Add a custom specs file users can edit */
    private static Map<String, EnumMap<PowerMode, Double>> getPowerDraw() {
        try {
            return parseCsv(NativeUtils.readFileContentsFromJar(DEFAULT_SPECS_FILE));
        } catch (IOException e) {
            throw new IllegalStateException("Unable to read the default specs file.", e);
        }
    }

}