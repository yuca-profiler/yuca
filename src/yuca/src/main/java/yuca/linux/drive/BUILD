BINARY_SRCS = ["DriveSmokeTest.java"]

java_library(
    name = "drive",
    visibility = ["//visibility:public"],
    srcs = glob(["*.java"], exclude = BINARY_SRCS),
    deps = [
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/java/yuca/linux/drive/spec:spec",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
    resources = [
        "//src/yuca/src/main/c/yuca/drive:libdrivecmds.so",
        "//src/yuca/src/main/resources/disks:disks_data"
        ],
)

java_binary(
    name = "smoke_test",
    main_class = "yuca.linux.drive.DriveSmokeTest",
    srcs = ["DriveSmokeTest.java"],
    deps = [
        ":drive",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
)