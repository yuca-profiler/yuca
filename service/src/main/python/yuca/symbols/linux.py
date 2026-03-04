import logging

import numpy as np
import pandas as pd

from yuca.signal_pb2 import Signal
from yuca.symbols.symbol import SOCKET_POWER
from yuca.symbols.symbol import CPU_AMORTIZED_EMISSIONS, SOCKET_OPERATIONAL_EMISSIONS
from yuca.symbols.symbol import CPU_FREQUENCY, SOCKET_TEMPERATURE
from yuca.symbols.symbol import TASK_POWER, TASK_OPERATIONAL_EMISSIONS

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="yuca-processing (%(asctime)s) [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %p %Z",
    level=logging.DEBUG,
)


class SignalProcessor:
    def process(self, signal):
        return self.index, self._process_internal(signal)

    def _process_internal(self, signal):
        pass


class SystemEnergyProcessor(SignalProcessor):
    index = SOCKET_POWER

    def _process_internal(self, signal):
        power = []
        for interval in signal.interval:
            start = 1000000000 * interval.start.secs + interval.start.nanos
            end = 1000000000 * interval.end.secs + interval.end.nanos
            elapsed = (end - start) / 1000000000
            for data in interval.data:
                metadata = {m.name: m.value for m in data.metadata}
                power.append([
                    start,
                    int(metadata['socket']),
                    metadata['component'],
                    data.value / elapsed
                ])
        return pd.DataFrame(
            data=power,
            columns=[
                'timestamp',
                'socket',
                'component',
                'value'
            ]
        ).set_index(['timestamp', 'socket', 'component']).value


class SystemEmissionsProcessor(SignalProcessor):
    index = SOCKET_OPERATIONAL_EMISSIONS

    def _process_internal(self, signal):
        emissions = []
        for interval in signal.interval:
            start = 1000000000 * interval.start.secs + interval.start.nanos
            end = 1000000000 * interval.end.secs + interval.end.nanos
            elapsed = (end - start) / 1000000000
            for data in interval.data:
                metadata = {m.name: m.value for m in data.metadata}
                emissions.append([
                    start,
                    int(metadata['socket']),
                    metadata['component'],
                    data.value / elapsed
                ])
        return pd.DataFrame(
            data=emissions,
            columns=[
                'timestamp',
                'socket',
                'component',
                'value'
            ]
        ).set_index(['timestamp', 'socket', 'component']).value


class SystemTemperatureProcessor(SignalProcessor):
    index = SOCKET_TEMPERATURE

    def _process_internal(self, signal):
        temperature = []
        for interval in signal.interval:
            start = 1000000000 * interval.start.secs + interval.start.nanos
            for data in interval.data:
                metadata = {m.name: m.value for m in data.metadata}
                if metadata['kind'] != 'X86_PKG_TEMP':
                    continue
                temperature.append([
                    start,
                    int(metadata['socket']),
                    data.value
                ])
        return pd.DataFrame(
            data=temperature,
            columns=[
                'timestamp',
                'socket',
                'value'
            ]
        ).set_index(['timestamp', 'socket']).value


class SystemFrequencyProcessor(SignalProcessor):
    index = CPU_FREQUENCY

    def _process_internal(self, signal):
        frequency = []
        for interval in signal.interval:
            start = 1000000000 * interval.start.secs + interval.start.nanos
            for data in interval.data:
                metadata = {m.name: m.value for m in data.metadata}
                if metadata['kind'] != 'observed':
                    continue
                frequency.append([
                    start,
                    int(metadata['socket']),
                    int(metadata['cpu']),
                    data.value
                ])
        return pd.DataFrame(
            data=frequency,
            columns=[
                'timestamp',
                'socket',
                'cpu',
                'value'
            ]
        ).set_index(['timestamp', 'socket', 'cpu']).value


class TaskEnergyProcessor(SignalProcessor):
    index = TASK_POWER

    def _process_internal(self, signal):
        power = []
        for interval in signal.interval:
            start = 1000000000 * interval.start.secs + interval.start.nanos
            end = 1000000000 * interval.end.secs + interval.end.nanos
            elapsed = (end - start) / 1000000000
            for data in interval.data:
                metadata = {m.name: m.value for m in data.metadata}
                power.append([
                    start,
                    int(metadata['socket']),
                    int(metadata['cpu']),
                    int(metadata['task']),
                    metadata['component'],
                    data.value / elapsed
                ])
        return pd.DataFrame(
            data=power,
            columns=[
                'timestamp',
                'socket',
                'cpu',
                'task',
                'component',
                'value'
            ]
        ).set_index(['timestamp', 'socket', 'cpu', 'task', 'component']).value


class TaskEmissionsProcessor(SignalProcessor):
    index = TASK_OPERATIONAL_EMISSIONS

    def _process_internal(self, signal):
        emissions = []
        for interval in signal.interval:
            start = 1000000000 * interval.start.secs + interval.start.nanos
            end = 1000000000 * interval.end.secs + interval.end.nanos
            elapsed = (end - start) / 1000000000
            for data in interval.data:
                metadata = {m.name: m.value for m in data.metadata}
                emissions.append([
                    start,
                    int(metadata['socket']),
                    int(metadata['cpu']),
                    int(metadata['task']),
                    metadata['component'],
                    data.value / elapsed
                ])
        return pd.DataFrame(
            data=emissions,
            columns=[
                'timestamp',
                'socket',
                'cpu',
                'task',
                'component',
                'value'
            ]
        ).set_index(['timestamp', 'socket', 'cpu', 'task', 'component']).value


