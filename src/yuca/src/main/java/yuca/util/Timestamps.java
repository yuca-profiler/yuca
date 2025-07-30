package yuca.util;

import java.time.Duration;
import java.time.Instant;
import yuca.signal.SignalInterval.Timestamp;

/** Utilities for algebra with {@link Instants} and {@link Durations}. */
public final class Timestamps {
  /** Returns the maximum (i.e. furthest in the future) {@link Instant}. */
  public static Instant toInstant(Timestamp timestamp) {
    return Instant.ofEpochSecond(timestamp.getSecs(), timestamp.getNanos());
  }

  /** Returns the maximum (i.e. furthest in the future) {@link Instant}. */
  public static Timestamp fromInstant(Instant timestamp) {
    return Timestamp.newBuilder()
        .setSecs(timestamp.getEpochSecond())
        .setNanos(timestamp.getNano())
        .build();
  }

  /** Returns the maximum (i.e. furthest in the future) {@link Instant}. */
  public static boolean isBefore(Timestamp first, Timestamp second) {
    return toInstant(first).isBefore(toInstant(second));
  }

  /** Returns the maximum (i.e. furtherest in the future) {@link Instant}. */
  public static boolean isAfter(Timestamp first, Timestamp second) {
    return toInstant(first).isAfter(toInstant(second));
  }

  /** Returns the minimum (i.e. furthest in the past) {@link Instant}. */
  public static Timestamp min(Timestamp first, Timestamp second) {
    if (isBefore(first, second)) {
      return first;
    } else {
      return second;
    }
  }

  /** Returns the maximum (i.e. furthest in the future) {@link Instant}. */
  public static Timestamp max(Timestamp first, Timestamp second) {
    if (isAfter(first, second)) {
      return first;
    } else {
      return second;
    }
  }

  /** Returns the minimum (i.e. furthest in the past) {@link Instant}. */
  public static Timestamp min(Timestamp first, Timestamp... others) {
    Timestamp timestamp = first;
    for (Timestamp other : others) {
      timestamp = min(timestamp, other);
    }
    return timestamp;
  }

  /** Returns the maximum (i.e. furthest in the future) {@link Instant}. */
  public static Timestamp max(Timestamp first, Timestamp... others) {
    Timestamp timestamp = first;
    for (Timestamp other : others) {
      timestamp = max(timestamp, other);
    }
    return timestamp;
  }

  /**
   * Computes the ratio of elapsed time between two {@link Durations}. It is recommended that the
   * {@code dividend} is less than the {@code divisor} otherwise the value is somewhat non-sensical.
   */
  public static Duration between(Timestamp first, Timestamp second) {
    return Duration.between(toInstant(first), toInstant(second));
  }

  /** Computes the difference in seconds between two timestamps. */
  public static double betweenAsSecs(Timestamp first, Timestamp second) {
    return (double) Duration.between(toInstant(first), toInstant(second)).toNanos() / 1000000000;
  }

  /**
   * Computes the ratio of elapsed time between two {@link Durations}. It is recommended that the
   * {@code dividend} is less than the {@code divisor} otherwise the value is somewhat non-sensical.
   */
  public static double divide(Duration dividend, Duration divisor) {
    return (double) dividend.toNanos() / divisor.toNanos();
  }

  // Native methods
  private static final boolean HAS_NATIVE;

  /** Returns a Yuca proto {@link Timestamp} of the current unixtime with microsecond precision. */
  public static Timestamp now() {
    if (!HAS_NATIVE) {
      return fromInstant(Instant.now());
    }
    long timestamp = epochTimeNative();
    long secs = timestamp / 1000000;
    long micros = timestamp - 1000000 * secs;
    return Timestamp.newBuilder().setSecs(secs).setNanos(1000 * micros).build();
  }

  /** Returns a java {@link Instant} of the current unixtime with microsecond precision. */
  public static Instant nowAsInstant() {
    if (!HAS_NATIVE) {
      return Instant.now();
    }
    long timestamp = epochTimeNative();
    long secs = timestamp / 1000000;
    long micros = timestamp - 1000000 * secs;
    return Instant.ofEpochSecond(secs, 1000 * micros);
  }

  /** Returns a Yuca proto {@link Timestamp} of the current monotonic clock time. */
  public static Timestamp monotonicTime() {
    if (!HAS_NATIVE) {
      return fromInstant(Instant.now());
    }
    long monotonicTime = monotonicTimeNative();
    long secs = monotonicTime / 1000000000;
    long nanos = monotonicTime - 1000000000 * secs;
    return Timestamp.newBuilder().setSecs(secs).setNanos(nanos).build();
  }

  /** Returns the unixtime as microseconds. */
  private static native long epochTimeNative();

  /** Returns the monotonic clock time as nanoseconds. */
  private static native long monotonicTimeNative();

  private static boolean loadLibrary() {
    try {
      // TODO: Remember to fix this when we migrate the files over to /src/yuca.
      NativeUtils.loadLibraryFromJar("/yuca/src/main/c/yuca/util/libtime.so");
      return true;
    } catch (Exception e) {
      LoggerUtil.getLogger().info("couldn't load native timestamps library");
      e.printStackTrace();
      return false;
    }
  }

  static {
    HAS_NATIVE = loadLibrary();
  }

  private Timestamps() {}
}
