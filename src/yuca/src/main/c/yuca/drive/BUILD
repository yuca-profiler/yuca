cc_library(
    name = "drivecmds-lib",
    srcs = glob(["*.c"]),
    deps = [
      "//src/yuca/src/main/c:copy_jni_hdr_lib",
    ],
    alwayslink = True,
)

cc_binary(
    name = "libdrivecmds.so",
    visibility = ["//src/yuca/src/main/java/yuca/linux/drive:__pkg__"],
    linkshared = True,
    deps = [":drivecmds-lib"],
)