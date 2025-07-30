java_library(
    name = "signal",
    visibility = ["//src/yuca:__pkg__"],
    srcs = glob(["*.java"]),
    deps = [
        "//src/yuca/src/main/java/yuca/linux",
        "//src/yuca/src/main/java/yuca/linux/jiffies",
        "//src/yuca/src/main/java/yuca/linux/powercap",
        "//src/yuca/src/main/java/yuca/emissions",
        "//src/yuca/src/main/java/yuca/rapl",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
    exports = [
        "//src/yuca/src/main/java/yuca/linux",
        "//src/yuca/src/main/java/yuca/linux/jiffies",
        "//src/yuca/src/main/java/yuca/linux/powercap",
        "//src/yuca/src/main/java/yuca/emissions",
        "//src/yuca/src/main/java/yuca/rapl",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ]
)
