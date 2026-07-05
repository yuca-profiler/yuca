# import logging

# import numpy as np
# import pandas as pd
# import scipy as sp

# from yuca.signal_pb2 import Signal
# from yuca.symbols.symbol import SOCKET_POWER, SOCKET_PACKAGE_POWER, SOCKET_DRAM_POWER
# from yuca.symbols.symbol import SOCKET_OPERATIONAL_EMISSIONS, SOCKET_PACKAGE_OPERATIONAL_EMISSIONS, SOCKET_DRAM_OPERATIONAL_EMISSIONS
# from yuca.symbols.symbol import CPU_FREQUENCY, CPU_AMORTIZED_EMISSIONS, SOCKET_TEMPERATURE, DRAM_AMORTIZED_EMISSIONS
# from yuca.symbols.symbol import TASK_POWER, TASK_OPERATIONAL_EMISSIONS, TASK_PACKAGE_OPERATIONAL_EMISSIONS, TASK_DRAM_OPERATIONAL_EMISSIONS
# from yuca.symbols.symbol import DISK_POWER, DISK_OPERATIONAL_EMISSIONS, DISK_AMORTIZED_EMISSIONS
# from yuca.symbols.unit import SocketComponentKind

# logger = logging.getLogger(__name__)
# logging.basicConfig(
#     format="yuca-processing (%(asctime)s) [%(name)s]: %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S %p %Z",
#     level=logging.DEBUG,
# )


# class SignalProcessor:
#     def process(self, signal):
#         return self.index, self._process_internal(signal)

#     def _process_internal(self, signal):
#         pass


# class SystemEnergyProcessor(SignalProcessor):
#     index = SOCKET_POWER

#     def _process_internal(self, signal):
#         power = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000

#             total_value = 0
#             socket = None
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 total_value += data.value
#                 socket = int(metadata['socket'])
#             power.append([
#                 start,
#                 f"socket:{socket}",
#                 total_value / elapsed,
#                 elapsed
#             ])
#         return pd.DataFrame(
#             data=power,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id'])


# class SystemPackagePowerProcessor(SignalProcessor):
#     index = SOCKET_PACKAGE_POWER

#     def _process_internal(self, signal):
#         power = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 component = metadata['component'].upper()

#                 if component not in SocketComponentKind.__members__:
#                     logger.info(
#                         '%s is not a supported SocketComponentKind', component)
#                     continue
#                 if component != SocketComponentKind.PACKAGE.name:
#                     continue
#                 power.append([
#                     start,
#                     f"socket:{int(metadata['socket'])}",
#                     metadata['component'],
#                     data.value / elapsed,
#                     elapsed
#                 ])
#         return pd.DataFrame(
#             data=power,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'component',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'component'])


# class SystemDramPowerProcessor(SignalProcessor):
#     index = SOCKET_DRAM_POWER

#     def _process_internal(self, signal):
#         power = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 component = metadata['component'].upper()
#                 if component not in SocketComponentKind.__members__:
#                     logger.info(
#                         '%s is not a supported SocketComponentKind', component)
#                     continue
#                 if component != SocketComponentKind.DRAM.name:
#                     continue
#                 power.append([
#                     start,
#                     f"socket:{int(metadata['socket'])}",
#                     metadata['component'],
#                     data.value / elapsed,
#                     elapsed
#                 ])
#         return pd.DataFrame(
#             data=power,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'component',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'component'])


# class SystemDiskPowerProcessor(SignalProcessor):
#     index = DISK_POWER

#     def _process_internal(self, signal):
#         power = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'device' not in metadata:
#                     continue
#                 power.append([
#                     start,
#                     metadata['device'],
#                     metadata['model'],
#                     data.value / elapsed,
#                     elapsed
#                 ])
#         return pd.DataFrame(
#             data=power,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'model',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'model'])


# class SystemEmissionsProcessor(SignalProcessor):
#     index = SOCKET_OPERATIONAL_EMISSIONS

#     def _process_internal(self, signal):
#         emissions = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000

#             total_value = 0
#             socket = None
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 total_value += data.value
#                 socket = int(metadata['socket'])
#             emissions.append([
#                 start,
#                 f"socket:{socket}",
#                 total_value / elapsed,
#                 elapsed
#             ])
#         return pd.DataFrame(
#             data=emissions,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id'])


# class SystemPackageEmissionsProcessor(SignalProcessor):
#     index = SOCKET_PACKAGE_OPERATIONAL_EMISSIONS

