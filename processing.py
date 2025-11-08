import argparse
import logging
import os

from zipfile import ZipFile

import pandas as pd

from yuca.signal_pb2 import Report
from yuca.symbols.linux import extract_linux_symbols, aggregate_symbols
from yuca.symbols.util import load_symbols, write_symbols

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="yuca-processing (%(asctime)s) [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %p %Z",
    level=logging.DEBUG,
)


def parse_args():
    parser = argparse.ArgumentParser(description='yuca signal processor')
    parser.add_argument(
        nargs='*',
        type=str,
        help='yuca report protos',
        dest='files',
    )
    parser.add_argument(
        '--symbol_output',
        dest='symbol_output',
        required=False,
        help='location to write the symbol files as an archive',
        type=str,
    )
    parser.add_argument(
        '--agg_output',
        dest='agg_output',
        required=False,
        help='location to write the aggregated symbol files as an archive',
        type=str,
    )

    return parser.parse_args()


def parse_symbols_from_file(report_file):
    logger.info('parsing signals for %s', report_file)
    report = Report()
    report.ParseFromString(open(report_file, 'rb').read())
    return extract_linux_symbols(report)


def parse_symbols_from_directory(report_file):
    logger.info('parsing signals from %s', report_file)
    symbols = []
    for file in os.listdir(report_file):
        _, file_type = os.path.splitext(os.path.basename(file))
        if os.path.isdir(file):
            symbols.extend(parse_symbols_from_directory(file))
        elif file_type == r'.pb':
            symbols.append(parse_symbols_from_file(file))
    return symbols


def parse_symbols_from_archive(report_file):
    logger.info('parsing signals from %s', report_file)
    symbols = []
    with ZipFile(report_file, 'r') as archive_file:
        for file in archive_file.filelist:
            _, file_type = os.path.splitext(os.path.basename(file.filename))
            if file_type != r'.pb':
                continue
            logger.info('parsing signals for %s', file.filename)
            report = Report()
            report.ParseFromString(archive_file.read(file))
            symbols.append(extract_linux_symbols(report))
    return symbols


def aggregate_symbols_with_metadata(symbols):
    agg_symbols = []
    suite = symbols['metadata']['suite']
    workload = symbols['metadata']['workload']
    iteration = symbols['metadata']['iteration']
    logger.info('aggregating symbols for workload=%s, iteration=%s',
                workload, iteration)
    agg = aggregate_symbols(symbols)
    for symbol in agg['data']:
        logger.info(' - aggregating symbol %s', symbol)
        agg_symbols.append(agg['data'][symbol].assign(
            suite=suite,
            workload=workload,
            iteration=iteration,
            symbol=str(symbol),
        ).set_index(['suite', 'workload', 'iteration', 'symbol'], append=True))
    return agg_symbols


def main():
    args = parse_args()

    all_symbols = []
    for report_file in args.files:
        _, file_type = os.path.splitext(os.path.basename(report_file))
        if os.path.isdir(report_file):
            all_symbols.extend(parse_symbols_from_directory(report_file))
        elif file_type == r'.pb':
            all_symbols.append(parse_symbols_from_file(report_file))
        elif file_type == r'.zip':
            all_symbols.extend(parse_symbols_from_archive(report_file))
        else:
            logger.info('found unhandlable file %s', report_file)

    agg_symbols = []
    for symbols in all_symbols:
        if args.symbol_output:
            symbol_file = f'{os.path.join(args.output_path, )}.zip'
            write_symbols(symbols, symbol_file)
        if args.agg_output:
            agg_symbols.extend(aggregate_symbols_with_metadata(symbols))
    agg_symbols = pd.concat(agg_symbols)
    agg_symbols.to_csv(os.path.join(args.agg_output, 'agg_symbols.csv'))


if __name__ == '__main__':
    main()
