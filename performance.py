import psutil
import time


def measure_process(pid, duration=3):
    """
    Measure CPU and memory usage of a process.
    """

    process = psutil.Process(pid)

    # First call initializes CPU measurement
    process.cpu_percent(None)

    time.sleep(duration)

    cpu = process.cpu_percent(None)
    memory = process.memory_percent()

    return {
        "cpu": cpu,
        "memory": memory
    }