#     def _process_internal(self, signal):
#         emissions = []
#         component = None
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 component = metadata['component'].upper()
#                 if component not in SocketComponentKind.__members__:
#                     logger.info(
#                         '%s is not a supported SocketComponentKind', component)
#                     continue
#                 if component != SocketComponentKind.PACKAGE.name:
#                     continue
#                 emissions.append([
#                     start,
#                     f"socket:{int(metadata['socket'])}",
#                     metadata['component'],
#                     data.value / elapsed,
#                     elapsed
#                 ])
#         return pd.DataFrame(
#             data=emissions,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'component',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'component'])


# class SystemDramEmissionsProcessor(SignalProcessor):
#     index = SOCKET_DRAM_OPERATIONAL_EMISSIONS

#     def _process_internal(self, signal):
#         emissions = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 component = metadata['component'].upper()
#                 if component not in SocketComponentKind.__members__:
#                     logger.info(
#                         '%s is not a supported SocketComponentKind', component)
#                     continue
#                 if component != SocketComponentKind.DRAM.name:
#                     continue
#                 emissions.append([
#                     start,
#                     f"socket:{int(metadata['socket'])}",
#                     metadata['component'],
#                     data.value / elapsed,
#                     elapsed,
#                 ])
#         return pd.DataFrame(
#             data=emissions,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'component',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'component'])


# class SystemDiskEmissionsProcessor(SignalProcessor):
#     index = DISK_OPERATIONAL_EMISSIONS

#     def _process_internal(self, signal):
#         emissions = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'device' not in metadata:
#                     continue
#                 emissions.append([
#                     start,
#                     metadata['device'],
#                     metadata['model'],
#                     data.value / elapsed,
#                     elapsed
#                 ])
#         return pd.DataFrame(
#             data=emissions,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'model',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'model'])


# class SystemTemperatureProcessor(SignalProcessor):
#     index = SOCKET_TEMPERATURE

#     def _process_internal(self, signal):
#         temperature = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if metadata['kind'] != 'X86_PKG_TEMP':
#                     continue
#                 temperature.append([
#                     start,
#                     f"socket:{int(metadata['socket'])}",
#                     data.value,
#                     elapsed
#                 ])
#         return pd.DataFrame(
#             data=temperature,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id'])


# class SystemFrequencyProcessor(SignalProcessor):
#     index = CPU_FREQUENCY

#     def _process_internal(self, signal):
#         frequency = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if metadata['kind'] != 'observed':
#                     continue
#                 frequency.append([
#                     start,
#                     f"socket:{int(metadata['socket'])}",
#                     int(metadata['cpu']),
#                     data.value,
#                     elapsed
#                 ])
#         return pd.DataFrame(
#             data=frequency,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'cpu',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'cpu'])


# class TaskEnergyProcessor(SignalProcessor):
#     index = TASK_POWER

#     def _process_internal(self, signal):
#         power = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             # for data in interval.data:
#             #     metadata = {m.name: m.value for m in data.metadata}
#             #     power.append([
#             #         start,
#             #         f"socket:{int(metadata['socket'])}",
#             #         int(metadata['cpu']),
#             #         int(metadata['task']),
#             #         metadata['component'],
#             #         data.value / elapsed,
#             #         elapsed
#             #     ])
#             total_value = 0
#             socket = None
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 total_value += data.value
#                 socket = int(metadata['socket'])
#             power.append([
#                 start,
#                 f"socket:{socket}",
#                 int(metadata['cpu']),
#                 int(metadata['task']),
#                 total_value / elapsed,
#                 elapsed
#             ])
#         return pd.DataFrame(
#             data=power,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'cpu',
#                 'task',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'cpu', 'task'])


# class TaskEmissionsProcessor(SignalProcessor):
#     index = TASK_OPERATIONAL_EMISSIONS

#     def _process_internal(self, signal):
#         emissions = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             # for data in interval.data:
#             #     metadata = {m.name: m.value for m in data.metadata}
#             #     emissions.append([
#             #         start,
#             #         f"socket:{int(metadata['socket'])}",
#             #         int(metadata['cpu']),
#             #         int(metadata['task']),
#             #         metadata['component'],
#             #         data.value / elapsed,
#             #         elapsed
#             #     ])
#             total_value = 0
#             socket = None
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 total_value += data.value
#                 socket = int(metadata['socket'])
#             emissions.append([
#                 start,
#                 f"socket:{socket}",
#                 int(metadata['cpu']),
#                 int(metadata['task']),
#                 total_value / elapsed,
#                 elapsed
#             ])
#         return pd.DataFrame(
#             data=emissions,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'cpu',
#                 'task',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'cpu', 'task'])

# class TaskPackageEmissionsProcessor(SignalProcessor):
#     index = TASK_PACKAGE_OPERATIONAL_EMISSIONS

