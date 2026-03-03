java_library(
    name = "commands",
    visibility = ["//visibility:public"],
    srcs = glob(["*.java"]),
    deps = [
        "//src/yuca/src/main/java/yuca/linux/drive:drive",
        "//src/yuca/src/main/java/yuca/linux/drive/powermode:powermode",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
)

java_binary(
    name = "smoke_test",
    main_class = "yuca.linux.drive.commands.DriveSmokeTest",
    srcs = ["DriveSmokeTest.java"],
    deps = [
        ":commands",
        "//src/yuca/src/main/java/yuca/linux/drive/powermode:powermode",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
)
  