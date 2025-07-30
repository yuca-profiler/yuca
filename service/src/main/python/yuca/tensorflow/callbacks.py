import os
import time
import pandas as pd

from tensorflow.keras.callbacks import Callback

from yuca.client import YucaClient
from yuca.report import to_dataframe

from yuca.nvml.sampler import NvmlSampler

DEFAULT_PERIOD_MS = 10
DEFAULT_PERIOD_SECS = 2
DEFAULT_SIGNALS = [
    'nvml',
    'linux_process',
    'linux_system',
    'JOULES',
    'GRAMS_OF_CO2',
    'WATTS',
    'CELSIUS',
    'HERTZ',
]
UNITS = {
    'GRAMS_OF_CO2': 'CO2',
    'JOULES': 'J',
    'ACTIVITY': '%',
    'NANOSECONDS': 'ns',
    'JIFFIES': '',
    'WATTS': 'W',
    'CELSIUS': 'C',
    'HERTZ': 'Hz'
}


def add_yuca_log(df, logs=None):
    if logs:
        for (component_type, component_id, unit, source), df in df.groupby(['component_type', 'component_id', 'unit', 'source']):
            # TODO: this should really not ignore negatives
            if unit == 'JOULES':
                logs[f'{component_type}-{UNITS[unit]}'] = df[df > 0].sum()

# TODO(https://github.com/project-yuca/yuca/issues/35#issue-2551253967): Refactor so this can be reused easily
class YucaCallback(Callback):
    def __init__(
            self,
            addr,
            period_ms=DEFAULT_PERIOD_MS,
            signals=DEFAULT_SIGNALS):
        self.pid = os.getpid()
        self.client = YucaClient(addr)
        self.period_ms = period_ms
        self.signals = signals

    def start_yuca(self):
        self.client.purge()
        self.client.start(self.pid, self.period_ms)

    def stop_yuca(self):
        self.client.stop(self.pid)
        # return to_dataframe(self.client.read(self.pid, self.signals))
        return self.client.read(self.pid, self.signals)

class YucaChunkingCallback(YucaCallback):
    def __init__(
            self,
            addr='localhost:8980',
            period_ms=DEFAULT_PERIOD_MS,
            signals=DEFAULT_SIGNALS,
            chunking_period_sec=DEFAULT_PERIOD_SECS):
        super().__init__(addr, period_ms, signals)
        self.reports = {}
        self.chunking_period_sec = chunking_period_sec

    def on_epoch_begin(self, epoch, logs=None):
        self.time = time.time()
        self.last_report = None
        self.start_yuca()

    def on_train_batch_end(self, epoch, logs=None):
        curr = time.time()
        if (curr - self.time > self.chunking_period_sec):
            self.time = curr
            if self.last_report is None:
                self.last_report = to_dataframe(self.stop_yuca())
            else:
                self.last_report = pd.concat([
                    self.last_report,
                    to_dataframe(self.stop_yuca()),
                ])
            add_yuca_log(self.last_report, logs)
            self.start_yuca()

    def on_epoch_end(self, epoch, logs=None):
        if self.last_report is None:
            self.last_report = to_dataframe(self.stop_yuca())
        else:
            self.last_report = pd.concat([
                self.last_report,
                to_dataframe(self.stop_yuca()),
            ])
        add_yuca_log(self.last_report, logs)
        self.reports[epoch] = self.last_report.to_frame().assign(
            epoch=epoch).set_index('epoch', append=True)

class YucaExperimentCallback(YucaChunkingCallback):
    def __init__(
            self,
            addr='localhost:8980',
            period_ms=DEFAULT_PERIOD_MS,
            signals=DEFAULT_SIGNALS,
            chunking_period_sec=DEFAULT_PERIOD_SECS):
        super().__init__(addr, period_ms, signals, chunking_period_sec)
        self.timestamps = {}

    def on_epoch_begin(self, epoch, logs=None):
        super().on_epoch_begin(epoch, logs)
        self.batch_timestamps = []

    def on_train_batch_begin(self, batch, logs=None):
        self.batch_start = time.time()
        super().on_train_batch_begin(batch, logs)
        
    def on_train_batch_end(self, batch, logs=None):
        curr = time.time()
        super().on_train_batch_end(batch, logs)
        self.batch_start = int((10**9 * self.batch_start))
        self.batch_timestamps.append({'batch': batch, 'start': self.batch_start, 'end': int((10**9 * curr))})

    def on_epoch_end(self, epoch, logs=None):
        super().on_epoch_end(epoch, logs)
        self.timestamps[epoch] = pd.DataFrame(data = self.batch_timestamps).assign(
            epoch=epoch)
            
