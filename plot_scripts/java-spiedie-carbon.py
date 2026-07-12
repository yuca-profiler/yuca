#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import re
import glob
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


# In[ ]:


TUPLE_TO_SYMBOL_NAME = {
    value: name
    for name, value in vars(sym).items()
    if name.isupper() and isinstance(value, tuple)
}


# In[ ]:


def map_symbol(t):
    name = TUPLE_TO_SYMBOL_NAME.get(t)
    if name is None:
        print(f"No mapping found for tuple: {t}")
    return name


# In[ ]:


def plot_single_bar(grouped, unit, workload):
    df = grouped[(grouped['symbol_name'] == unit) & (grouped['workload'] == workload)]
    title = df['workload'].unique()[0]
    symbol_name = df['symbol_name'].unique()[0]
    
    pivoted = df.pivot(index='workload', columns='socket', values='elapsed')
    pivoted.plot(title=f'spiedie {title} {symbol_name}', kind='bar')
    
def plot_bar(df, title, ylabel, ylim=None, legend=True, figsize=(12, 5)):    
    ax = df.plot(
        kind='bar',
        title=title,
        stacked=True,
        figsize=figsize
    )
    handles, labels = ax.get_legend_handles_labels()

    ax.legend(handles, labels)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha = 'right')
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


KG_TO_G = 1000
# lifespan is 5 years in seconds
ssd_lifespan = 157680000
ssd_embodied_carbon =  2143 * 0.16 * KG_TO_G
ssd_design_power = 8

dram_lifespan = 157680000
dram_embodied_carbon = 512 * 0.29 * KG_TO_G
# We measure DRAM, this is only for completeness
dram_design_power = 0

def process_ssd(df, amortized=True):
    ssd = df.copy()
    if amortized == True:
        print('Doing amortized ssd')
        rate = ssd_embodied_carbon / ssd_lifespan
        ssd['SSD'] = (ssd['sum'] / 1e9) * rate
    else:
        print('Doing operational ssd')
        ssd['SSD'] = (ssd['sum'] / 1e9) * 396.87 * 2.77778e-7 * ssd_design_power
    return ssd[['SSD', 'workload']].set_index('workload').reset_index()

def process_dram(df, amortized=True):
    dram = df.copy()
    if amortized == True:
        print('Doing amortized dram')
        rate = dram_embodied_carbon / dram_lifespan
        dram['DRAM'] = (dram['sum'] / 1e9) * rate
    else:
        print('Doing operational dram')
        dram['DRAM'] = (dram['sum'] / 1e9) *  396.87 * 2.77778e-7 * dram_design_power
    return dram[['DRAM', 'workload']].set_index('workload').reset_index()


# In[ ]:


def load_all_java_runs(d_pattern, p_pattern):
    dacapo = sorted(glob.glob(d_pattern))
    renaissance = sorted(glob.glob(p_pattern))
    
    dfs = []

    for i, (d, r) in enumerate(zip(dacapo, renaissance)):
        df = pd.concat([
            pd.read_csv(d),
            pd.read_csv(r)
        ], ignore_index=True)
        
        df["run_id"] = i
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


# In[ ]:


def group_report(report, statistic):
    df = report.copy()
    df['symbol_name'] = report['symbol'].apply(parse_symbol).apply(map_symbol)
    # Toss the first 40 iterations (cold runs)
    df = df[df['iteration'] > 40]
    grouped = df.groupby(['suite', 'workload', 'device_id', 'symbol_name'])[statistic].agg(['sum'])
    grouped = grouped.reset_index()
    return grouped


# In[ ]:


def process_java(report, signal, name):
    df = report.copy()
    df = df[df['symbol_name'] == signal]
    if signal == 'cpu_package_carbon' or signal == 'cpu_dram_carbon':
        df = df[df['component_type'] == 'linux_system']
    return df.set_index('workload')[['sum']].rename(columns = {'sum':name}).reset_index()


# In[ ]:


