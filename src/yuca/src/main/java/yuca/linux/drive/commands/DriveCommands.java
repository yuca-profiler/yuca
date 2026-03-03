package yuca.linux.drive.commands;

import static yuca.util.LoggerUtil.getLogger;

import static yuca.util.Timestamps.nowAsInstant;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Map;
import java.util.logging.Logger;
import java.util.stream.Collectors;
import yuca.linux.drive.DiskModel;
import yuca.linux.drive.PowerMode;
import yuca.linux.drive.powermode.PowerModeSample;
import yuca.linux.drive.powermode.PowerModeReading;
import yuca.util.NativeUtils;

/** Simple wrapper around hdparm access that requires libhdparm.so. */
public final class DriveCommands {
  private static final Logger logger = getLogger();

  private static Map<String, DiskModel> DEVICE_MODEL_MAP = mapDeviceToModel();

  /** Maps all found devices to its' model name. Model nameformat is "MODEL_SERIAL" */
  private static Map<String, DiskModel> mapDeviceToModel() {
  return Drives.getDeviceKeys().stream()
      .collect(
          Collectors.toMap(
              dev -> dev,
              dev -> {
                Path modelPath = Drives.SYS_BLOCK.resolve(Paths.get(dev, "device/model"));
                try {
                  String model = Files.readString(modelPath).trim().replace(' ', '_');
                  try {
                    return DiskModel.valueOf(model);
                  } catch (IllegalArgumentException e) {
                    logger.info(
                        String.format(
                            "Drive %s is not defined in yuca.linux.drive.spec.DiskModel, using DEFAULT",
                            model));
                    return DiskModel.DEFAULT;
                  }
                } catch (IOException e) {
                  return DiskModel.DEFAULT;
                }
              }));}
  // map devices to device id, ie: sda -> hdd:0. we can look up  /sys/block/sdX/queue/rotational
  public static PowerMode getMode(String device) {
    return getPowerMode(Paths.get("/dev", device).toString());
  }

  public static DiskModel getModel(String device) {
    return DEVICE_MODEL_MAP.getOrDefault(device, DiskModel.DEFAULT);
  }

  /**
   * Returns an {@link PowerModeSample} populated by parsing the string returned by {@ readNative}.
   */
  public static PowerModeSample samplePowerMode() {
    Instant timestamp = nowAsInstant();
    ArrayList<PowerModeReading> readings = new ArrayList<>();
    for (String device : Drives.getDeviceKeys()) {
      DiskModel model = getModel(device);
      PowerMode mode = getMode(device);
      readings.add(
          new PowerModeReading(
              Drives.deviceIdFor(device), getModel(device), mode));
    }
    return new PowerModeSample(timestamp, readings);
  }

  public static native int powerMode(String device); // returns jint from c

  public static PowerMode getPowerMode(String device) {
    int rawValue = powerMode(device);
    return PowerMode.fromRegister(rawValue);
  }

  static boolean loadLibrary() {
    try {
      NativeUtils.loadLibraryFromJar("/yuca/src/main/c/yuca/drive/libdrivecmds.so");
      return true;
    } catch (Exception e) {
      e.printStackTrace();
      // Fallback to system library
      try {
        System.loadLibrary("drivecmds");
      } catch (UnsatisfiedLinkError err) {
        err.printStackTrace();
      }
    }
    return false;
  }

  static {
    if (!loadLibrary()) {
      logger.warning("native library couldn't be initialized; ioctl likely not available");
    }
  }

  private DriveCommands() {}
}
