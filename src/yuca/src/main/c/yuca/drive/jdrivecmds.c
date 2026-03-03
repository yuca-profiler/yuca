#include <jni.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/hdreg.h>

// Type definitions
typedef unsigned char __u8;

static int open_flags = O_RDONLY|O_NONBLOCK;

#define HDIO_DRIVE_CMD         0x031f
#define ATA_OP_SMART           0xb0
#define ATA_OP_CHECKPOWERMODE1 0xe5
#define ATA_OP_CHECKPOWERMODE2 0x98

int do_drive_cmd(int fd, unsigned char *args, unsigned int timeout_secs)
{
    return ioctl(fd, HDIO_DRIVE_CMD, args);
}

/** Returns the current IDE (Integrated Drive Electronics) power mode status of a Linux block device 
  * Replicates `hdparm -C` behavior, Consult https://man7.org/linux/man-pages/man8/hdparm.8.html for more details.
  */
int get_powermode(const char *devname) {
    int err = 0;
    int fd = open(devname, open_flags);
    if (fd < 0) {
        return err;
    }
    
    __u8 args[4] = {ATA_OP_CHECKPOWERMODE1, 0, 0, 0};
    
    if (do_drive_cmd(fd, args, 0)
        && (args[0] = ATA_OP_CHECKPOWERMODE2) /* (single =) try again with 0x98 */
        && do_drive_cmd(fd, args, 0)) {
        err = errno;
        close(fd);
        return err;
    } 
    
    close(fd);
    return (int) args[2];
}

JNIEXPORT jint JNICALL
Java_yuca_linux_drive_commands_DriveCommands_powerMode(JNIEnv *env, jclass jcls, jstring jdevice) {
    const char *device = (*env)->GetStringUTFChars(env, jdevice, NULL);
    if (device == NULL){
        return -1;
    }
    int result = get_powermode(device);

    (*env)->ReleaseStringUTFChars(env, jdevice, device);

    return (jint) result;
}