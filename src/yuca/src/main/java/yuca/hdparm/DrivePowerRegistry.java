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
import yuca.hdparm.DrivePowerTable;

// each device needs to map to a DrivePowerTable
public final class DrivePowerRegistry {
    private static final Logger logger = getLogger();
    private static final String DEFAULT_SPECS_FILE = "/disks/DiskSpecs.csv";
    private static final Path SYS_BLOCK = Paths.get("/sys", "block");

    // public final Map<String, DrivePowerTable> DEVICES_MP = new HashMap<>();;
    public static final Map<String, EnumMap<PowerMode, Double>> DEVICES_MP = getPowerDraw();

    // public DrivePowerTable get(String device){
    //     return DEVICES_MP.get(device);
    // }

    // public void register(String device, DrivePowerTable table){
    //     DEVICES_MP.put(device, table);
    // }

    //create a list of string of available devices by name
    public static List<String> findDevicesModelName(){
        if(!Files.exists(SYS_BLOCK)){
            logger.warning("couldn't check the device blocks; block sysfs likely not available");
            return List.of();
        }
        try (Stream<Path> paths = Files.list(SYS_BLOCK)) {
            return paths
                .filter(p -> !Files.exists(p.resolve("partition")))
                .map(p -> {
                    try {
                        return Files.readString(
                            p.resolve("device").resolve("model")
                        ).trim().replace(' ', '_');
                    } catch(IOException e){
                        return "DEFAULT";
                    }
                })
                .collect(Collectors.toList());
        } catch (Exception e) {
            logger.warning("couldn't check the block devices; block sysfs likely not available");
            return List.of();
        }
    }
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
    private static Map<String, EnumMap<PowerMode, Double>> getPowerDraw() {
        // Path path = Path.of("src/yuca/src/main/resources/disks/DiskSpecs.csv");
        // System.out.println("hello");
        // System.out.println(path);
        // if (!Files.exists(path)) {
        //     logger.info(String.format("device specs file %s could not be found", path));
        //     return Map.of();
        //     // return getDefaultIntensities();
        // }
        try {
            // return parseCsv(Files.readAllLines(path));
            return parseCsv(NativeUtils.readFileContentsFromJar(DEFAULT_SPECS_FILE));
        } catch (IOException e) {
            throw new IllegalStateException("Unable to read the default specs file.", e);
            // throw new IllegalStateException(String.format("Unable to read %s", path), e);
        }
    }

    public static void main (String[] args){
        List<String> arr = findDevicesModelName();
        arr.forEach(System.out::println);
        try{
            Map<String, EnumMap<PowerMode, Double>> mp = parseCsv(NativeUtils.readFileContentsFromJar(DEFAULT_SPECS_FILE));
            for (String s: mp.keySet()){
                System.out.println(s);
                EnumMap<PowerMode, Double> t = mp.get(s);
                for (PowerMode d: t.keySet()){
                    System.out.println("the thing is: " + d + t.get(d));
                }
            }
        }
        catch (IOException e) {
            logger.warning("couldn't check the block devices; block sysfs likely not available");
            // return List.of();
        }
       
    }

}