package yuca.hdparm;

import static java.util.stream.Collectors.toList;
import static yuca.util.LoggerUtil.getLogger;
import static yuca.util.Timestamps.fromInstant;
import static yuca.util.Timestamps.nowAsInstant;
import static yuca.util.Timestamps.betweenAsSecs;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.Map;
import java.util.Comparator;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.logging.Logger;
import java.util.stream.Collectors;
import yuca.signal.SignalInterval;
import yuca.signal.SignalInterval.SignalData;

import yuca.util.NativeUtils;
import yuca.hdparm.PowerMode;


/** Simple wrapper around hdparm access that requires libhdparm.so. */
public final class Hdparm {
    private static final Logger logger = getLogger();
    static final Path SYS_BLOCK = Paths.get("/sys", "block");
    private static Map<String, String> DEVICE_ID_MAP = buildDeviceIds();
    private static Map<String, String> DEVICE_MODEL_MAP = mapDeviceToModel();

    /** Collects all ATA readable disks on system and builds its' device_id */
    public static Map<String, String> buildDeviceIds(){
        if(!Files.exists(SYS_BLOCK)){
            logger.warning("couldn't check the device blocks; block sysfs likely not available");
            return Map.of();
        }
        try{
            List<Path> devices =  Files.list(SYS_BLOCK)
                .filter(p -> !Files.exists(p.resolve("partition")))
                .filter(p -> {
                    Path vendorPath = p.resolve("device/vendor");
                    try {
                        // hdparm is only used to read ATA hard disk drive parameters
                        String vendor = Files.readString(vendorPath).trim();
                        return vendor.equals("ATA");
                    }
                    catch (IOException e) {
                        return false;
                    }
                })
                .sorted(Comparator.comparing(p -> p.getFileName().toString()))
                .collect(Collectors.toList());

            Map<String, String> deviceIds = new HashMap<>();
            int ssdCount = 0;
            int hddCount = 0;
            for(Path device: devices){
                Path rotationalPath = device.resolve("queue").resolve("rotational");
                if (!Files.exists(rotationalPath)){
                    continue;
                }
                String rotation = Files.readString(rotationalPath).trim();
                String deviceName = device.getFileName().toString();
                // if rotation is 0, means its a ssd
                if(rotation.equals("0")){
                    deviceIds.put(deviceName, "ssd:" + ssdCount++);
                }
                else{
                    deviceIds.put(deviceName, "hdd:" + hddCount++);
                }
            }
            return deviceIds;
        } catch (Exception e) {
            logger.warning("couldn't check the block devices; block sysfs likely not available");
            return Map.of();
        }
    }

    /** Maps all found devices to its' model name. Model nameformat is "MODEL_SERIAL" */
    public static Map<String, String> mapDeviceToModel(){
        return DEVICE_ID_MAP.keySet().stream()
            .collect(Collectors.toMap(
                dev -> dev,
                dev -> {
                    Path modelPath = SYS_BLOCK.resolve(Paths.get(dev, "device/model"));
                    try {
                        return Files.readString(modelPath).trim().replace(' ', '_');
                    } catch (IOException e) {
                        return "DEFAULT";
                    }
                }
            ));
    }

    //map devices to device id, ie: sda -> hdd:0. we can look up  /sys/block/sdX/queue/rotational
    public static double getPower(String device){
        return readTable(getModel(device), getMode(device));
    }
    public static EnumMap<PowerMode, Double> getTable(String model){
        return DrivePowerRegistry.DEVICES_MP.getOrDefault(model, DrivePowerRegistry.DEVICES_MP.get("DEFAULT"));
    }
    public static PowerMode getMode(String device){
        return getPowerMode(Paths.get("/dev", device).toString());
    }
    public static String getModel(String device){
        return DEVICE_MODEL_MAP.getOrDefault(device, "DEFAULT");
    }
    public static double readTable(String model, PowerMode mode){
        return getTable(model).get(mode);
    }

    /** Returns an {@link HdparmSample} populated by parsing the string returned by {@ readNative}. */
    public static HdparmSample sample() {
        Instant timestamp = nowAsInstant();
        ArrayList<HdparmReading> readings = new ArrayList<>();
        for(String device : DEVICE_ID_MAP.keySet()){
            readings.add(new HdparmReading(DEVICE_ID_MAP.get(device), getModel(device), getMode(device), getPower(device)));
        }
        return new HdparmSample(timestamp, readings);
    }

    /** Computes the difference of two {@link HdparmSamples}. Passes in HdparmSample for timestamps */
    public static List<SignalData> between(HdparmSample first, HdparmSample second) {
        Map<String, HdparmReading> secondMap = second.data().stream()
        .collect(Collectors.toMap(r -> r.device, r -> r));
        ArrayList<SignalData> states = new ArrayList<>();
        double elapsedSeconds = betweenAsSecs(fromInstant(first.timestamp()), fromInstant(second.timestamp()));

        for(HdparmReading reading : first.data()){
            HdparmReading later = secondMap.get(reading.device);
            if (later == null) continue;
            double energyJoules = reading.watts * elapsedSeconds;

            states.add(
                SignalData.newBuilder()
                .addMetadata(
                    SignalData.Metadata.newBuilder()
                        .setName("device")
                        .setValue(reading.device))
                .addMetadata(
                        SignalData.Metadata.newBuilder().setName("model").setValue(reading.model))
                .setValue(energyJoules)
                .build());
        }
        return states;
    }

    public static SignalInterval difference(HdparmSample first, HdparmSample second) {
        return SignalInterval.newBuilder()
            .setStart(fromInstant(first.timestamp()))
            .setEnd(fromInstant(second.timestamp()))
            .addAllData(between(first, second))
            .build();
    }
    public static native int powerMode(String device); //returns jint from c

    public static PowerMode getPowerMode(String device) {
        int rawValue = powerMode(device);
        return PowerMode.fromRegister(rawValue);
    }
    static boolean loadLibrary(){
        try {
            NativeUtils.loadLibraryFromJar("/yuca/src/main/c/yuca/hdparm/libhdparm.so");
            return true;
        } catch (Exception e) {
            e.printStackTrace();
            // Fallback to system library
            try {
                System.loadLibrary("hdparm");
            } catch (UnsatisfiedLinkError err) {
                err.printStackTrace();
            }
        }
        return false;
    }

    static {
        if (!loadLibrary()) {
            logger.warning("native library couldn't be initialized; hdparm likely not available");
        }
    }

    private Hdparm() {}
}