#     def _process_internal(self, signal):
#         emissions = []
#         component = None
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             '''
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 component = metadata['component'].upper()
#                 if component not in SocketComponentKind.__members__:
#                     logger.info(
#                         '%s is not a supported SocketComponentKind', component)
#                     continue
#                 if component != SocketComponentKind.PACKAGE.name:
#                     continue
#                 emissions.append([
#                     start,
#                     f"socket:{int(metadata['socket'])}",
#                     metadata['component'],
#                     data.value / elapsed,
#                     elapsed
#                 ])
#                 '''
#             total_value = 0
#             socket = None
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 component = metadata['component'].upper()
#                 if component not in SocketComponentKind.__members__:
#                     logger.info(
#                         '%s is not a supported SocketComponentKind', component)
#                     continue
#                 if component != SocketComponentKind.PACKAGE.name:
#                     continue
#                 total_value += data.value
#                 socket = int(metadata['socket'])
#             emissions.append([
#                 start,
#                 f"socket:{socket}",
#                 int(metadata['cpu']),
#                 int(metadata['task']),
#                 total_value / elapsed,
#                 elapsed
#             ])
#         return pd.DataFrame(
#             data=emissions,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'cpu',
#                 'task',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'cpu', 'task'])


# class TaskDramEmissionsProcessor(SignalProcessor):
#     index = TASK_DRAM_OPERATIONAL_EMISSIONS

#     def _process_internal(self, signal):
#         emissions = []
#         for interval in signal.interval:
#             start = 1000000000 * interval.start.secs + interval.start.nanos
#             end = 1000000000 * interval.end.secs + interval.end.nanos
#             elapsed = (end - start) / 1000000000
#             '''
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 component = metadata['component'].upper()
#                 if component not in SocketComponentKind.__members__:
#                     logger.info(
#                         '%s is not a supported SocketComponentKind', component)
#                     continue
#                 if component != SocketComponentKind.DRAM.name:
#                     continue
#                 emissions.append([
#                     start,
#                     f"socket:{int(metadata['socket'])}",
#                     metadata['component'],
#                     data.value / elapsed,
#                     elapsed,
#                 ])'''
#             total_value = 0
#             socket = None
#             for data in interval.data:
#                 metadata = {m.name: m.value for m in data.metadata}
#                 if 'component' not in metadata:
#                     continue
#                 component = metadata['component'].upper()
#                 if component not in SocketComponentKind.__members__:
#                     logger.info(
#                         '%s is not a supported SocketComponentKind', component)
#                     continue
#                 if component != SocketComponentKind.DRAM.name:
#                     continue
#                 total_value += data.value
#                 socket = int(metadata['socket'])
#             emissions.append([
#                 start,
#                 f"socket:{socket}",
#                 int(metadata['cpu']),
#                 int(metadata['task']),
#                 total_value / elapsed,
#                 elapsed
#             ])
#         return pd.DataFrame(
#             data=emissions,
#             columns=[
#                 'timestamp',
#                 'device_id',
#                 'cpu',
#                 'task',
#                 'value',
#                 'elapsed'
#             ]
#         ).set_index(['timestamp', 'device_id', 'cpu', 'task'])


# # boltzmann's constant in eV/K
# k_b, _, _ = sp.constants.physical_constants['Boltzmann constant in eV/K']
# # poisson parameter for trap distribution in eV nm/V
# B = 0.075
# # transistor channel energy in eV
# E_0 = 0.1897
# # supply voltage in V
# v_dd = 0.070
# # equivalent oxide thickness in nm
# t_ox = 0.9
# # Transistor gap temperature
# T = -(B * v_dd / t_ox - E_0) / k_b

# # TODO: Need to be customizable based on device
# # lifespan is 10 years in seconds
# # embodied_carbon is in grams
# cpu_lifespan = 315360000
# cpu_embodied_carbon = 10274.2


# def compute_amortized_carbon(temperature, frequency, normal_temperature, normal_frequency):
#     """
#     This code is not fully tested but appears to work as expected based on this script:

#     from itertools import product

#     import math
#     import pandas as pd
#     import numpy as np

#     from yuca.symbols.linux import compute_amortized_carbon

#     freq_index = pd.MultiIndex.from_tuples(
#         product([1767403714251088000, 1767403714251088010],
#                 list(range(2)), list(range(9))),
#         names=["timestamp", "socket", "cpu"]
#     )

#     freq = pd.Series(
#         [10e9] * len(freq_index),
#         index=freq_index,
#         name="value"
#     )