class YucaPredictCallback(YucaCallback):
    def __init__(self, addr='localhost:8980', period_ms=DEFAULT_PERIOD_MS, signals=DEFAULT_SIGNALS,chunking_period_sec=DEFAULT_PERIOD_SECS):
        super().__init__(addr, period_ms, signals)
        self.reports = {}
        self.chunking_period_sec = chunking_period_sec

    def on_predict_begin(self, logs=None):
        self.time = time.time()
        self.last_report = None
        self.start_yuca()

    def on_predict_batch_end(self, batch, logs=None):
        curr = time.time()
        if (curr - self.time > self.chunking_period_sec):
            self.time = curr
            if self.last_report is None:
                self.last_report = [self.stop_yuca()]
            else:
                self.last_report.append(self.stop_yuca())
            self.start_yuca()

        if self.last_report is None:
            self.last_report = [self.stop_yuca()]
        else:
            self.last_report.append(self.stop_yuca())
        self.reports[batch] = pd.concat(list(map(
            to_dataframe,
            self.last_report
        ))).to_frame().assign(
            batch=batch).set_index('batch', append=True)

class NvmlSamplerCallback(Callback):
    def __init__(self):
        self.sampler = NvmlSampler()

    def on_epoch_begin(self, epoch, logs = None):
        self.sampler.sample()
    
    def on_epoch_end(self, epoch, logs = None):
        self.sampler.sample()

# TODO: these two benchmarks exist for completeness; always use the chunking callback.
# TODO: we need the streaming response rpc for this
class YucaEpochCallback(YucaCallback):
    def __init__(self, addr='localhost:8980', period_ms=DEFAULT_PERIOD_MS, signals=DEFAULT_SIGNALS):
        super().__init__(addr, period_ms, signals)
        self.reports = {}

    def on_epoch_begin(self, epoch, logs=None):
        self.start_yuca()

    def on_epoch_end(self, epoch, logs=None):
        self.reports[epoch] = to_dataframe(self.stop_yuca())
        add_yuca_log(self.reports[epoch], logs)

# TODO: this kills performance due to the GRPC layer
class YucaBatchCallback(YucaCallback):
    def __init__(self, addr='localhost:8980', period_ms=DEFAULT_PERIOD_MS, signals=DEFAULT_SIGNALS):
        super().__init__(addr, period_ms, signals)
        self.reports = {}

    def on_train_batch_begin(self, epoch, logs=None):
        self.start_yuca()
        self.reports[epoch] = []

    def on_train_batch_end(self, epoch, logs=None):
        self.reports[epoch].append(to_dataframe(self.stop_yuca()))
        add_yuca_log(self.reports[epoch], logs)

class YucaChunkingCallback2(YucaCallback):
    def __init__(
            self,
            addr='localhost:8980',
            period_ms=DEFAULT_PERIOD_MS,
            signals=DEFAULT_SIGNALS,
            chunking_period_sec=DEFAULT_PERIOD_SECS):
        super().__init__(addr, period_ms, signals)
        self.reports = {}
        self.chunking_period_sec = chunking_period_sec

    def on_epoch_begin(self, epoch, logs=None):
        self.time = time.time()
        self.last_report = None
        self.start_yuca()

    def on_train_batch_end(self, epoch, logs=None):
        curr = time.time()
        if (curr - self.time > self.chunking_period_sec):
            self.time = curr
            if self.last_report is None:
                self.last_report = [self.stop_yuca()]
            else:
                self.last_report.append(self.stop_yuca())
            self.start_yuca()

    def on_epoch_end(self, epoch, logs=None):
        if self.last_report is None:
            self.last_report = [self.stop_yuca()]
        else:
            self.last_report.append(self.stop_yuca())
        self.reports[epoch] = pd.concat(list(map(
            to_dataframe,
            self.last_report
        ))).to_frame().assign(
            epoch=epoch).set_index('epoch', append=True)

# TODO: we need the streaming response rpc for this
class YucaDumpingEpochCallback(YucaCallback):
    def __init__(
            self,
            addr='localhost:8980',
            period_ms=DEFAULT_PERIOD_MS,
            signals=DEFAULT_SIGNALS,
            output_path=None):
        super().__init__(addr, period_ms, signals)
        if output_path is None:
            self.output_path = f'/tmp/yuca-{os.getpid()}'
        else:
            self.output_path = output_path

    def on_epoch_begin(self, epoch, logs=None):
        self.start_yuca()

    def on_epoch_end(self, epoch, logs=None):
        self.client.stop(self.pid)
        self.client.dump(
            self.pid, f'{self.output_path}/report-{epoch}.pb', self.signals)

