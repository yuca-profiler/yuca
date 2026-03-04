package yuca.linux.drive.commands;

import static yuca.util.LoggerUtil.getLogger;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import static yuca.util.Timestamps.nowAsInstant;
import java.util.ArrayList;
import java.time.Instant;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.logging.Logger;
import java.util.stream.Collectors;
import yuca.linux.drive.DiskModel;
import yuca.linux.drive.PowerMode;
import yuca.linux.drive.powermode.PowerModeReading;
import yuca.linux.drive.powermode.PowerModeSample;

/** A class that exposes drive information from /sys/block. */
public final class Drives {
  private static final Logger logger = getLogger();
  private static final Path SYS_BLOCK = Paths.get("/sys", "block");
  private static Map<String, String> DEVICE_ID_MAP = buildDeviceIds();
  private static Map<String, DiskModel> DEVICE_MODEL_MAP = mapDeviceToModel();

  /** Collects all ATA readable disks on system and builds its' device_id */
  private static Map<String, String> buildDeviceIds() {
    if (!Files.exists(SYS_BLOCK)) {
      logger.warning("couldn't check the device blocks; block sysfs likely not available");
      return Map.of();
    }
    try {
      List<Path> devices =
          Files.list(SYS_BLOCK)
              .filter(p -> !Files.exists(p.resolve("partition")))
              .filter(
                  p -> {
                    Path vendorPath = p.resolve("device/vendor");
                    try {
                      // hdparm is only used to read ATA hard disk drive parameters
                      String vendor = Files.readString(vendorPath).trim();
                      return vendor.equals("ATA");
                    } catch (IOException e) {
                      return false;
                    }
                  })
              .sorted(Comparator.comparing(p -> p.getFileName().toString()))
              .collect(Collectors.toList());

      Map<String, String> deviceIds = new HashMap<>();
      int ssdCount = 0;
      int hddCount = 0;
      for (Path device : devices) {
        Path rotationalPath = device.resolve("queue").resolve("rotational");
        if (!Files.exists(rotationalPath)) {
          continue;
        }
        String rotation = Files.readString(rotationalPath).trim();
        String deviceName = device.getFileName().toString();
        // if rotation is 0, means its a ssd
        if (rotation.equals("0")) {
          deviceIds.put(deviceName, "ssd:" + ssdCount++);
        } else {
          deviceIds.put(deviceName, "hdd:" + hddCount++);
        }
      }
      return deviceIds;
    } catch (Exception e) {
      logger.warning("couldn't check the block devices; block sysfs likely not available");
      return Map.of();
    }
  }

  /** Maps all system found devices to its' model name. Model name format is "MODEL_SERIAL" */
  private static Map<String, DiskModel> mapDeviceToModel() {
    return Drives.getDeviceKeys().stream()
        .collect(
            Collectors.toMap(
                dev -> dev,
                dev -> {
                  Path modelPath = SYS_BLOCK.resolve(Paths.get(dev, "device/model"));
                  try {
                    String model = Files.readString(modelPath).trim().replace(' ', '_');
                    try {
                      return DiskModel.valueOf(model);
                    } catch (IllegalArgumentException e) {
                      logger.info(
                          String.format(
                              "Drive %s is not defined in yuca.linux.drive.spec.DiskModel, using"
                                  + " DEFAULT",
                              model));
                      return DiskModel.DEFAULT;
                    }
                  } catch (IOException e) {
                    return DiskModel.DEFAULT;
                  }
                }));
  }



  public static DiskModel getModel(String device) {
    return DEVICE_MODEL_MAP.getOrDefault(device, DiskModel.DEFAULT);
  }

  public static Set<String> getDeviceKeys() {
    return DEVICE_ID_MAP.keySet();
  }

  public static String deviceIdFor(String device) {
    return DEVICE_ID_MAP.getOrDefault(device, "DEFAULT");
  }

  /** Returns an {@link PowerModeSample} populated by parsing the int returned by {@ powerMode}. */
  public static PowerModeSample samplePowerMode() {
    Instant timestamp = nowAsInstant();
    ArrayList<PowerModeReading> readings = new ArrayList<>();
    for (String device : Drives.getDeviceKeys()) {
      readings.add(
          new PowerModeReading(deviceIdFor(device), getModel(device), DriveCommands.getPowerModeFromRegisterValue(device)));
    }
    return new PowerModeSample(timestamp, readings);
  }
}