# Transistor gap temperature
T = -(0.075 * 0.070 / 0.9 - 0.1897) / (8.6173303 * 10**-5)

# TODO: Need to be customizable based on device
# lifespan is 10 years in seconds
cpu_lifespan = 315360000
cpu_embodied_carbon = 10274.2


def compute_amortized_carbon(temperature, frequency, normal_temperature, normal_frequency):
    norm = temperature.copy(deep=True)
    norm[norm > normal_temperature] = normal_temperature
    # e^(T/temp) / e^(T/normal temp) = e^(T/temp - T/normal temp) = e^(T * (1 /temp - 1/normal temp))
    # Temperature must be in Kelvin for aging to prevent unit mismatch
    age = np.exp(T * (1 / (273 + temperature) - 1 / (273 + norm)))

    df = pd.concat(
        [frequency.unstack('cpu'), age],
        axis=1
    )
    dfs = []
    for _, df in df.groupby('socket'):
        df = df.sort_index().ffill().dropna(axis=1, how='all').dropna(axis=0)
        age = df.pop('value')
        for col in df.columns:
            norm = df[col].copy(deep=True)
            norm[norm > normal_frequency] = normal_frequency
            df[col] = (age * df[col] / norm) * \
                (cpu_embodied_carbon / cpu_lifespan)
        df.columns.name = 'cpu'
        dfs.append(df.stack())
    amortized = pd.concat(dfs)
    amortized.name = 'value'
    return amortized


"""
This code is not fully tested but appears to work as expected based on this script:

from itertools import product

import math
import pandas as pd
import numpy as np

from yuca.symbols.linux import compute_amortized_carbon

freq_index = pd.MultiIndex.from_tuples(
    product([1767403714251088000, 1767403714251088010],
            list(range(2)), list(range(9))),
    names=["timestamp", "socket", "cpu"]
)

freq = pd.Series(
    [10e9] * len(freq_index),
    index=freq_index,
    name="value"
)

temp_index = pd.MultiIndex.from_tuples(
    product([1767403714251088005, 1767403714251088015], list(range(2))),
    names=["timestamp", "socket"]
)

temp = pd.Series(
    [37] * len(temp_index),
    index=temp_index,
    name="value"
)

result = compute_amortized_carbon(temp, freq, 40, 1800000000)
assert math.isclose(
    result.sum(),
    0.000181 * len(result),
    rel_tol=1e-4
)
"""

# maps component type + unit to processing
PROCESSORS = {
    ('linux_system', Signal.Unit.JOULES): SystemEnergyProcessor(),
    ('linux_system', Signal.Unit.GRAMS_OF_CO2): SystemEmissionsProcessor(),
    ('linux_system', Signal.Unit.HERTZ): SystemFrequencyProcessor(),
    ('linux_system', Signal.Unit.CELSIUS): SystemTemperatureProcessor(),
    ('linux_process', Signal.Unit.JOULES): TaskEnergyProcessor(),
    ('linux_process', Signal.Unit.GRAMS_OF_CO2): TaskEmissionsProcessor(),
}


def extract_linux_symbols(report):
    symbols = {}
    symbols['metadata'] = {m.name: m.value for m in report.metadata}
    symbols['data'] = {}
    for component in report.component:
        ctype = component.component_type
        cid = component.component_id
        logger.info('Processing component %s (%s)', ctype, cid)
        # component contains component_type, component_id, and Signal obj:
        for signal in component.signal:
            source = '+'.join(signal.source)
            unit = signal.unit
            unit_name = Signal.Unit.DESCRIPTOR.values_by_number[signal.unit].name
            logger.info(' - Processing signal %s (%s)', source, unit_name)
            if (ctype, unit) in PROCESSORS:
                logger.info(
                    ' - Processing with %s',
                    type(PROCESSORS[ctype, unit])
                )
                symbol, df = PROCESSORS[ctype, unit].process(signal)
                symbols['data'][symbol] = df
    if SOCKET_TEMPERATURE in symbols['data'] and CPU_FREQUENCY in symbols['data']:
        logger.info('Adding new signal amortized emissions (GRAMS_OF_CO2)')
        symbols['data'][CPU_AMORTIZED_EMISSIONS] = compute_amortized_carbon(
            symbols['data'][SOCKET_TEMPERATURE],
            symbols['data'][CPU_FREQUENCY],
            # TODO: need system specs to abstract this
            40,
            1800000000
        )
    return symbols


def aggregate_symbols(symbols):
    agg_symbols = {}
    agg_symbols['data'] = {}
    agg_symbols['metadata'] = symbols['metadata']
    for symbol in symbols['data']:
        if symbol in [
            SOCKET_POWER,
            CPU_FREQUENCY,
            SOCKET_OPERATIONAL_EMISSIONS,
            CPU_AMORTIZED_EMISSIONS,
            TASK_POWER,
            TASK_OPERATIONAL_EMISSIONS,
        ]:
            df = symbols['data'][symbol].groupby([
                'timestamp',
                'socket'
            ]).sum().reset_index()
            df.value *= df.timestamp.diff() / 1000000000
        else:
            df = df.reset_index()
        agg_symbols['data'][symbol] = df.groupby('socket').agg({
            'value': ('mean', 'median', 'sum', 'std'),
            'timestamp': ('min', 'max')
        })
        agg_symbols['data'][symbol].columns = [
            'mean',
            'median',
            'sum',
            'std',
            'start',
            'end'
        ]
        start = agg_symbols['data'][symbol]['start']
        end = agg_symbols['data'][symbol]['end']
        agg_symbols['data'][symbol]['elapsed'] = end - start
    return agg_symbols
