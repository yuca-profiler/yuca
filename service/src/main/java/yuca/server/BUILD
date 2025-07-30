SERVER_BINARIES=[
    "YucaServer.java",
]

java_library(
    name = "server_impl",
    srcs = glob(["*.java"], exclude=SERVER_BINARIES),
    deps = [
        "//service/src/main/proto/yuca/service:yuca_service_java_protos",
        "//service/src/main/proto/yuca/service:yuca_service_java_grpc",
        "//src/yuca:yuca",
        "@grpc-java//stub",
    ],
    exports = [
        "//service/src/main/proto/yuca/service:yuca_service_java_protos",
        "//service/src/main/proto/yuca/service:yuca_service_java_grpc",
    ]
)

java_binary(
    name = "server",
    visibility = ["//service:__pkg__"],
    srcs = ["YucaServer.java"],
    main_class = "yuca.server.YucaServer",
    runtime_deps = ["@grpc-java//netty"],
    deps = [
        ":server_impl",
        "@grpc-java//api",
        "@maven//:commons_cli_commons_cli",
    ]
)
