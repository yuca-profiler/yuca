import os

from argparse import ArgumentParser

import numpy as np
import pandas as pd
import scipy as sp

from tqdm import tqdm

# import warnings

# from pandas.core.common import SettingWithCopyWarning

# warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

pd.set_option('mode.chained_assignment', None)
# This code will not complain!
pd.reset_option("mode.chained_assignment")

# boltzmann's constant in eV/K
k_b, _, _ = sp.constants.physical_constants['Boltzmann constant in eV/K']
# poisson parameter for trap distribution in eV nm/V
B = 0.075
# transistor channel energy in eV
E_0 = 0.1897
# supply voltage in V
v_dd = 0.070
# equivalent oxide thickness in nm
t_ox = 0.9
# Transistor gap temperature
T = -(B * v_dd / t_ox - E_0) / k_b

# TODO: Need to be customizable based on device
# lifespan is 5 years in seconds
# embodied_carbon is in grams
cpu_lifespan = 157680000
# 7.3 kg per die
cpu_embodied_carbon=7300

# 101.1 kg per gpu
# 3 years in seconds
gpu_lifespan = 94608000
gpu_embodied_carbon=101100

def compute_amortized_carbon(temperature, frequency, normal_temperature, normal_frequency, lifespan, embodied_carbon):
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
        count = df.shape[1]
        for col in df.columns:
            norm = df[col].copy(deep=True)
            norm[norm > normal_frequency] = normal_frequency
            df[col] = (age * df[col] / norm) * \
                (embodied_carbon / count / lifespan)

        df.columns.name = 'cpu'
        df = df.stack().rename('value').reset_index()
        df = df.groupby(['timestamp', 'socket'])['value'].sum().to_frame()
        df['elapsed'] = df.reset_index().groupby('socket')['timestamp'].diff().values / 1e9
        df = df.dropna()
        dfs.append(df)
    amortized = pd.concat(dfs)
    amortized.name = 'value'
    amortized['carbon'] = amortized['value'] * amortized['elapsed']
    return amortized.reset_index()[['timestamp', 'socket', 'carbon']].rename(columns={'carbon': 'value'})

def parse_metadata(s):
    return dict(item.split('=', 1) for item in s.split(';'))

