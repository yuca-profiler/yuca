""" a client that can talk to an yuca server. """
from argparse import ArgumentParser
from os import getpid
from pprint import pprint

from yuca.client import YucaClient
from yuca.util import fib


def parse_args():
    """ Parses client-side arguments. """
    parser = ArgumentParser('yuca smoke tester')
    parser.add_argument(
        '-n',
        '--number',
        dest='n',
        type=int,
        default=33,
        help='fibonacci number to compute',
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
    return parser.parse_args()


def main():
    args = parse_args()

    signals = args.signals.split(',')
    pid = getpid()

    print(f'smoke testing server at {args.addr} with fib({args.n})')
    client = YucaClient(args.addr)
    client.start(pid, 100)
    fib(args.n)
    client.stop(pid)
    report = client.read(pid, signals)
    # TODO: this is too vague
    results = {}
    for component in report.component:
        for signal in component.signal:
            key = f'{component.component_type}:{str(signal.unit)}-{",".join(list(signal.source))}'
            results[key] = sum(
                data.value for interval in signal.interval for data in interval.data
            )
    pprint(results)


if __name__ == '__main__':
    main()
