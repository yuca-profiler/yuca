package yuca.hdparm;

import yuca.util.NativeUtils;
import yuca.hdparm.PowerMode;
import yuca.hdparm.Hdparm;
import yuca.hdparm.HdparmReading;

import java.util.List;

public final class HdparmSmokeTest {
    public static native int powerMode(String device); //returns jint from c

    public static String getPowerMode(String device) {
        int rawValue = powerMode(device);
        return PowerMode.fromValue(rawValue).getState();
    }

    static {
        try {
            NativeUtils.loadLibraryFromJar("/yuca/src/main/c/yuca/hdparm/libhdparm.so");
        } catch (Exception e) {
            e.printStackTrace();
            // Fallback to system library
            try {
                System.loadLibrary("hdparm");
            } catch (UnsatisfiedLinkError err) {
                err.printStackTrace();
            }
        }
    }

    public static void main(String[] args) {
        System.out.println("Testing hdparm JNI wrapper...");
        try {
            HdparmSample sample = Hdparm.sample();
            List<HdparmReading> readings = sample.data();
            for(HdparmReading r: readings){
                System.out.println(r.device + ' ' + r.mode.getState());
            }
        } catch (UnsatisfiedLinkError e) {
            System.err.println("Failed to call native method: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private HdparmSmokeTest() {}
}