package yuca.linux.drive.powermode;

import static java.util.stream.Collectors.toList;
import static yuca.util.Timestamps.betweenAsSecs;
import static yuca.util.Timestamps.fromInstant;
import static yuca.util.Timestamps.nowAsInstant;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import yuca.linux.drive.DiskModel;
import yuca.linux.drive.PowerMode;
import yuca.signal.SignalInterval;
import yuca.signal.SignalInterval.SignalData;

/**
 * A reading of a disk drive's {@link PowerMode} Refer to https://linux.die.net/man/8/hdparm for
 * more details
 */
public final class PowerModeReading {
  // TODO: immutable data structures are "safe" as public
  // PowerModeReading domain
  public final String device;
  // PowerModeReading domain model name
  public final DiskModel model;
  // PowerModeReading reading
  public final PowerMode mode;

  public PowerModeReading(String device, DiskModel model, PowerMode mode) {
    this.device = device;
    this.model = model;
    this.mode = mode;
  }

  /** Computes the difference of two {@link PowerModeSamples}. */
  public static List<SignalData> between(PowerModeSample first, PowerModeSample second) {
    Map<String, PowerModeReading> secondMap =
        second.data().stream().collect(Collectors.toMap(r -> r.device, r -> r));
    ArrayList<SignalData> states = new ArrayList<>();
    double elapsedSeconds =
        betweenAsSecs(fromInstant(first.timestamp()), fromInstant(second.timestamp()));

    for (PowerModeReading reading : first.data()) {
      PowerModeReading later = secondMap.get(reading.device);
      if (later == null) continue;
      double energyJoules = reading.getPower() * elapsedSeconds;

      states.add(
          SignalData.newBuilder()
              .addMetadata(
                  SignalData.Metadata.newBuilder().setName("device").setValue(reading.device))
              .addMetadata(
                  SignalData.Metadata.newBuilder()
                      .setName("model")
                      .setValue(reading.model.toString()))
              .addMetadata(
                  SignalData.Metadata.newBuilder()
                      .setName("mode")
                      .setValue(reading.mode.toString()))
              .setValue(energyJoules)
              .build());
    }
    return states;
  }

  public static SignalInterval difference(PowerModeSample first, PowerModeSample second) {
    return SignalInterval.newBuilder()
        .setStart(fromInstant(first.timestamp()))
        .setEnd(fromInstant(second.timestamp()))
        .addAllData(between(first, second))
        .build();
  }

  public double getPower() {
    return model.getPowerForMode(mode);
  }
}
