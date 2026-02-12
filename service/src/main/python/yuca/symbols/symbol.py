from yuca.symbols.unit import EmissionKind, LogicalUnit, PhysicalUnit

DISK_POWER = (
    LogicalUnit.DISK,
    PhysicalUnit.WATTS
) 

DISK_OPERATIONAL_EMISSIONS = (
    LogicalUnit.DISK,
    PhysicalUnit.GRAMS_OF_CO2_RATE,
    EmissionKind.OPERATIONAL
)

SOCKET_POWER = (
    LogicalUnit.SOCKET,
    PhysicalUnit.WATTS
)

SOCKET_OPERATIONAL_EMISSIONS = (
    LogicalUnit.SOCKET,
    PhysicalUnit.GRAMS_OF_CO2_RATE,
    EmissionKind.OPERATIONAL
)
SOCKET_TEMPERATURE = (
    LogicalUnit.SOCKET,
    PhysicalUnit.CELSIUS
)
CPU_FREQUENCY = (
    LogicalUnit.CPU,
    PhysicalUnit.HERTZ
)
CPU_AMORTIZED_EMISSIONS = (
    LogicalUnit.SOCKET,
    PhysicalUnit.GRAMS_OF_CO2_RATE,
    EmissionKind.AMORTIZED
)
TASK_POWER = (
    LogicalUnit.TASK,
    PhysicalUnit.WATTS
)
TASK_OPERATIONAL_EMISSIONS = (
    LogicalUnit.TASK,
    PhysicalUnit.GRAMS_OF_CO2_RATE,
    EmissionKind.OPERATIONAL
)