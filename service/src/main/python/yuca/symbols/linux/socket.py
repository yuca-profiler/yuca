import pandas as pd

from yuca.signal_pb2 import Signal
from yuca.symbols.symbol import SOCKET_POWER, SOCKET_PACKAGE_POWER, SOCKET_DRAM_POWER
from yuca.symbols.symbol import SOCKET_OPERATIONAL_EMISSIONS, SOCKET_PACKAGE_OPERATIONAL_EMISSIONS, SOCKET_DRAM_OPERATIONAL_EMISSIONS
from yuca.symbols.symbol import CPU_FREQUENCY, CPU_AMORTIZED_EMISSIONS, SOCKET_TEMPERATURE, DRAM_AMORTIZED_EMISSIONS
from yuca.symbols.symbol import TASK_POWER, TASK_OPERATIONAL_EMISSIONS, TASK_PACKAGE_OPERATIONAL_EMISSIONS, TASK_DRAM_OPERATIONAL_EMISSIONS
from yuca.symbols.symbol import DISK_POWER, DISK_OPERATIONAL_EMISSIONS, DISK_AMORTIZED_EMISSIONS

from yuca.symbols.unit import SocketComponentKind
from yuca.symbols.processor import SignalProcessor, interval_bounds, get_metadata

class SocketTotalProcessor(SignalProcessor):

    group_fields = []
    def _process_internal(self, signal):
        rows = []
        for interval in signal.interval:
            start, elapsed = interval_bounds(interval)
            accum = {}
            for data in interval.data:
                metadata = get_metadata(data)
                if 'component' not in metadata:
                    continue
                extra = [int(metadata[field]) for field in self.group_fields]
                device_id = f"socket:{int(metadata['socket'])}"
                key = (device_id, *extra)
                accum[key] = accum.get(key, 0) + data.value
    
            for key, total_value in accum.items():
                rows.append([start, *key, total_value / elapsed, elapsed])
                
        index_cols = ['timestamp', 'device_id', *self.group_fields]
        columns = [*index_cols, 'value', 'elapsed']
        return pd.DataFrame(
            data=rows,
            columns=columns
            ).set_index(index_cols)

class SocketComponentProcessor(SignalProcessor):
    component_kind = None
    group_fields = []

    def _process_internal(self, signal):
        rows = []
        for interval in signal.interval:
            start, elapsed = interval_bounds(interval)
            for data in interval.data:
                metadata = get_metadata(data)
                if 'component' not in metadata:
                    continue
                component = metadata['component'].upper()
                if component not in SocketComponentKind.__members__:
                    logger.info(
                        '%s is not a supported SocketComponentKind', component)
                    continue
                if component != self.component_kind.name:
                    continue
                extra = [int(metadata[field]) for field in self.group_fields]
                rows.append([
                    start,
                    f"socket:{int(metadata['socket'])}",
                    *extra,
                    metadata['component'],
                    data.value / elapsed,
                    elapsed,
                ])
 
        index_cols = ['timestamp', 'device_id', *self.group_fields, 'component']
        columns = [*index_cols, 'value', 'elapsed']
        return pd.DataFrame(
            data=rows,
            columns=columns
            ).set_index(index_cols)
 
# ---- System (socket-scoped) power ----
 
class SystemEnergyProcessor(SocketTotalProcessor):
    index = SOCKET_POWER
 
 
class SystemPackagePowerProcessor(SocketComponentProcessor):
    index = SOCKET_PACKAGE_POWER
    component_kind = SocketComponentKind.PACKAGE
 
 
class SystemDramPowerProcessor(SocketComponentProcessor):
    index = SOCKET_DRAM_POWER
    component_kind = SocketComponentKind.DRAM
 
 
# ---- System (socket-scoped) emissions ----
 
class SystemEmissionsProcessor(SocketTotalProcessor):
    index = SOCKET_OPERATIONAL_EMISSIONS
 
 
class SystemPackageEmissionsProcessor(SocketComponentProcessor):
    index = SOCKET_PACKAGE_OPERATIONAL_EMISSIONS
    component_kind = SocketComponentKind.PACKAGE
 
 
class SystemDramEmissionsProcessor(SocketComponentProcessor):
    index = SOCKET_DRAM_OPERATIONAL_EMISSIONS
    component_kind = SocketComponentKind.DRAM


# ---- Task (socket+cpu+task-scoped) power/emissions ----
# Same shapes as System above; the only difference is group_fields, which
# adds cpu/task to both the grouping key and the output index.
 
class TaskEnergyProcessor(SocketTotalProcessor):
    index = TASK_POWER
    group_fields = ['cpu', 'task']
 
class TaskEmissionsProcessor(SocketTotalProcessor):
    index = TASK_OPERATIONAL_EMISSIONS
    group_fields = ['cpu', 'task']
 
 
class TaskPackageEmissionsProcessor(SocketComponentProcessor):
    index = TASK_PACKAGE_OPERATIONAL_EMISSIONS
    component_kind = SocketComponentKind.PACKAGE
    group_fields = ['cpu', 'task']
 
 
class TaskDramEmissionsProcessor(SocketComponentProcessor):
    index = TASK_DRAM_OPERATIONAL_EMISSIONS
    component_kind = SocketComponentKind.DRAM
    group_fields = ['cpu', 'task']


class SystemTemperatureProcessor(SignalProcessor):
    index = SOCKET_TEMPERATURE

    def _process_internal(self, signal):
        rows = []
        for interval in signal.interval:
            start, elapsed = interval_bounds(interval)
            for data in interval.data:
                metadata = get_metadata(data)
                if metadata['kind'] != 'X86_PKG_TEMP':
                    continue
                rows.append([
                    start,
                    f"socket:{int(metadata['socket'])}",
                    data.value,
                    elapsed
                ])
        return pd.DataFrame(
            data=rows,
            columns=[
                'timestamp',
                'device_id',
                'value',
                'elapsed'
            ]
        ).set_index(['timestamp', 'device_id'])

class SystemFrequencyProcessor(SignalProcessor):
    index = CPU_FREQUENCY

    def _process_internal(self, signal):
        frequency = []
        for interval in signal.interval:
            start, elapsed = interval_bounds(interval)
            for data in interval.data:
                metadata = get_metadata(data)
                if metadata['kind'] != 'observed':
                    continue
                frequency.append([
                    start,
                    f"socket:{int(metadata['socket'])}",
                    int(metadata['cpu']),
                    data.value,
                    elapsed
                ])
        return pd.DataFrame(
            data=frequency,
            columns=[
                'timestamp',
                'device_id',
                'cpu',
                'value',
                'elapsed'
            ]
        ).set_index(['timestamp', 'device_id', 'cpu'])