BINARY_SRCS = ["RaplSmokeTest.java"]

java_library(
    name = "rapl",
    visibility = ["//visibility:public"],
    srcs = glob(["*.java"], exclude = BINARY_SRCS),
    deps = [
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
    resources = ["//src/yuca/src/main/c/yuca/rapl:libjrapl.so"],
)

java_binary(
    name = "smoke_test",
    main_class = "yuca.rapl.RaplSmokeTest",
    srcs = ["RaplSmokeTest.java"],
    deps = [
        ":rapl",
        "//src/yuca/src/main/java/yuca/util",
        "//src/yuca/src/main/proto/yuca/signal:signal_java_protos",
    ],
)