def process_report_operational(profiled):
    report = group_report(profiled.copy(), "sum")

    cpu = (
        process_java(report,
                     "SOCKET_PACKAGE_OPERATIONAL_EMISSIONS",
                     "CPU")
        .groupby("workload", as_index=False)["CPU"]
        .sum()
    )

    dram = (
        process_java(report,
                     "SOCKET_DRAM_OPERATIONAL_EMISSIONS",
                     "DRAM")
        .groupby("workload", as_index=False)["DRAM"]
        .sum()
    )

    elapsed_report = group_report(profiled.copy(), "elapsed")
    elapsed_report = elapsed_report[
        elapsed_report["symbol_name"] == "SOCKET_POWER"
    ]

    ssd = process_ssd(elapsed_report, "False")

    df = pd.concat(
        [
            cpu.set_index("workload"),
            dram.set_index("workload"),
            ssd.set_index("workload"),
        ],
        axis=1,
    ).reset_index()

    return df


# In[ ]:


def process_report_embodied(profiled):

    report = group_report(profiled.copy(), "sum")

    cpu = (
        process_java(
            report,
            "CPU_AMORTIZED_EMISSIONS",
            "CPU"
        )
        .groupby("workload", as_index=False)["CPU"]
        .sum()
    )

    elapsed_report = group_report(profiled.copy(), "elapsed")
    elapsed_report = elapsed_report[
        elapsed_report["symbol_name"] == "SOCKET_POWER"
    ]

    # dram = process_dram(elapsed_report)
    dram = (
        process_java(report,
                     "DRAM_AMORTIZED_EMISSIONS",
                     "DRAM")
        .groupby("workload", as_index=False)["DRAM"]
        .sum()
    )
    ssd = process_ssd(elapsed_report)

    df = pd.concat(
        [
            cpu.set_index("workload"),
            dram.set_index("workload"),
            ssd.set_index("workload"),
        ],
        axis=1,
    ).reset_index()

    return df


# In[ ]:


def get_summary(all_reports):
    mean_df = (
        all_reports
        .groupby("workload")[["CPU", "DRAM", "SSD"]]
        .mean()
    )
    
    std_df = (
        all_reports
        .groupby("workload")[["CPU", "DRAM", "SSD"]]
        .std()
    )
    return mean_df, std_df


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


def plot_bar(mean, std, title, ylabel, ylim=None, legend=True, figsize=(12, 6)):
    workloads = mean.index
    
    fig, ax = plt.subplots(figsize=figsize)
    bottom = np.zeros(len(workloads))
    
    # add hatching per series
    hatches = ['/o', '\\|', '|*', '-\\', '+o', 'x*', 'o-', 'O|', 'O.', '*-']
    
    for i, col in enumerate(mean.columns):
        bars = ax.bar(workloads, mean[col], 
               bottom=bottom, 
               yerr=std[col],  # error bars
               label=col, 
               color=color_map[col],
    
                capsize=5,         
                error_kw={
                    "elinewidth": 2,  
                    "capthick": 2,    
                    "ecolor": "black",
                    "zorder": 10 
                }
        )
        for bar in bars:
            bar.set_hatch(hatches[i])
        bottom += mean[col].values  # update bottom for stacking
    
    ax.set_ylabel(get_latex('GRAMS_OF_CO2'))
    plt.xticks(rotation=45, ha='right')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])
        
    plt.tight_layout()
    return ax


# In[ ]:


def get_all_reports(reports, amortized=True):
    dfs = []
    
    for i, report in enumerate(reports):
        if amortized:
            df = process_report_embodied(report)
            df["instance"] = i
            dfs.append(df)
        else:
            df = process_report_operational(report)
            df["instance"] = i
            dfs.append(df)
    
    all_reports = pd.concat(dfs, ignore_index=True)
    return all_reports


# In[ ]:


plots_dir = 'jul-12-plots'
machine = 'spiedie'


# In[ ]:


