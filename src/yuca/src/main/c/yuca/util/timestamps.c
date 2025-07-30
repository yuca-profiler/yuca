#include <jni.h>

#include "time.h"

JNIEXPORT jlong JNICALL Java_yuca_util_Timestamps_epochTimeNative
  (JNIEnv *env, jclass jcls) {
	return usec_since_epoch();
}

JNIEXPORT jlong JNICALL Java_yuca_util_Timestamps_monotonicTimeNative
  (JNIEnv *env, jclass jcls) {
	return usec_monotonic_time();
}
