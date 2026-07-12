#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import re
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


# In[ ]:


from yuca.symbols.unit import EmissionKind, LogicalUnit, PhysicalUnit, SocketComponentKind
from yuca.symbols import symbol as sym

mpl.rcParams['pdf.fonttype'] = 42                                                                                                                             
mpl.rcParams['ps.fonttype'] = 42


# In[ ]:


def parse_symbol(s):
    matches = re.findall(r"<(\w+)\.(\w+): \d+>", s)
    mapping = {
        'LogicalUnit': LogicalUnit,
        'PhysicalUnit': PhysicalUnit,
        'EmissionKind': EmissionKind,
        'SocketComponentKind': SocketComponentKind,
    }
    return tuple(mapping[cls][member] for cls, member in matches)
    
def get_latex(unit):
    FONTS = {
        'GRAMS_OF_CO2':'$g\ CO_2$',
        'MGRAMS_OF_CO2': '$mg\ CO_2$',
        'HERTZ': '$Hertz$',
        'GIGAHERTZ':'$Gigahertz$',
        'CELSIUS':'$Celsius$',
        'WATTS': '$Watts$',
        'NANOSECONDS': '$Nanoseconds$',
        'PERCENT': '$Percent$',
    }
    return FONTS[unit]
    
def get_bert_labels(model):
    name = model.split('small_bert@bert_en_uncased_')[-1]
    L = name.split('_')[0].split('-')[-1]
    H = name.split('_')[1].split('-')[-1]
    label = f'L={L},H={H}'
    return label
    
def extract_keys(idx):
    nums = idx.str.extract(r'L-(\d+)_H-(\d+)_A-(\d+)')
    return (
        nums[0].astype(int) * 1000000 +
        nums[1].astype(int) * 1000 +
        nums[2].astype(int)
    )
    
def extract_bert_keys(idx):
    m = re.search(r'L=(\d+),H=(\d+)', idx)
    return (int(m.group(1)) * 1000000 +
            int(m.group(2)) * 1000)


# In[ ]:


def process_bert(report, signal):
    df = report.copy()
    df = df[df['signal'] == signal]
    if signal == 'cpu_package_carbon' or signal == 'cpu_dram_carbon':
        df = df[df['component_type'] == 'linux_process']
    return df.set_index('model')[['mean', 'std']].sort_index(key=extract_keys)


# In[ ]:


color_map = {
    'CPU': 'tab:orange',
    'GPU': 'tab:green',
    'DRAM': 'tab:blue',
    'SSD': 'tab:red',
    "Operational": "tab:purple",
    "Embodied":    "tab:cyan",
}


# In[ ]:


def plot_stacked(cpu, dram, gpu, ssd, figsize=(12,6)):
    models = cpu.index
    means_stack = pd.DataFrame({
        'CPU': cpu['mean'],
        'GPU': gpu['mean'],
        'DRAM': dram['mean'],
        'SSD': ssd['mean']
    }, index=models)
    
    std_stack = pd.DataFrame({
        'CPU': cpu['std'],
        'GPU': gpu['std'],
        'DRAM': dram['std'],
        'SSD': ssd['std']
    }, index=models)
    
    fig, ax = plt.subplots(figsize=figsize)
    bottom = np.zeros(len(models))
    
    # add hatching per series
    hatches = ['/o', '\\|', '|*', '-\\', '+o', 'x*', 'o-', 'O|', 'O.', '*-']
    
    for i, col in enumerate(means_stack.columns):
        bars = ax.bar(models, means_stack[col], 
               bottom=bottom, 
               yerr=std_stack[col],  # error bars
               label=col, 
               color=color_map[col],
               capsize=3)
        for bar in bars:
            bar.set_hatch(hatches[i])
        bottom += means_stack[col].values  # update bottom for stacking
    
    ax.set_ylabel(get_latex('GRAMS_OF_CO2'))
    ax.set_xticklabels(
        models.map(get_bert_labels),
        rotation=45,
        ha="right"
    )

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])
        
    plt.tight_layout()
    return ax
    # plt.show()


# In[ ]:


KG_TO_G = 1000
# lifespan is 5 years in seconds
ssd_lifespan = 157680000
ssd_embodied_carbon =  2143 * 0.16 * KG_TO_G
ssd_design_power = 8.35

