graceful_terminate() {
    echo "terminating servers gracefully"
}
trap 'graceful_terminate' SIGINT SIGTERM INT

python3 -m yuca.nvml.server &
nvml_pid=$!

java -jar bazel-bin/service/src/main/java/yuca/server/server_deploy.jar -nvml &
yuca_pid=$!

wait
python3 -m yuca.cli purge
kill -9 $yuca_pid $nvml_pid
