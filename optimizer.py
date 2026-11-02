import psutil
from optimization_history import log_optimization


def get_priority(pid):
    """
    Get the current priority of a process.
    """
    process = psutil.Process(pid)
    return process.nice()


def lower_priority(pid):
    """
    Lower the priority of a process.
    """
    process = psutil.Process(pid)

    original_priority = process.nice()

    # Lower priority on Windows
    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

    return original_priority


def restore_priority(pid, original_priority):
    """
    Restore the original process priority.
    """
    process = psutil.Process(pid)
    process.nice(original_priority)


def optimize_and_restore(pid):
    """
    Lower process priority and then restore it.

    Records the optimization action in the history file.
    """

    process = psutil.Process(pid)

    process_name = process.name()
    priority_before = process.nice()

    # Lower priority
    process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    priority_after = process.nice()

    # Restore original priority
    process.nice(priority_before)
    restored = process.nice() == priority_before

    # Record the optimization action.
    # CPU/memory measurements are not performed here because
    # performance.py is responsible for performance measurement.
    log_optimization(
        pid=pid,
        process_name=process_name,
        cpu_before=0,
        memory_before=0,
        priority_before=priority_before,
        priority_after=priority_after,
        cpu_after=0,
        memory_after=0,
        restored=restored
    )

    return {
        "pid": pid,
        "process_name": process_name,
        "priority_before": priority_before,
        "priority_after": priority_after,
        "restored": restored
    }