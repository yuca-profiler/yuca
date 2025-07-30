BINARY_SRCS = ["PowercapSmokeTest.java"]

java_library(
    name = "powercap",
    visibility = ["//visibility:public"],
    srcs = glob(["*.java"], exclude = BINARY_SRCS),
    deps = [
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
)

java_binary(
    name = "smoke_test",
    main_class = "yuca.linux.powercap.PowercapSmokeTest",
    srcs = ["PowercapSmokeTest.java"],
    deps = [
        ":powercap",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
)