BENCHMARK_SRCS = [
    "YucaDacapoCallback.java",
    "YucaRenaissancePlugin.java",
]

java_binary(
    name = "dacapo",
    main_class = "Harness",
    visibility = ["//benchmarks:__pkg__"],
    srcs = ["YucaDacapoCallback.java"],
    deps = [
        "//benchmarks/src/main/java/yuca/benchmarks/util",
        "//src/yuca:yuca",
        "@dacapo",
    ],
    args = [
        "--callback yuca.benchmarks.YucaDacapoCallback",
        "--no-validation",
    ]
)

java_binary(
    name = "renaissance",
    main_class = "org.renaissance.core.Launcher",
    visibility = ["//benchmarks:__pkg__"],
    srcs = ["YucaRenaissancePlugin.java"],
    deps = [
        "//benchmarks/src/main/java/yuca/benchmarks/util",
        "//src/yuca:yuca",
        "@renaissance//jar",
    ],
    args = [
        "--plugin !yuca.benchmarks.YucaRenaissancePlugin",
    ]
)
