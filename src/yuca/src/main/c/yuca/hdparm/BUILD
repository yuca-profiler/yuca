cc_library(
    name = "hdparm-lib",
    srcs = glob(["*.c"]),
    # hdrs = glob(["*.h"]),
    deps = [
      "//src/yuca/src/main/c:copy_jni_hdr_lib",
      "//src/yuca/src/main/c/yuca/util:time-lib",
    ],
    alwayslink = True,
)

cc_binary(
    name = "libhdparm.so",
    visibility = ["//src/yuca/src/main/java/yuca/hdparm:__pkg__"],
    linkshared = True,
    # data = glob(["*.h"]),
    deps = [":hdparm-lib"],
)