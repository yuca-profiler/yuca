# yuca

## Building

 - Install bazel through https://bazel.build/install
 - Install Java 11+
 - Install python version 3.12
 - To use rapl, you may need to run `sudo modprobe msr` to enable the registers.
 - Create a new venv with `pip -m venv .venv` and activate it with `source .venv/bin/activate`.
 - Run `bash build_yuca.sh` to build the codebase. This may take a few minutes.

## Running

To run Java benchmarks, run:
 - `sudo bash benchmarks/run_dacapo.sh`
 - `sudo bash benchmarks/run_renaissance.sh`

To run python benchmarks, first create a server with `sudo bash run_yuca_sever.sh`. Then open a new terminal, and run `bash benchmarks/run_pyperformance.sh`.

To run the BERT experiments, first create a server with `sudo bash run_yuca_sever_with_nvml.sh` if you are using a GPU or `sudo bash run_yuca_sever.sh` otherwise. Then open a new terminal, and run `bash experiments/bert_finetune/bert_glue_finetune_experiment_test.sh` or `bash experiments/bert_finetune/bert_glue_finetune_experiment.sh`.

## Data

The full plots for our evaluation can be found in https://github.com/yuca-profiler/yuca/tree/main/evaluation.
