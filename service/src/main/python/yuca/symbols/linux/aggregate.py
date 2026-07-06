import logging

from yuca.signal_pb2 import Signal
from yuca.symbols.symbol import SOCKET_POWER, SOCKET_PACKAGE_POWER, SOCKET_DRAM_POWER
from yuca.symbols.symbol import SOCKET_OPERATIONAL_EMISSIONS, SOCKET_PACKAGE_OPERATIONAL_EMISSIONS, SOCKET_DRAM_OPERATIONAL_EMISSIONS
from yuca.symbols.symbol import CPU_FREQUENCY, CPU_AMORTIZED_EMISSIONS, SOCKET_TEMPERATURE, DRAM_AMORTIZED_EMISSIONS
from yuca.symbols.symbol import TASK_POWER, TASK_OPERATIONAL_EMISSIONS, TASK_PACKAGE_OPERATIONAL_EMISSIONS, TASK_DRAM_OPERATIONAL_EMISSIONS
from yuca.symbols.symbol import DISK_POWER, DISK_OPERATIONAL_EMISSIONS, DISK_AMORTIZED_EMISSIONS

from yuca.symbols.linux.socket import *
from yuca.symbols.linux.disk import *
from yuca.symbols.linux.amortized import compute_amortized_carbon, compute_straight_line_amortized_carbon


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="yuca-processing (%(asctime)s) [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %p %Z",
    level=logging.DEBUG,
)

# maps component type + unit to processing
PROCESSORS = {
    ('linux_system', Signal.Unit.JOULES): [
        SystemEnergyProcessor(),
        SystemPackagePowerProcessor(),
        SystemDramPowerProcessor(),
    ],
    ('linux_system', Signal.Unit.GRAMS_OF_CO2): [
        SystemEmissionsProcessor(),
        SystemPackageEmissionsProcessor(),
        SystemDramEmissionsProcessor(),
    ],
    ('linux_system_disk', Signal.Unit.JOULES): [SystemDiskPowerProcessor()],
    ('linux_system_disk', Signal.Unit.GRAMS_OF_CO2): [SystemDiskEmissionsProcessor()],
    ('linux_system', Signal.Unit.HERTZ): [SystemFrequencyProcessor()],
    ('linux_system', Signal.Unit.CELSIUS): [SystemTemperatureProcessor()],
    ('linux_process', Signal.Unit.JOULES): [TaskEnergyProcessor()],
    ('linux_process', Signal.Unit.GRAMS_OF_CO2): [
        TaskEmissionsProcessor(),
        TaskPackageEmissionsProcessor(),
        TaskDramEmissionsProcessor(),
    ],
}


dram_lifespan = 157680000
dram_embodied_carbon = 512 * 0.29 * 1000

ssd_lifespan = 157680000
ssd_embodied_carbon =  2143 * 0.16 * 100

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
            ctype_old = ctype
            if source == '/sys/class/block' or source == '/sys/class/block+USA':
                ctype = ctype + '_disk'
            if (ctype, unit) in PROCESSORS:
                processors = PROCESSORS[ctype, unit]

                for processor in processors:
                    logger.info(
                        ' - Processing with %s',
                        type(processor)
                    )
                    symbol, df = processor.process(signal)
                    symbols['data'][symbol] = df
            ctype = ctype_old

    if SOCKET_TEMPERATURE in symbols['data'] and CPU_FREQUENCY in symbols['data']:
        logger.info('Adding new signal amortized emissions (GRAMS_OF_CO2)')
        symbols['data'][CPU_AMORTIZED_EMISSIONS] = compute_amortized_carbon(
            symbols['data'][SOCKET_TEMPERATURE],
            symbols['data'][CPU_FREQUENCY],
            # TODO: need system specs to abstract this
            35,
            1800000000
        )

    if SOCKET_POWER in symbols['data']:
        logger.info('Adding new signal dram amortized emissions (GRAMS_OF_CO2)')
        symbols['data'][DRAM_AMORTIZED_EMISSIONS] = compute_straight_line_amortized_carbon(
            symbols['data'][SOCKET_POWER],
            # TODO: need system specs to abstract this
            dram_lifespan,
            dram_embodied_carbon
        )

    if DISK_POWER in symbols['data']:
        logger.info('Adding new signal disk amortized emissions (GRAMS_OF_CO2)')
        symbols['data'][DISK_AMORTIZED_EMISSIONS] = compute_straight_line_amortized_carbon(
            symbols['data'][DISK_POWER],
            # TODO: need system specs to abstract this
            ssd_lifespan,
            ssd_embodied_carbon
        )
    return symbols


def aggregate_symbols(symbols):
    agg_symbols = {}
    agg_symbols['data'] = {}
    agg_symbols['metadata'] = symbols['metadata']
    for symbol in symbols['data']:
        df = symbols['data'][symbol].groupby([
            'timestamp',
            'device_id'
        ]).sum().reset_index()
        # TODO: Should really check if symbol in SOCKET_TEMPERATURE instead
        if symbol in [
            SOCKET_POWER,
            SOCKET_PACKAGE_POWER,
            SOCKET_DRAM_POWER,
            CPU_FREQUENCY,
            SOCKET_OPERATIONAL_EMISSIONS,
            SOCKET_PACKAGE_OPERATIONAL_EMISSIONS,
            SOCKET_DRAM_OPERATIONAL_EMISSIONS,
            CPU_AMORTIZED_EMISSIONS,
            TASK_POWER,
            TASK_OPERATIONAL_EMISSIONS,
            TASK_PACKAGE_OPERATIONAL_EMISSIONS,
            TASK_DRAM_OPERATIONAL_EMISSIONS,
            DISK_POWER,
            DISK_OPERATIONAL_EMISSIONS,
            DISK_AMORTIZED_EMISSIONS,
            DRAM_AMORTIZED_EMISSIONS,
        ]:
            df['value'] *= df['elapsed']
        else:
            print(f"Symbol {symbol} is not in the table")

        agg_symbols['data'][symbol] = df.groupby('device_id').agg({
            'value': ('mean', 'median', 'sum', 'std')
        })
        timestamps = df.groupby('device_id').agg({
            'timestamp': 'min',
            'elapsed': 'sum'
        })
        agg_symbols['data'][symbol].columns = [
            'mean',
            'median',
            'sum',
            'std'
        ]
        agg_symbols['data'][symbol]['start'] = timestamps['timestamp']
        agg_symbols['data'][symbol]['end'] = timestamps['timestamp'] + \
            (timestamps['elapsed'] * 1e9).astype('int')
        agg_symbols['data'][symbol]['elapsed'] = agg_symbols['data'][symbol]['end'] - \
            agg_symbols['data'][symbol]['start']
    return agg_symbols
