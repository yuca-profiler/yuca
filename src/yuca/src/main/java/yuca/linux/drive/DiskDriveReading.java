package yuca.linux.drive;

import yuca.linux.drive.spec.PowerMode;
import yuca.linux.drive.spec.DiskModel;

/** A reading from a hdparm energy system. */
public final class DiskDriveReading {
  // TODO: immutable data structures are "safe" as public
  // DiskDriveReading domain
  public final String device;
  // DiskDriveReading domain model name
  public final DiskModel model;
  // DiskDriveReading reading
  public final PowerMode mode;
  //energy value
  public final double watts;

  DiskDriveReading(String device, DiskModel model, PowerMode mode, double watts) {
    this.device = device;
    this.model = model;
    this.mode = mode;
    this.watts = watts;
  }
}
