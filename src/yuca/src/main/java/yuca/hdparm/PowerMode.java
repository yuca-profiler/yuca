package yuca.hdparm;
import java.util.Map;
import java.util.HashMap;

public enum PowerMode{
    STANDBY,
    NVCACHE_SPINDOWN,
    NVCACHE_SPINUP,
    IDLE,
    ACTIVE_IDLE,
    UNKNOWN;

    public static PowerMode fromRegister(int reg) {
        switch (reg) {
            case 0x00: return STANDBY;
            case 0x40: return NVCACHE_SPINDOWN;
            case 0x41: return NVCACHE_SPINUP;
            case 0x80: return IDLE;
            case 0xff: return ACTIVE_IDLE;
            default:   return UNKNOWN;
        }
    }
//     STANDBY(0x00, "standby"),
//     NVCACHE_SPINDOWN(0x40, "NVcache_spindown"),
//     NVCACHE_SPINUP(0x41, "NVcache_spinup"),
//     IDLE(0x80, "idle"),
//     ACTIVE_IDLE(0xff, "active/idle"),
//     UNKNOWN(-1, "unknown");
// //     case 0x00: state = "standby";		break;
// //     case 0x40: state = "NVcache_spindown";	break;
// //     case 0x41: state = "NVcache_spinup";	break;
// //     case 0x80: state = "idle";		break;
// //     case 0xff: state = "active/idle";	break;
//     private static final Map<Integer, PowerMode> MODE_MP = new HashMap<>();
//     private final int value;
//     private final String state; 

//     static {
//         for (PowerMode mode: values()){
//             MODE_MP.put(mode.value, mode);
//         }
//     }
//     private PowerMode(int value, String state){
//         this.value = value;
//         this.state = state;
//     }

//     public int getValue(){
//         return value;
//     }
//     public String getState(){
//         return state;
//     }
//     static PowerMode fromValue(int value){
//         return MODE_MP.getOrDefault(value, UNKNOWN);
//     }
}