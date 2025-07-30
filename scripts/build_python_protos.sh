python3 -m grpc_tools.protoc \
    -Iservice/src/main/proto/yuca/service \
    -Isrc/yuca/src/main/proto/yuca/signal \
    --python_out=service/src/main/python/yuca \
    --pyi_out=service/src/main/python/yuca \
    --grpc_python_out=service/src/main/python/yuca \
    src/yuca/src/main/proto/yuca/signal/signal.proto \
    service/src/main/proto/yuca/service/yuca_service.proto
