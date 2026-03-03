package yuca.linux.drive.commands;

import static yuca.util.LoggerUtil.getLogger;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.logging.Logger;
import java.util.stream.Collectors;

/** A class that exposes drive information from /sys/block. */
public final class Drives {
  private static final Logger logger = getLogger();
  static final Path SYS_BLOCK = Paths.get("/sys", "block");
  private static Map<String, String> DEVICE_ID_MAP = buildDeviceIds();

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

  public static Set<String> getDeviceKeys() {
    return DEVICE_ID_MAP.keySet();
  }

  public static String deviceIdFor(String device) {
    return DEVICE_ID_MAP.getOrDefault(device, "DEFAULT");
  }
}