def add_ssd_signal(report, amortized=True):
    
    carbon = (
        report[report["signal"] == "runtime"]
    )

    if amortized:
        rate = ssd_embodied_carbon / ssd_lifespan
        carbon['signal'] = 'ssd_amortized_carbon'

    else:
        rate = 396.87 * 2.77778e-7 * ssd_design_power
        carbon['signal'] = 'ssd_carbon'

    carbon['value']*=rate
    carbon['component_type'] = 'linux_process'
    return carbon


# In[ ]:


# lifespan is 5 years in seconds
dram_lifespan = 157680000
dram_embodied_carbon = 512 * 0.29 * KG_TO_G
# We measure DRAM, this is only for completeness
dram_design_power = 0

def add_dram_signal(report, amortized=True):
    
    carbon = (
        report[report["signal"] == "runtime"]
    )

    if amortized:
        rate = dram_embodied_carbon / dram_lifespan
        carbon['signal'] = 'dram_amortized_carbon'

    else:
        rate = 396.87 * 2.77778e-7 * dram_design_power
        carbon['signal'] = 'dram_carbon'

    carbon['value']*=rate
    carbon['component_type'] = 'linux_process'
    return carbon


# In[ ]:


df = pd.read_csv("bert-profiled-summary-dump-101kg.csv")

report = pd.concat(
    [
        df,
        add_ssd_signal(df),
        add_ssd_signal(df, False),
        add_dram_signal(df),
    ],
    ignore_index=True,
)
report.to_csv('bert-profiled-summary-dump-101kg-with-ssd.csv', index=False)

report = (
    report.groupby(["model", "signal", "component_type"])["value"]
          .agg(["mean", "std"])
          .reset_index()
)

data_dir = 'jun-30-plots'


# In[ ]:


# bert operational carbon

df = pd.DataFrame()
cpu = process_bert(report, 'cpu_package_carbon')
dram = process_bert(report, 'cpu_dram_carbon')
gpu = process_bert(report, 'gpu_carbon')
ssd = process_bert(report, 'ssd_carbon')

ax = plot_stacked(cpu, dram, gpu, ssd, (10,4))

plt.savefig(f'plots/{data_dir}/spiedie_bert_stacked_operational.pdf', bbox_inches='tight')
op_total = cpu + dram + gpu + ssd


# In[ ]:


# bert amortized carbon
df = pd.DataFrame()
cpu = process_bert(report, 'cpu_amortized_sum')
dram = process_bert(report, 'cpu_amortized_sum')
gpu = process_bert(report, 'gpu_amortized_carbon')
ssd = process_bert(report, 'ssd_amortized_carbon')

ax = plot_stacked(cpu, dram, gpu, ssd, (10,4))

plt.savefig(f'plots/{data_dir}/spiedie_bert_stacked_amortized.pdf', bbox_inches='tight')
em_total = cpu + dram + gpu + ssd


# In[ ]:


def plot_bar(df, title, ylabel, ylim=None, legend=True, figsize=(12,6)):    
    ax = df.plot(
        kind='bar',
        title=title,
        stacked=True,
        figsize=figsize,
        color=[color_map[col] for col in df.columns]
    )

    labels = [
        get_bert_labels(idx)
        for idx in df.index
    ]
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_xlim(left = -0.5, right=len(df) - 0.5)
    ax.set_xlabel('')
    
    # y axis
    ax.set_ylabel(ylabel)
    ax.set_ylim(bottom=0)
    
    if ylim == 0:
        ax.set_yscale('log')
    elif ylim is not None:
        ax.set_ylim(0,ylim)
    
    # add hatching per series
    hatches = ['/o', '\\|', '|*', '-\\', '+o', 'x*', 'o-', 'O|', 'O.', '*-']
    for i, container in enumerate(ax.containers):
        hatch = hatches[i % len(hatches)]
        for bar in container:
            bar.set_hatch(hatch)

    # legend in correct order (IMPORTANT FIX)
    handles = [c[0] for c in ax.containers][::-1]
    labels = list(df.columns)[::-1]

    if legend:
        ax.legend(handles, labels)

    plt.tight_layout()
    return ax


# In[ ]:


op_stacked = op_total['mean']
em_stacked = em_total['mean']

op = (op_stacked / ( op_stacked + em_stacked)) * 100
em = (em_stacked / ( op_stacked + em_stacked)) * 100

ratio = pd.DataFrame()
ratio['Operational'] = op
ratio['Embodied'] = em

ax = plot_bar(ratio, None, get_latex('PERCENT'), figsize=(10,4))
plt.savefig(f'plots/{data_dir}/spiedie_bert_carbon_percentage.pdf', bbox_inches='tight')

