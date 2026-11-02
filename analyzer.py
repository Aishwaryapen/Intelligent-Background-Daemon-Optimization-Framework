import psutil


# Processes that should never be considered for optimization
PROTECTED_PROCESSES = {
    "system",
    "system idle process",
    "registry",
    "smss.exe",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "svchost.exe",
}


def analyze_process(process):
    """
    Analyze one process and decide whether it needs attention.
    """

    name = process["name"]
    cpu = process["cpu"]
    memory = process["memory"]

    # Handle processes with no name
    if not name:
        return "UNKNOWN"

    name_lower = name.lower()

    # Protect important Windows processes
    if name_lower in PROTECTED_PROCESSES:
        return "PROTECTED"

    # High CPU usage
    if cpu >= 20:
        return "HIGH CPU"

    # High memory usage
    if memory >= 5:
        return "HIGH MEMORY"

    # Normal resource usage
    return "NORMAL"


def analyze_processes(processes):
    """
    Analyze all processes.
    """

    results = []

    for process in processes:

        category = analyze_process(process)

        result = process.copy()
        result["category"] = category

        results.append(result)

    return results