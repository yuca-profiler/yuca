import argparse
import os

from re import search
from time import time
from time import sleep

import psutil
import pandas as pd

from yuca.client import YucaClient
from yuca.report import to_dataframe

from yuca.symbols.linux import extract_linux_symbols, aggregate_symbols
from yuca.symbols.util import load_symbols, write_symbols

DEFAULT_SIGNALS = [
    'linux_process',
    'linux_system',
    'ACTIVITY',
    'JOULES',
    'GRAMS_OF_CO2',
    'CELSIUS',
    'HERTZ',
]


def parse_args():
    parser = argparse.ArgumentParser(
        description='multiprocessed yuca monitor for pyperformance')
    parser.add_argument('-p', '--pid', type=int, help='pid to monitor')
    parser.add_argument(
        '--addr',
        default='localhost:8980',
        type=str,
        help='grpc server address',
    )
    parser.add_argument(
        '--output',
        type=str,
        help='location to write the log',
    )
    return parser.parse_args()


def is_child_process(child):
    child_pid = child.pid
    if not psutil.pid_exists(child_pid):
        return None
    try:
        cmd = child.cmdline()
        if "pip" in cmd:
            return None
        elif len(cmd) == 0:
            return None
        else:
            return child_pid, '@'.join(cmd)
    except:
        return None


def get_child_process(process):
    while True:
        for child in process.children(recursive=False):
            child = is_child_process(child)
            if child is not None:
                return child


def monitor_process(pid, client):
    client.start(pid, 10)
    chunks = []
    last = time()
    while psutil.pid_exists(pid):
        sleep(1)
    client.stop(pid)
    print(f"pid {pid} still finsihes")
    return client.read(
        pid,
        DEFAULT_SIGNALS
    )


def main():
    args = parse_args()

    process = psutil.Process(pid=args.pid)  # Main process to track
    print(f'monitoring process {args.pid}')

    client = YucaClient(args.addr)
    client.purge()
    i = 0
    try:
        # The psutil stuff is a hack for working with pyperformance
        signals = monitor_process(
            args.pid,
            client
        )
        #  Write to disk as binary protobuf
        with open(os.path.join(args.output, f'yuca-{args.pid}-{i}.pb'), "wb") as f:
            f.write(signals.SerializeToString())
        i += 1
        # return signals
        # print("done monitoring")
        # symbols = extract_linux_symbols(signals)
        # # TODO: write the data
        # symbol_file = f'{args.output}.zip'
        # print(symbol_file)
        # write_symbols(symbols, symbol_file)
        # agg_symbols.to_csv(os.path.join(args.agg_output, 'agg_symbols.csv'))
        print(f'pid {args.pid} terminated')
    except KeyboardInterrupt:
        print(f'monitoring of pid {args.pid} ended by user')


if __name__ == '__main__':
    main()
