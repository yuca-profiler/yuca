#include <jni.h>

#ifndef _Included_yuca_util_Timestamps
#define _Included_yuca_util_Timestamps

JNIEXPORT jlong JNICALL Java_yuca_util_Timestamps_epochTimeNative
   (JNIEnv *, jclass);

JNIEXPORT jlong JNICALL Java_yuca_util_Timestamps_monotonicTimeNative
   (JNIEnv *, jclass);
