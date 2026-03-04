package yuca.linux.drive.commands;

import static yuca.util.LoggerUtil.getLogger;

import java.nio.file.Paths;
import java.util.logging.Logger;
import yuca.linux.drive.PowerMode;
import yuca.util.NativeUtils;

/** Simple wrapper around Linux block device access that requires libhdparm.so. */
public final class DriveCommands {
  private static final Logger logger = getLogger();

  /** Returns the current disk drive powermode as a jint from c */
  private static native int powerMode(String devicePath);

  private static int getRawPowerMode(String devicePath) {
    return powerMode(devicePath);
  }

  /** Returns the current disk drive {@ PowerMode} */
  public static PowerMode getPowerModeFromRegisterValue(String device) {
    String devicePath = Paths.get("/dev", device).toString();
    return PowerMode.fromRegister(getRawPowerMode(devicePath));
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
