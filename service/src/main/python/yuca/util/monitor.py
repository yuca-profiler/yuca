""" a tool that watches another process until it dies """
import json

from argparse import ArgumentParser
from os import getpid
from time import sleep

from psutil import pid_exists

from yuca.client import YucaClient


def parse_args():
    """ Parses client-side arguments. """
    parser = ArgumentParser()
    parser.add_argument(
        '--pid',
        dest='pid',
        type=int,
        default=getpid(),
        help='pid to be monitored',
    )
    parser.add_argument(
        '--period',
        dest='period',
        type=int,
        default=10,
        help='sampling period',
    )
    parser.add_argument(
        '--addr',
        dest='addr',
        type=str,
        default='localhost:8980',
        help='address of the smaragdine server',
    )
    parser.add_argument(
        '-s',
        '--signals',
        dest='signals',
        type=str,
        default='yuca.emissions.Emissions',
        help='signals to read from yuca',
    )
    parser.add_argument(
        '--output_path',
        dest='output_path',
        type=str,
        default='/tmp',
        help='location to write the report',
    )
    return parser.parse_args()


def main():
    args = parse_args()

    signals = args.signals.split(',')
    if getpid() == args.pid:
        print('i refuse to watch myself!')
        return
    if any('yuca.cpu' in signal or 'yuca.emissions' for signal in signals):
        client = YucaClient(args.addr)
        client.start(args.pid, args.period)
    while pid_exists(args.pid):
        sleep(1)
    if any('yuca.cpu' in signal or 'yuca.emissions' for signal in signals):
        client.stop(args.pid)
        yuca_signal = client.read(args.pid, signals)
    print({
        signal.signal_name: sum(
            s.data.value for s in signal.signal) for signal in yuca_signal.signal})


if __name__ == '__main__':
    main()
