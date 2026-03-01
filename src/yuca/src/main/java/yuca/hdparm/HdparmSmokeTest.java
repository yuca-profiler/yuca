package yuca.hdparm;

import static java.util.stream.Collectors.joining;
import static yuca.util.LoggerUtil.getLogger;

import java.util.List;
import java.util.logging.Logger;
import java.util.stream.IntStream;
import yuca.signal.SignalInterval;
import yuca.signal.SignalInterval.SignalData;
import yuca.util.Timestamps;

public final class HdparmSmokeTest {
    private static final Logger logger = getLogger();

    private static int fib(int n) {
        if (n == 0 || n == 1) {
        return 1;
        } else {
        return fib(n - 1) + fib(n - 2);
        }
    }

    private static void exercise() {
        fib(42);
    }

    /** Checks if hdparm is available for sampling. */
    private static boolean hdparmAvailable() throws Exception {
        if (!Hdparm.loadLibrary()) {
        logger.info("the native library isn't available!");
        return false;
        }

        HdparmSample start = Hdparm.sample();

        exercise();

        SignalInterval interval = Hdparm.difference(start, Hdparm.sample());

        List<SignalData> readings = interval.getDataList();
        double totalEnergy = 0;
        for(SignalData reading: readings){
            totalEnergy += reading.getValue();
        }
        if (totalEnergy == 0) {
            logger.info("no energy consumed with the difference of two hdparm samples!");
            return false;
        }

        logger.info(
            String.join(
                System.lineSeparator(),
                "hdparm report",
                String.format(
                    " - elapsed time: %.6fs",
                    (double) Timestamps.between(interval.getStart(), interval.getEnd()).toNanos()
                        / 1000000000),
                // TODO: Find a way to display each device model name
                readings.stream()
                    .map(reading -> String.format(
                        " - energy: %.6fJ",
                        reading.getValue()))
                    .collect(joining(System.lineSeparator()))
                )
            );
        return true;
    }

    public static void main(String[] args) throws Exception {
        logger.info("warming up...");
        for (int i = 0; i < 5; i++) exercise();
        logger.info("testing hdparm...");
        if (hdparmAvailable()) {
        logger.info("smoke test passed!");
        } else {
        logger.info("smoke testing failed; please consult the log.");
        }
    }
    private HdparmSmokeTest() {}
}