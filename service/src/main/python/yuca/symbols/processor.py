def interval_bounds(interval):
    start = 1e9 * interval.start.secs + interval.start.nanos
    end = 1e9 * interval.end.secs + interval.end.nanos
    elapsed = (end - start) / 1e9
    return start, elapsed

def get_metadata(data):
    return {m.name: m.value for m in data.metadata}
    
class SignalProcessor:
    def process(self, signal):
        return self.index, self._process_internal(signal)

    def _process_internal(self, signal):
        pass