BINARY_SRCS = [""]

java_library(
    name = "hdparm",
    visibility = ["//visibility:public"],
    srcs = glob(["*.java"], exclude = BINARY_SRCS),
    deps = [
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
    resources = ["//src/yuca/src/main/c/yuca/hdparm:libhdparm.so"],
)

# java_binary(
#     name = "hdparm_smoke_test",
#     main_class = "yuca.hdparm.HdParm",
#     srcs = ["HdParm.java"],
#     deps = [
#         ":hdparm",
#         "//src/yuca/src/main/java/yuca/util",
#         "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
#     ],
# )

java_binary(
    name = "hdparm_disk_monitor",
    main_class = "yuca.hdparm.DiskMonitor",
    srcs = ["DiskMonitor.java"],
    deps = [
        ":hdparm",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
)

java_binary(
    name = "lazy_smoke_test",
    main_class = "yuca.hdparm.Hdparm",
    srcs = ["Hdparm.java"],
    deps = [
        ":hdparm",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
)

java_binary(
    name = "smoke_test",
    main_class = "yuca.hdparm.HdparmSmokeTest",
    srcs = ["HdparmSmokeTest.java"],
    deps = [
        ":hdparm",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
)

java_binary(
    name = "drive_power_smoke",
    main_class = "yuca.hdparm.DrivePowerRegistry",
    srcs = ["DrivePowerRegistry.java"],
    deps = [
        ":hdparm",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
)
