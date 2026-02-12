from enum import Enum


class LogicalUnit(Enum):
    SOCKET = 1
    CPU = 2
    TASK = 3
    GPU = 4
    DISK = 5


class PhysicalUnit(Enum):
    ACTIVITY = 1
    ACTIVITY_RATE = 2
    CYCLES = 3
    GRAMS_OF_CO2 = 4
    GRAMS_OF_CO2_RATE = 5
    JOULES = 6
    JIFFIES = 7
    HERTZ = 8
    NANOSECONDS = 9
    WATTS = 10
    CELSIUS = 11

class EmissionKind(Enum):
    OPERATIONAL = 1
    AMORTIZED = 2
