import pandas as pd

from yuca.signal_pb2 import Signal
from yuca.symbols.symbol import SOCKET_POWER, SOCKET_PACKAGE_POWER, SOCKET_DRAM_POWER
from yuca.symbols.symbol import SOCKET_OPERATIONAL_EMISSIONS, SOCKET_PACKAGE_OPERATIONAL_EMISSIONS, SOCKET_DRAM_OPERATIONAL_EMISSIONS
from yuca.symbols.symbol import CPU_FREQUENCY, CPU_AMORTIZED_EMISSIONS, SOCKET_TEMPERATURE, DRAM_AMORTIZED_EMISSIONS
from yuca.symbols.symbol import TASK_POWER, TASK_OPERATIONAL_EMISSIONS, TASK_PACKAGE_OPERATIONAL_EMISSIONS, TASK_DRAM_OPERATIONAL_EMISSIONS
from yuca.symbols.symbol import DISK_POWER, DISK_OPERATIONAL_EMISSIONS, DISK_AMORTIZED_EMISSIONS

from yuca.symbols.unit import SocketComponentKind
from yuca.symbols.processor import SignalProcessor, interval_bounds, get_metadata

class DiskProcessor(SignalProcessor):

    def _process_internal(self, signal):
        rows = []
        for interval in signal.interval:
            start, elapsed = interval_bounds(interval)
            for data in interval.data:
                metadata = get_metadata(data)
                if 'device' not in metadata:
                    continue
                rows.append([
                    start,
                    metadata['device'],
                    metadata['model'],
                    data.value / elapsed,
                    elapsed,
                ])
        return pd.DataFrame(
            data=rows,
            columns=[
                'timestamp',
                'device_id',
                'model',
                'value',
                'elapsed'
            ]
        ).set_index(['timestamp', 'device_id', 'model'])

class SystemDiskPowerProcessor(DiskProcessor):
    index = DISK_POWER
 
class SystemDiskEmissionsProcessor(DiskProcessor):
    index = DISK_OPERATIONAL_EMISSIONS