#     temp_index = pd.MultiIndex.from_tuples(
#         product([1767403714251088005, 1767403714251088015], list(range(2))),
#         names=["timestamp", "socket"]
#     )

#     temp = pd.Series(
#         [37] * len(temp_index),
#         index=temp_index,
#         name="value"
#     )

#     result = compute_amortized_carbon(temp, freq, 40, 1800000000)
#     assert math.isclose(
#         result.sum(),
#         0.000181 * len(result),
#         rel_tol=1e-4
#     )
#     """
#     norm = temperature.copy(deep=True)
#     norm[norm > normal_temperature] = normal_temperature
#     # e^(T/temp) / e^(T/normal temp) = e^(T/temp - T/normal temp) = e^(T * (1 /temp - 1/normal temp))
#     # Temperature must be in Kelvin for aging to prevent unit mismatch
#     age = np.exp(
#         T * (1 / (273 + temperature['value']) - 1 / (273 + norm['value'])))
#     # age = pd.DataFrame({
#     #     'value': age_func,
#     #     'elapsed': norm['elapsed']
#     # })

#     df = pd.concat(
#         [frequency['value'].unstack('cpu'), age],
#         axis=1
#     )
#     # print(frequency['value'].unstack('cpu'))

#     dfs = []
#     for _, df in df.groupby('device_id'):
#         df = df.sort_index()
#         # elapsed = df.pop('elapsed')
#         # print('inside groby')
#         # print(df)
#         df = df.ffill().dropna(axis=1, how='all').dropna(axis=0)
#         age = df.pop('value')
#         count = df.shape[1]
#         for col in df.columns:
#             norm = df[col].copy(deep=True)
#             norm[norm > normal_frequency] = normal_frequency
#             df[col] = (age * df[col] / norm) * \
#                 (cpu_embodied_carbon / count / cpu_lifespan)
#         df.columns.name = 'cpu'
#         df = df.stack().to_frame(name='value')
#         # important because value is indexed by cpu rn
#         df = df.groupby(['timestamp', 'device_id'])['value'].sum().to_frame()
#         df['elapsed'] = df.reset_index().groupby('device_id')['timestamp'].diff().values / 1e9
#         df = df.dropna()
#         dfs.append(df)
#     amortized = pd.concat(dfs)
#     amortized.name = 'value'

#     return amortized


# # TODO: Need to be customizable based on device
# # lifespan is 5 years in seconds
# # embodied_carbon is in grams
# dram_lifespan = 157680000
# dram_embodied_carbon = 4750

# # lifespan is 3.5 years in seconds
# # embodied_carbon is in grams
# hdd_lifespan = 110376000
# hdd_embodied_carbon = 22440

# def compute_straight_line_amortized_carbon(power, lifespan, embodied_carbon):
#     # straight line amortization
#     df = power.copy()
#     rate = embodied_carbon / lifespan
#     df['value'] = rate
#     return df


# # maps component type + unit to processing
# PROCESSORS = {
#     ('linux_system', Signal.Unit.JOULES): [
#         SystemEnergyProcessor(),
#         SystemPackagePowerProcessor(),
#         SystemDramPowerProcessor(),
#     ],
#     ('linux_system', Signal.Unit.GRAMS_OF_CO2): [
#         SystemEmissionsProcessor(),
#         SystemPackageEmissionsProcessor(),
#         SystemDramEmissionsProcessor(),
#     ],
#     ('linux_system_disk', Signal.Unit.JOULES): [SystemDiskPowerProcessor()],
#     ('linux_system_disk', Signal.Unit.GRAMS_OF_CO2): [SystemDiskEmissionsProcessor()],
#     ('linux_system', Signal.Unit.HERTZ): [SystemFrequencyProcessor()],
#     ('linux_system', Signal.Unit.CELSIUS): [SystemTemperatureProcessor()],
#     ('linux_process', Signal.Unit.JOULES): [TaskEnergyProcessor()],
#     ('linux_process', Signal.Unit.GRAMS_OF_CO2): [
#         TaskEmissionsProcessor(),
#         TaskPackageEmissionsProcessor(),
#         TaskDramEmissionsProcessor(),
#     ],
# }


# def extract_linux_symbols(report):
#     symbols = {}
#     symbols['metadata'] = {m.name: m.value for m in report.metadata}
#     symbols['data'] = {}
#     for component in report.component:
#         ctype = component.component_type
#         cid = component.component_id
#         logger.info('Processing component %s (%s)', ctype, cid)
#         # component contains component_type, component_id, and Signal obj:
#         for signal in component.signal:
#             source = '+'.join(signal.source)
#             unit = signal.unit
#             unit_name = Signal.Unit.DESCRIPTOR.values_by_number[signal.unit].name
#             logger.info(' - Processing signal %s (%s)', source, unit_name)
#             ctype_old = ctype
#             if source == '/sys/class/block' or source == '/sys/class/block+USA':
#                 ctype = ctype + '_disk'
#             if (ctype, unit) in PROCESSORS:
#                 processors = PROCESSORS[ctype, unit]

