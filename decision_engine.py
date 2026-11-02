# Processes that should never be optimized
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


def is_safe_to_optimize(process):
    """
    Decide whether a process is a candidate for optimization.
    """

    name = process["name"]

    if not name:
        return False

    name_lower = name.lower()

    # Never optimize protected Windows processes
    if name_lower in PROTECTED_PROCESSES:
        return False

    # Only consider processes identified as resource-heavy
    if process["category"] in ["HIGH CPU", "HIGH MEMORY"]:
        return True

    return False


def get_optimization_candidates(processes):
    """
    Return processes that are safe candidates for optimization.
    """

    candidates = []

    for process in processes:

        if is_safe_to_optimize(process):
            candidates.append(process)

    return candidates