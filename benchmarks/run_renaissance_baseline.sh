DATA_DIR=renaissance-baseline-data
mkdir -p "${DATA_DIR}"

ITERATIONS=128
PERIOD=0
LOCALE=USA

run_benchmark() {
    java -jar bazel-bin/src/yuca/sys_thermal_cooldown_deploy.jar -period 10000 -temperature 35
    local data_dir="${DATA_DIR}/${BENCHMARK}"
    mkdir -p "${data_dir}"
    java \
        -Dyuca.benchmarks.output="${data_dir}" \
        -Dyuca.benchmarks.period="${PERIOD}" \
        -Dyuca.emissions.locale="${LOCALE}" \
        -jar bazel-bin/benchmarks/src/main/java/yuca/benchmarks/renaissance_deploy.jar \
        -r ${ITERATIONS} \
        --plugin "!yuca.benchmarks.YucaRenaissancePlugin" \
        ${BENCHMARK}
}

BENCHMARKS=(
    scrabble
    page-rank
    future-genetic
    akka-uct
    movie-lens
    scala-doku
    chi-square
    fj-kmeans
    rx-scrabble
    db-shootout
    neo4j-analytics
    finagle-http
    reactors
    dec-tree
    scala-stm-bench7
    naive-bayes
    als
    par-mnemonics
    scala-kmeans
    philosophers
    log-regression
    gauss-mix
    mnemonics
    dotty
    finagle-chirper
)

for BENCHMARK in ${BENCHMARKS[@]}; do
    run_benchmark
done
