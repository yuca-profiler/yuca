package yuca.linux.drive.spec;

public enum PowerMode {
  STANDBY,
  NVCACHE_SPINDOWN,
  NVCACHE_SPINUP,
  IDLE,
  ACTIVE_IDLE,
  UNKNOWN;

  public static PowerMode fromRegister(int reg) {
    switch (reg) {
      case 0x00:
        return STANDBY;
      case 0x40:
        return NVCACHE_SPINDOWN;
      case 0x41:
        return NVCACHE_SPINUP;
      case 0x80:
        return IDLE;
      case 0xff:
        return ACTIVE_IDLE;
      default:
        return UNKNOWN;
    }
  }
}
