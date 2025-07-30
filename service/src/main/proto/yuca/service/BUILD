load("@protobuf//bazel:java_proto_library.bzl", "java_proto_library")
load("@grpc-java//:java_grpc_library.bzl", "java_grpc_library")

proto_library(
    name = "yuca_service_protos",
    srcs = ["yuca_service.proto"],
    deps = ["//src/yuca/src/main/proto/yuca/signal:signal_protos"]
)

java_proto_library(
    name = "yuca_service_java_protos",
    visibility = ["//visibility:public"],
    deps = [":yuca_service_protos"]
)

java_grpc_library(
    name = "yuca_service_java_grpc",
    visibility = ["//visibility:public"],
    srcs = [":yuca_service_protos"],
    deps = [":yuca_service_java_protos"]
)
