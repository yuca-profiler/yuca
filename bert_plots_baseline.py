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
    
    '''
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
    # cpu_freqs['cpu'] = cpu_freqs.metadata.str.split('=').str[1].astype(int)
    cpu_freqs['cpu'] = meta.str['cpu'].astype(int)
    cpu_freqs['socket'] = meta.str['socket'].astype(int)
    # print(cpu_freqs['cpu'])
    # print(cpu_freqs['socket'])
    # cpu_freqs['socket'] = 0
    cpu_freqs = cpu_freqs.drop_duplicates(['start', 'cpu'])

    cpu_temp = cpu_temp[['start', 'socket', 'value']]
    cpu_temp['timestamp'] = cpu_temp['start']
    cpu_temp = cpu_temp.set_index(['timestamp', 'socket']).value

    cpu_freqs = cpu_freqs[['start', 'cpu', 'socket', 'value']]
    cpu_freqs['timestamp'] = cpu_freqs['start']
    cpu_freqs = cpu_freqs.groupby(['timestamp', 'cpu', 'socket']).value.max()

    # amortized = compute_amortized_carbon(cpu_temp, cpu_freqs, 35, 1.6 * 10**9).to_frame()
    amortized = compute_amortized_carbon(cpu_temp, cpu_freqs, 43, 1.6 * 10**9, cpu_lifespan, cpu_embodied_carbon)
    amortized['signal']='cpu_amortized_carbon'
    amortized['component_type']='linux_system'
    s = amortized.groupby(['signal', 'component_type']).value.sum().to_frame().reset_index()
    summary.append(s)
    
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

    gpu_freqs=freqs[freqs.component_type == 'nvml']
    gpu_freqs['cpu']=0
    gpu_freqs['socket']=0

    gpu_temp=gpu_temp[['start', 'socket', 'value']]
    gpu_temp['timestamp']=gpu_temp['start']
    gpu_temp=gpu_temp.set_index(['timestamp', 'socket']).value

    gpu_freqs=gpu_freqs[['start', 'cpu', 'socket', 'value']]
    gpu_freqs['timestamp']=gpu_freqs['start']
    gpu_freqs=gpu_freqs.groupby(['timestamp', 'cpu', 'socket']).value.max()

    # amortized=compute_amortized_carbon(gpu_temp, gpu_freqs, 40, 1.6 * 10**9).to_frame()
    amortized=compute_amortized_carbon(gpu_temp, gpu_freqs, 40, 1.6 * 10**9, gpu_lifespan, gpu_embodied_carbon)
    amortized['component_type']='nvml'
    amortized['signal']='gpu_amortized_carbon'
    s=amortized.groupby(['signal', 'component_type']).value.sum().to_frame().reset_index()
    summary.append(s)
    '''
    # Baseline
    
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
    summary.to_csv(os.path.join(args.output, 'bert-baseline-summary.csv'), index=False)


if __name__ == '__main__':
    main()
