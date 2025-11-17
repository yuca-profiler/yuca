import json
import logging
import pickle
import os
import uuid

from io import BytesIO
from zipfile import ZipFile

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="yuca-processing (%(asctime)s) [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %p %Z",
    level=logging.DEBUG,
)


def write_symbols(symbols, file_path):
    logger.info('writing symbols to %s', file_path)
    with ZipFile(file_path, 'w') as file:
        index = {}
        file.writestr('metadata.json', json.dumps(symbols['metadata']))
        for symbol in symbols['data']:
            key = str(uuid.uuid4())
            index[key] = symbol
            logger.info('writing data for symbol %s as %s', symbol, key)
            file.writestr(f'{key}.csv', symbols['data'][symbol].to_csv())
        file.writestr('index.json', pickle.dumps(index))
        file.close()
    logger.info('wrote %d symbols to %s', len(index), file_path)


def load_symbols(file_path):
    logger.info('loading symbols from %s', file_path)
    symbols = {}
    symbols['data'] = {}
    with ZipFile(file_path, 'r') as file:
        symbols['metadata'] = json.loads(file.read('metadata.json'))
        index = pickle.loads(file.read('index.json'))
        for symbol in index:
            data = file.read(f'{symbol}.csv')
            # TODO: there must be a better way
            df = pd.read_csv(BytesIO(data))
            df = df.set_index(list(df.columns[:-1])).value
            symbols['data'][index[symbol]] = df
            logger.info('loaded symbol for %s', index[symbol])
    logger.info('loaded %d symbols from %s', len(symbols['data']), file_path)
    return symbols
