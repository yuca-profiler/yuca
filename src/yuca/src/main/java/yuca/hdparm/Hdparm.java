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
import java.util.ArrayList;
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
    private static final Path SYS_BLOCK = Paths.get("/sys", "class", "block");
    private static final List<String> DEVICES = findBlockDevices();
    private static Map<String, String> DEVICE_PATH_TO_MODEL = mapDeviceToModel();

    //create a list of string of avaible devices
    public static List<String> findBlockDevices(){
        if(!Files.exists(SYS_BLOCK)){
            logger.warning("couldn't check the device blocks; block sysfs likely not available");
            return List.of();
        }
        try{
            return Files.list(SYS_BLOCK)
                .filter(p -> !Files.exists(p.resolve("partition")))
                .map(p -> Paths.get("/dev", (p.getFileName()).toString()).toString())
                .collect(Collectors.toList());
        } catch (Exception e) {
            logger.warning("couldn't check the block devices; block sysfs likely not available");
            return List.of();
        }
    }
    
    // map devices to its model name
    public static Map<String, String> mapDeviceToModel(){
        // /sys/class/block/sda/device/model 
        return DEVICES.stream()
            .collect(Collectors.toMap(
                dev -> dev,
                dev -> {
                    Path modelPath = Paths.get("/sys/block", dev.substring(5), "device/model");
                    try {
                        return Files.readString(modelPath).trim().replace(' ', '_');
                    } catch (IOException e) {
                        // System.out.println("bad map " + dev);
                        return "unknown";
                    }
                }
            ));
    }

    /** Returns an {@link HdparmSample} populated by parsing the string returned by {@ readNative}. */
    public static HdparmSample sample() {
        // if (COMPONENTS.isEmpty()) {
        // logger.warning("no components founds; hdparm likely not available");
        // return Optional.empty();
        // }
        Instant timestamp = nowAsInstant();
        ArrayList<HdparmReading> readings = new ArrayList<>();
        for(String device : DEVICES){
            String model = DEVICE_PATH_TO_MODEL.getOrDefault(device, "unknown");
            PowerMode mode = getPowerMode(device);
            double watts = DrivePowerRegistry.DEVICES_MP.get(model).get(mode);

            readings.add(new HdparmReading(device, model, mode, watts));
        }
        return new HdparmSample(timestamp, readings);
    }

    /** Computes the difference of two {@link PowercapReadings}. */
    public static List<SignalData> between(HdparmSample first, HdparmSample second) {
        // if (first.device != second.device) {
        //     throw new IllegalArgumentException(
        //         String.format(
        //             "readings are not from the same domain (%d != %d)", first.device, second.device));
        // }
        ArrayList<SignalData> states = new ArrayList<>();
        double elapsedSeconds = betweenAsSecs(fromInstant(first.timestamp()), fromInstant(second.timestamp()));

        Map<String, HdparmReading> secondMap = second.data().stream()
        .collect(Collectors.toMap(r -> r.device, r -> r));

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

    static {
        try {
            NativeUtils.loadLibraryFromJar("/yuca/src/main/c/yuca/hdparm/libhdparm.so");
        } catch (Exception e) {
            e.printStackTrace();
            // Fallback to system library
            try {
                System.loadLibrary("hdparm");
            } catch (UnsatisfiedLinkError err) {
                err.printStackTrace();
            }
        }
    }
    
    public static void main(String[] args) {
        System.out.println("Testing hdparm JNI wrapper...");
        try {
            PowerMode test = getPowerMode("/dev/sda");
            System.out.println(test);
            for (String d: DEVICES){
                System.out.println(d);
            }
            HdparmSample sample = Hdparm.sample();
            List<HdparmReading> readings = sample.data();
            for(HdparmReading r: readings){
                System.out.println(r.device + ' ' + r.model + ' ' + r.mode + ' ' + r.watts); 
            }
        } catch (UnsatisfiedLinkError e) {
            System.err.println("Failed to call native method: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private Hdparm() {}
}