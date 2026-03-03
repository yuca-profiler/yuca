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
import yuca.linux.drive.powermode.PowerModeReading;
import yuca.linux.drive.powermode.PowerModeSample;
import yuca.util.NativeUtils;

/** Simple wrapper around Linux block device access that requires libhdparm.so. */
public final class DriveCommands {
  private static final Logger logger = getLogger();

  private static Map<String, DiskModel> DEVICE_MODEL_MAP = mapDeviceToModel();

  /** Maps all system found devices to its' model name. Model name format is "MODEL_SERIAL" */
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

  public static PowerMode getMode(String device) {
    return getPowerMode(Paths.get("/dev", device).toString());
  }

  public static DiskModel getModel(String device) {
    return DEVICE_MODEL_MAP.getOrDefault(device, DiskModel.DEFAULT);
  }

  /** Returns an {@link PowerModeSample} populated by parsing the int returned by {@ powerMode}. */
  public static PowerModeSample samplePowerMode() {
    Instant timestamp = nowAsInstant();
    ArrayList<PowerModeReading> readings = new ArrayList<>();
    for (String device : Drives.getDeviceKeys()) {
      readings.add(
          new PowerModeReading(Drives.deviceIdFor(device), getModel(device), getMode(device)));
    }
    return new PowerModeSample(timestamp, readings);
  }

  /** Returns the current disk drive powermode as a jint from c */
  public static native int powerMode(String device);

  /** Parses the raw register value of {@ powerMode} to a {@ PowerMode} */
  public static PowerMode getPowerMode(String device) {
    int rawValue = powerMode(device);
    return PowerMode.fromRegister(rawValue);
  }

  /** Makes a safe attempt to load the library. */
  static boolean loadLibrary() {
    try {
      // TODO: Figure out how shorten this path
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