def summarize(df):
    summary = []

    carbon = df[df.unit == 'GRAMS_OF_CO2']
    runtime = carbon[(carbon.component_type == 'nvml') & (carbon.source == 'nvmlDeviceGetTotalEnergyConsumption') & (carbon.metadata == 'device=0')]
    runtime = (runtime.end - runtime.start).sum() / 1e9

    summary.append(pd.Series({
        'component_type': 'all',
        'signal': 'runtime',
        'value': runtime,
    }).to_frame().T)

    package = carbon[carbon.metadata.str.contains('package').fillna(False)]
    s = package.groupby(['component_type']).value.sum().to_frame().reset_index()
    s['signal'] = 'cpu_package_carbon'
    summary.append(s)

    
    dram = carbon[carbon.metadata.str.contains('dram').fillna(False)]
    s = dram.groupby(['component_type']).value.sum().to_frame().reset_index()
    s['signal'] = 'cpu_dram_carbon'
    summary.append(s)
    
    
    temp = df[df.unit == 'CELSIUS']
    freqs = df[df.unit == 'HERTZ']

    cpu_temp = temp[temp.component_type == 'linux_system']
    temp_meta = cpu_temp['metadata'].apply(parse_metadata)
    cpu_temp = cpu_temp[cpu_temp.metadata.str.contains(
        'X86_PKG_TEMP').fillna(False)]
    cpu_temp['socket'] = temp_meta.str['socket'].astype(int)
    
    cpu_freqs = freqs[freqs.component_type == 'linux_system']
    meta = cpu_freqs['metadata'].apply(parse_metadata)
    cpu_freqs['cpu'] = meta.str['cpu'].astype(int)
    cpu_freqs['socket'] = meta.str['socket'].astype(int)
    cpu_freqs = cpu_freqs.drop_duplicates(['start', 'cpu'])

    all_amortized = []

    for socket in sorted(cpu_temp['socket'].unique()):
        cpu_temp_i = cpu_temp[cpu_temp['socket'] == socket].copy()
        cpu_freqs_i = cpu_freqs[cpu_freqs['socket'] == socket].copy()

        cpu_temp_i = cpu_temp_i[['start', 'socket', 'value']]
        cpu_temp_i['timestamp'] = cpu_temp_i['start']
        cpu_temp_i = cpu_temp_i.set_index(['timestamp', 'socket']).value

        cpu_freqs_i = cpu_freqs_i[['start', 'cpu', 'socket', 'value']]
        cpu_freqs_i['timestamp'] = cpu_freqs_i['start']
        cpu_freqs_i = cpu_freqs_i.groupby(['timestamp', 'cpu', 'socket']).value.max()

        amortized = compute_amortized_carbon(
            cpu_temp_i,
            cpu_freqs_i,
            48,
            1.6e9,
            cpu_lifespan,
            cpu_embodied_carbon,
        )

        amortized['signal'] = f'cpu_amortized_carbon:socket={socket}'
        amortized['component_type'] = 'linux_system'

        all_amortized.append(amortized)

        summary.append(
            amortized.groupby(['signal', 'component_type'])
                    .value.sum()
                    .reset_index()
        )

    cpu_amortized_sum = (
        pd.concat(all_amortized)
            .groupby(['timestamp', 'socket'], as_index=False)
            .agg({'value': 'sum'})
    )

    cpu_amortized_sum['signal'] = 'cpu_amortized_sum'
    cpu_amortized_sum['component_type'] = 'linux_system'

    summary.append(
        cpu_amortized_sum.groupby(['signal', 'component_type'])
                        .value.sum()
                        .reset_index()
    )

    # cpu_temp = cpu_temp[['start', 'socket', 'value']]
    # cpu_temp['timestamp'] = cpu_temp['start']
    # cpu_temp = cpu_temp.set_index(['timestamp', 'socket']).value

    # cpu_freqs = cpu_freqs[['start', 'cpu', 'socket', 'value']]
    # cpu_freqs['timestamp'] = cpu_freqs['start']
    # cpu_freqs = cpu_freqs.groupby(['timestamp', 'cpu', 'socket']).value.max()

    # # amortized = compute_amortized_carbon(cpu_temp, cpu_freqs, 35, 1.6 * 10**9).to_frame()
    # amortized = compute_amortized_carbon(cpu_temp, cpu_freqs, 48, 1.6 * 10**9, cpu_lifespan, cpu_embodied_carbon)
    # amortized['signal']='cpu_amortized_carbon'
    # amortized['component_type']='linux_system'
    # s = amortized.groupby(['signal', 'component_type']).value.sum().to_frame().reset_index()
    # summary.append(s)
    
    # GPU
    gpu_op=carbon[(carbon.component_type == 'nvml') & (carbon.source == 'nvmlDeviceGetTotalEnergyConsumption')]
    gpu_op['signal']='gpu_carbon'
    gpu_op['component_type']='nvml'
    s=gpu_op.groupby(['signal', 'component_type']).value.sum().to_frame().reset_index()
    summary.append(s)
    
    
    temp=df[df.unit == 'CELSIUS']
    freqs=df[df.unit == 'HERTZ']

    gpu_temp=temp[temp.component_type == 'nvml']
    gpu_temp['socket']=0
    # TODO: Fix nvml sampling factor on HPCs
    gpu_temp['value']*=1000

    gpu_freqs=freqs[freqs.component_type == 'nvml'].copy()

    gpu_freqs['cpu']=0
    gpu_freqs['socket']=0

    all_amortized = []
    for metadata in gpu_temp['metadata'].unique():
        gpu_temp_i = gpu_temp[gpu_temp['metadata'] == metadata].copy()
        gpu_temp_i = gpu_temp_i[['start', 'socket', 'value']]
        gpu_temp_i['timestamp'] = gpu_temp_i['start']
        gpu_temp_i = gpu_temp_i.set_index(['timestamp', 'socket']).value

        gpu_freqs_i = gpu_freqs[['start', 'cpu', 'socket', 'value']].copy()
        gpu_freqs_i['timestamp'] = gpu_freqs_i['start']
        gpu_freqs_i = gpu_freqs_i.groupby(['timestamp', 'cpu', 'socket']).value.max()

        amortized=compute_amortized_carbon(gpu_temp_i, gpu_freqs_i, 40, 1.6 * 10**9, gpu_lifespan, gpu_embodied_carbon)

        amortized['component_type'] = 'nvml'
        amortized['signal'] = f'gpu_amortized_carbon:{metadata}'

        all_amortized.append(amortized)

        s=amortized.groupby(['signal', 'component_type']).value.sum().to_frame().reset_index()
        summary.append(s)

    # Sum across all GPUs
    gpu_amortized_sum = (
        pd.concat(all_amortized)
        .groupby(['timestamp', 'socket'], as_index=False)
        .agg({
            'value': 'sum',
            'component_type': 'first',
            'signal': 'first'
        })
    )
    gpu_amortized_sum['signal'] = 'gpu_amortized_carbon'
    summary.append(
        gpu_amortized_sum.groupby(['signal', 'component_type'])
                        .value.sum()
                        .reset_index()
    )
    
    # Baseline
    '''
    package = carbon[carbon.metadata.str.contains('package').fillna(False)]
    s = package.groupby(['component_type']).value.sum().to_frame().reset_index()
    s['signal'] = 'cpu_package_carbon'
    summary.append(s)

    dram = carbon[carbon.metadata.str.contains('dram').fillna(False)]
    s = dram.groupby(['component_type']).value.sum().to_frame().reset_index()
    s['signal'] = 'cpu_dram_carbon'
    summary.append(s)

    # GPU
    gpu_op=carbon[(carbon.component_type == 'nvml') & (carbon.source == 'nvmlDeviceGetTotalEnergyConsumption')]
    gpu_op['signal']='gpu_carbon'
    gpu_op['component_type']='nvml'
    s=gpu_op.groupby(['signal', 'component_type']).value.sum().to_frame().reset_index()
    summary.append(s)

    '''
    return pd.concat(summary)


def parse_args():
    arg_parser=ArgumentParser()
    arg_parser.add_argument(dest='files', nargs='+')
    arg_parser.add_argument('--output')

    return arg_parser.parse_args()


def main():
    args=parse_args()
    summary=[]
    print(args.files)
    for f in tqdm(args.files):
        instance=f.split('/')[-2].split('-')[1]
        model='_'.join(f.split('/')[-3].split('@')[1].split('_')[-3:])

        df=pd.read_csv(f)
        summary.append(summarize(df).assign(
            instance=instance,
            model=model,
        ))

    summary=pd.concat(summary)
    print(summary)
    summary.to_csv(os.path.join(args.output, 'bert-profiled-summary.csv'), index=False)


if __name__ == '__main__':
    main()