reports = [
    pd.concat([pd.read_csv("data-ghpc005-dacapo-instance-0/agg_symbols.csv"),
               pd.read_csv("data-ghpc005-renaissance-instance-0/agg_symbols.csv")]),
    pd.concat([pd.read_csv("data-ghpc005-dacapo-instance-1/agg_symbols.csv"),
               pd.read_csv("data-ghpc005-renaissance-instance-1/agg_symbols.csv")]),
    pd.concat([pd.read_csv("data-ghpc005-dacapo-instance-2/agg_symbols.csv"),
               pd.read_csv("data-ghpc005-renaissance-instance-2/agg_symbols.csv")]),
]


# In[ ]:


all_reports = get_all_reports(reports, False)
mean, std = get_summary(all_reports)

op_total = mean.copy()
ax = plot_bar(mean, std, None, get_latex('GRAMS_OF_CO2'), figsize=(10,4))

plt.savefig(
    f'plots/{plots_dir}/{machine}_java_stacked_operational.pdf',
    bbox_inches='tight'
)


# In[ ]:


all_reports = get_all_reports(reports, True)
mean, std = get_summary(all_reports)
em_total = mean.copy()
ax = plot_bar(mean, std, None, get_latex('GRAMS_OF_CO2'), figsize=(10,4))

plt.savefig(
    f'plots/{plots_dir}/{machine}_java_stacked_amortized.pdf',
    bbox_inches='tight'
)


# In[ ]:


def plot_bar_percent(df, std_df, title, ylabel, ylim=None, legend=True, figsize=(12, 6)):

    workloads = df.index

    fig, ax = plt.subplots(figsize=figsize)
    bottom = np.zeros(len(workloads))

    hatches = ['/o', '\\|', '|*', '-\\', '+o', 'x*', 'o-', 'O|', 'O.', '*-']

    for i, col in enumerate(df.columns):

        bars = ax.bar(
            workloads,
            df[col].values,
            bottom=bottom,
            label=col,
            color=color_map[col]
        )

        for bar in bars:
            bar.set_hatch(hatches[i % len(hatches)])

        bottom += df[col].values

    op_height = df["Operational"].values
    err = std_df["Operational"].values  # same as embodied

    ax.errorbar(
        x=np.arange(len(workloads)),
        y=op_height,
        # yerr=err,
        fmt='none',
        ecolor='black',
        elinewidth=2,
        capsize=5,
        capthick=2,
        zorder=10
    )

    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')

    if ylim == 0:
        ax.set_yscale("log")
    elif ylim is not None:
        ax.set_ylim(0, ylim)

    handles, labels = ax.get_legend_handles_labels()
    if legend:
        ax.legend(handles[::-1], labels[::-1])

    plt.tight_layout()
    return ax


# In[ ]:


op_runs = []
em_runs = []

for r in reports:

    op_runs.append(process_report_operational(r))
    em_runs.append(process_report_embodied(r))

op_totals = []
em_totals = []

for op, em in zip(op_runs, em_runs):

    op_total = op.set_index("workload").sum(axis=1)
    em_total = em.set_index("workload").sum(axis=1)

    op_totals.append(op_total)
    em_totals.append(em_total)


op_pct_runs = []
em_pct_runs = []

for op_t, em_t in zip(op_totals, em_totals):

    total = op_t + em_t

    op_pct_runs.append(op_t / total * 100)
    em_pct_runs.append(em_t / total * 100)

op_pct_all = pd.concat(op_pct_runs, axis=1)
em_pct_all = pd.concat(em_pct_runs, axis=1)


ratio_mean = pd.DataFrame({
    "Operational": op_pct_all.mean(axis=1),
    "Embodied": em_pct_all.mean(axis=1),
})

ratio_std = pd.DataFrame({
    "Operational": op_pct_all.std(axis=1),
    "Embodied": em_pct_all.std(axis=1),
})


# In[ ]:


ax = plot_bar_percent(
    ratio_mean,
    ratio_std,
    None,
    get_latex("PERCENT"),
    figsize=(10,4)
)

plt.savefig(
    f'plots/{plots_dir}/{machine}_java_carbon_percentage.pdf',
    bbox_inches='tight'
)


# In[ ]:


ratio_mean.to_csv('ratio_csvs/java_mean.csv')
ratio_std.to_csv('ratio_csvs/java_std.csv')

