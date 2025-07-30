load("@rules_jvm_external//:defs.bzl", "artifact")

java_library(
    name = "thermal",
    visibility = ["//visibility:public"],
    srcs = glob(["*.java"]),
    deps = [
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
        artifact("commons-cli:commons-cli"),
    ],
)