#                 for processor in processors:
#                     logger.info(
#                         ' - Processing with %s',
#                         type(processor)
#                     )
#                     symbol, df = processor.process(signal)
#                     symbols['data'][symbol] = df
#             ctype = ctype_old

#     if SOCKET_TEMPERATURE in symbols['data'] and CPU_FREQUENCY in symbols['data']:
#         logger.info('Adding new signal amortized emissions (GRAMS_OF_CO2)')
#         symbols['data'][CPU_AMORTIZED_EMISSIONS] = compute_amortized_carbon(
#             symbols['data'][SOCKET_TEMPERATURE],
#             symbols['data'][CPU_FREQUENCY],
#             # TODO: need system specs to abstract this
#             35,
#             1800000000
#         )

#     if SOCKET_POWER in symbols['data']:
#         logger.info('Adding new signal dram amortized emissions (GRAMS_OF_CO2)')
#         symbols['data'][DRAM_AMORTIZED_EMISSIONS] = compute_straight_line_amortized_carbon(
#             symbols['data'][SOCKET_POWER],
#             # TODO: need system specs to abstract this
#             dram_lifespan,
#             dram_embodied_carbon
#         )

#     if DISK_POWER in symbols['data']:
#         logger.info('Adding new signal disk amortized emissions (GRAMS_OF_CO2)')
#         symbols['data'][DISK_AMORTIZED_EMISSIONS] = compute_straight_line_amortized_carbon(
#             symbols['data'][DISK_POWER],
#             # TODO: need system specs to abstract this
#             hdd_lifespan,
#             hdd_embodied_carbon
#         )
#     return symbols


# def aggregate_symbols(symbols):
#     agg_symbols = {}
#     agg_symbols['data'] = {}
#     agg_symbols['metadata'] = symbols['metadata']
#     # print("printing symbol")
#     # print(symbols['data'][CPU_FREQUENCY])
#     for symbol in symbols['data']:
#         # df  = symbols['data'][symbol].reset_index()
#         df = symbols['data'][symbol].groupby([
#             'timestamp',
#             'device_id'
#         ]).sum().reset_index()
#         # Should really check if symbol in SOCKET_TEMPERATURE instead
#         if symbol in [
#             SOCKET_POWER,
#             SOCKET_PACKAGE_POWER,
#             SOCKET_DRAM_POWER,
#             CPU_FREQUENCY,
#             SOCKET_OPERATIONAL_EMISSIONS,
#             SOCKET_PACKAGE_OPERATIONAL_EMISSIONS,
#             SOCKET_DRAM_OPERATIONAL_EMISSIONS,
#             CPU_AMORTIZED_EMISSIONS,
#             TASK_POWER,
#             TASK_OPERATIONAL_EMISSIONS,
#             TASK_PACKAGE_OPERATIONAL_EMISSIONS,
#             TASK_DRAM_OPERATIONAL_EMISSIONS,
#             DISK_POWER,
#             DISK_OPERATIONAL_EMISSIONS,
#             DISK_AMORTIZED_EMISSIONS,
#             DRAM_AMORTIZED_EMISSIONS,
#         ]:
#             df['value'] *= df['elapsed']
#             # df.value *= df.groupby('device_id')['timestamp'].diff() / 1e9
#             # df = df.dropna()
#         else:
#             print(f"Symbol {symbol} is not in the table")
#             # print("resetting index")
#             # df = df.reset_index()
#         agg_symbols['data'][symbol] = df.groupby('device_id').agg({
#             'value': ('mean', 'median', 'sum', 'std')
#         })
#         timestamps = df.groupby('device_id').agg({
#             'timestamp': 'min',
#             'elapsed': 'sum'
#         })
#         agg_symbols['data'][symbol].columns = [
#             'mean',
#             'median',
#             'sum',
#             'std'
#         ]
#         agg_symbols['data'][symbol]['start'] = timestamps['timestamp']
#         agg_symbols['data'][symbol]['end'] = timestamps['timestamp'] + \
#             (timestamps['elapsed'] * 1e9).astype('int')
#         agg_symbols['data'][symbol]['elapsed'] = agg_symbols['data'][symbol]['end'] - \
#             agg_symbols['data'][symbol]['start']
#     return agg_symbols
