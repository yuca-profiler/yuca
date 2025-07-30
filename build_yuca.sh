bazel build src/yuca:sys_thermal_cooldown_deploy.jar
bazel build benchmarks:dacapo
bazel build benchmarks:renaissance
bazel build --javacopt="-XepDisableAllChecks" service
pip install .
pip install protobuf==6.31.1 # required hack to install TF but also use grpcio
