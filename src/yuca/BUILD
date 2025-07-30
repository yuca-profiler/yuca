alias(
    name = "yuca",
    visibility = ["//visibility:public"],
    actual = "//src/yuca/src/main/java/yuca",
)

java_binary(
    name = "rapl_smoke_test",
    main_class = "yuca.cpu.rapl.RaplSmokeTest",
    runtime_deps = [":yuca"],
)

java_binary(
    name = "rapl_monitor",
    main_class = "yuca.cpu.rapl.RaplMonitor",
    runtime_deps = [":yuca"],
)

java_binary(
    name = "cpufreq_monitor",
    main_class = "yuca.cpu.freq.CpuFreqMonitor",
    runtime_deps = [":yuca"],
)

java_binary(
    name = "sys_thermal_cooldown",
    main_class = "yuca.linux.thermal.SysThermalCooldown",
    runtime_deps = [":yuca"],
)

java_binary(
    name = "systemp_monitor",
    main_class = "yuca.linux.thermal.TemperatureMonitor",
    runtime_deps = [":yuca"],
)

alias(
    name = "emissions_data",
    actual = "//src/main/resources/emissions/WorldIntensity.csv",
)
