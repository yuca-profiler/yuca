import numpy as np
import pandas as pd
import scipy as sp

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
cpu_embodied_carbon=7300

dram_lifespan = 157680000
dram_embodied_carbon = 512 * 0.29 * 1000

ssd_lifespan = 157680000
ssd_embodied_carbon =  2143 * 0.16 * 100

def compute_amortized_carbon(temperature, frequency, normal_temperature, normal_frequency):
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
    norm = temperature.copy(deep=True)
    norm[norm > normal_temperature] = normal_temperature
    # e^(T/temp) / e^(T/normal temp) = e^(T/temp - T/normal temp) = e^(T * (1 /temp - 1/normal temp))
    # Temperature must be in Kelvin for aging to prevent unit mismatch
    age = np.exp(T * (1 / (273 + temperature['value']) - 1 / (273 + norm['value'])))

    df = pd.concat(
        [frequency['value'].unstack('cpu'), age],
        axis=1
    )
    dfs = []
    for _, df in df.groupby('device_id'):
        df = df.sort_index()
        df = df.ffill().dropna(axis=1, how='all').dropna(axis=0)
        age = df.pop('value')
        count = df.shape[1]
        for col in df.columns:
            norm = df[col].copy(deep=True)
            norm[norm > normal_frequency] = normal_frequency
            df[col] = (age * df[col] / norm) * \
                (cpu_embodied_carbon / count / cpu_lifespan)

        df.columns.name = 'cpu'
        df = df.stack().to_frame(name='value')
        df = df.groupby(['timestamp', 'device_id'])['value'].sum().to_frame()
        df['elapsed'] = df.reset_index().groupby('device_id')['timestamp'].diff().values / 1e9
        df = df.dropna()
        dfs.append(df)
    amortized = pd.concat(dfs)
    amortized.name = 'value'

    return amortized

def compute_straight_line_amortized_carbon(power, lifespan, embodied_carbon):
    # straight line amortization
    df = power.copy()
    rate = embodied_carbon / lifespan
    df['value'] = rate
    return df