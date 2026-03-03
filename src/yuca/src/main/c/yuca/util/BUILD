cc_library(
    name = "time-lib",
    visibility = ["//src/yuca/src/main/c/yuca/rapl:__pkg__"],
    srcs = glob(["*.c"]),
    hdrs = glob(["*.h"]),
    deps = ["//src/yuca/src/main/c:copy_jni_hdr_lib"],
    alwayslink = True,
)

cc_binary(
    name = "libtime.so",
    visibility = ["//src/yuca/src/main/java/yuca/util:__pkg__"],
    linkshared = True,
    data = glob(["*.h"]),
    deps = [":time-lib"],
)
