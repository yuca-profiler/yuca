package yuca.linux.powercap;

import static java.util.stream.Collectors.toList;
import static yuca.util.LoggerUtil.getLogger;
import static yuca.util.Timestamps.fromInstant;
import static yuca.util.Timestamps.nowAsInstant;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.logging.Logger;
import java.util.stream.IntStream;
import yuca.signal.SignalInterval;
import yuca.signal.SignalInterval.SignalData;

/** Simple wrapper to read powercap's energy with pure Java. */
// TODO: this doesn't appear to work on more modern implementations that are hierarchical
public final class Powercap {
  private static final Logger logger = getLogger();

  private static final Path POWERCAP_ROOT =
      Paths.get("/sys", "devices", "virtual", "powercap", "intel-rapl");

  public static final int SOCKETS = getSocketCount();
  public static final double[][] MAX_ENERGY_JOULES = getMaximumEnergy();

  /** Returns whether we can read values. */
  public static boolean isAvailable() {
    return SOCKETS > 0;
  }

  /**
   * Returns an {@link PowercapSample} populated by parsing the string returned by {@ readNative}.
   */
  public static Optional<PowercapSample> sample() {
    if (!isAvailable()) {
      return Optional.empty();
    }

    Instant timestamp = nowAsInstant();
    ArrayList<PowercapReading> readings = new ArrayList<>();
    for (int socket = 0; socket < SOCKETS; socket++) {
      readings.add(new PowercapReading(socket, readPackage(socket), readDram(socket), 0.0, 0.0));
    }

    return Optional.of(new PowercapSample(timestamp, readings));
  }

  /** Computes the difference of two {@link PowercapReadings}. */
  public static List<SignalData> between(PowercapReading first, PowercapReading second) {
    if (first.socket != second.socket) {
      throw new IllegalArgumentException(
          String.format(
              "readings are not from the same domain (%d != %d)", first.socket, second.socket));
    }
    return List.of(
        SignalData.newBuilder()
            .addMetadata(
                SignalData.Metadata.newBuilder()
                    .setName("socket")
                    .setValue(Integer.toString(first.socket)))
            .addMetadata(SignalData.Metadata.newBuilder().setName("component").setValue("package"))
            .setValue(diffWithWraparound(first.pkg, second.pkg, first.socket, 0))
            .build(),
        SignalData.newBuilder()
            .addMetadata(
                SignalData.Metadata.newBuilder()
                    .setName("socket")
                    .setValue(Integer.toString(first.socket)))
            .addMetadata(SignalData.Metadata.newBuilder().setName("component").setValue("dram"))
            .setValue(diffWithWraparound(first.dram, second.dram, first.socket, 1))
            .build());
  }

  /** Computes the difference of two {@link PowercapReadings}, applying the wraparound. */
  public static SignalInterval difference(PowercapSample first, PowercapSample second) {
    if (first.compareTo(second) > -1) {
      throw new IllegalArgumentException(
          String.format(
              "first sample is not before second sample (%s !< %s)",
              first.timestamp(), second.timestamp()));
    }
    List<PowercapReading> firstData = first.data();
    List<PowercapReading> secondData = second.data();
    return SignalInterval.newBuilder()
        .setStart(fromInstant(first.timestamp()))
        .setEnd(fromInstant(second.timestamp()))
        .addAllData(
            IntStream.range(0, SOCKETS)
                .mapToObj(i -> Integer.valueOf(i))
                .flatMap(socket -> between(firstData.get(socket), secondData.get(socket)).stream())
                .collect(toList()))
        .build();
  }

  private static double diffWithWraparound(double first, double second, int socket, int component) {
    double energy = second - first;
    if (energy < 0) {
      logger.info(String.format("powercap overflow on %d:%d", socket, component));
      energy += MAX_ENERGY_JOULES[socket][component];
    }
    return energy;
  }

  private static int getSocketCount() {
    if (!Files.exists(POWERCAP_ROOT)) {
      logger.warning("couldn't check the socket count; powercap likely not available");
      return 0;
    }
    try {
      return (int)
          Files.list(POWERCAP_ROOT)
              .filter(p -> p.getFileName().toString().contains("intel-rapl"))
              .count();
    } catch (Exception e) {
      logger.warning("couldn't check the socket count; powercap likely not available");
      return 0;
    }
  }

  private static double[][] getMaximumEnergy() {
    if (!Files.exists(POWERCAP_ROOT)) {
      logger.warning("couldn't check the maximum energy; powercap likely not available");
      return new double[0][0];
    }
    // TODO: this is a hack and we need to formalize it
    try {
      double[][] maxEnergy =
          Files.list(POWERCAP_ROOT)
              .filter(p -> p.getFileName().toString().contains("intel-rapl"))
              .map(
                  socket -> {
                    double[] overflowValues = new double[2];
                    try {
                      overflowValues[0] =
                          Double.parseDouble(
                                  Files.readString(
                                      Path.of(socket.toString(), "max_energy_range_uj")))
                              / 1000000;
                    } catch (Exception e) {
                      logger.warning(
                          String.format("couldn't check the maximum energy for socket %s", socket));
                    }
                    try {
                      overflowValues[1] =
                          Double.parseDouble(
                                  Files.readString(
                                      Path.of(
                                          socket.toString(),
                                          String.format("%s:0", socket.getFileName()),
                                          "max_energy_range_uj")))
                              / 1000000;
                    } catch (Exception e) {
                      logger.warning(
                          String.format("couldn't check the maximum energy for socket %s", socket));
                    }
                    logger.info(
                        String.format(
                            "retrieved overflow values for %s: %s",
                            socket.getFileName(), Arrays.toString(overflowValues)));
                    return overflowValues;
                  })
              .toArray(double[][]::new);
      return maxEnergy;
    } catch (Exception e) {
      logger.warning("couldn't check the maximum energy; powercap likely not available");
      return new double[0][0];
    }
  }

  /**
   * Parses the contents of /sys/devices/virtual/powercap/intel-rapl/intel-rapl:<socket>/energy_uj,
   * which contains the number of microjoules consumed by the package since boot as an integer.
   */
  private static double readPackage(int socket) {
    String socketPrefix = String.format("intel-rapl:%d", socket);
    Path energyFile = Paths.get(POWERCAP_ROOT.toString(), socketPrefix, "energy_uj");
    try {
      return Double.parseDouble(Files.readString(energyFile)) / 1000000;
    } catch (Exception e) {
      return 0;
    }
  }

  /**
   * Parses the contents of
   * /sys/devices/virtual/powercap/intel-rapl/intel-rapl:<socket>/intel-rapl:<socket>:0/energy_uj,
   * which contains the number of microjoules consumed by the dram since boot as an integer.
   */
  private static double readDram(int socket) {
    String socketPrefix = String.format("intel-rapl:%d", socket);
    Path energyFile =
        Paths.get(
            POWERCAP_ROOT.toString(),
            socketPrefix,
            String.format("%s:0", socketPrefix),
            "energy_uj");
    try {
      return Double.parseDouble(Files.readString(energyFile)) / 1000000;
    } catch (Exception e) {
      return 0;
    }
  }
}
