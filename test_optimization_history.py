import psutil
import time

from performance import measure_process
from optimizer import lower_priority, restore_priority
from optimization_history import log_optimization


def find_test_workload():
    """
    Find the running test_workload.py process automatically.
    """

    current_pid = psutil.Process().pid

    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if process.info["pid"] == current_pid:
                continue

            cmdline = process.info["cmdline"]

            if cmdline:
                command = " ".join(cmdline).lower()

                if "test_workload.py" in command:
                    return process.info["pid"]

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return None


print("=" * 60)
print("OPTIMIZATION + PERFORMANCE + HISTORY TEST")
print("=" * 60)


PID = find_test_workload()

if PID is None:
    print("\nNo running test_workload.py process found.")
    print("Start it first with:")
    print("python test_workload.py")
    exit()


try:
    process = psutil.Process(PID)

    print(f"Process: {process.name()}")
    print(f"PID: {PID}")

    # ---------------------------------------------------------
    # 1. Get original priority
    # ---------------------------------------------------------
    priority_before = process.nice()

    print(f"\nOriginal priority: {priority_before}")

    # ---------------------------------------------------------
    # 2. Measure BEFORE optimization
    # ---------------------------------------------------------
    print("\nMeasuring BEFORE optimization...")

    before = measure_process(PID)

    print(f"CPU before: {before['cpu']} %")
    print(f"Memory before: {before['memory']:.2f} %")

    # ---------------------------------------------------------
    # 3. Lower priority
    # ---------------------------------------------------------
    print("\nApplying optimization...")

    lower_priority(PID)

    priority_after = process.nice()

    print(f"Priority after optimization: {priority_after}")

    # ---------------------------------------------------------
    # 4. Measure AFTER optimization
    # ---------------------------------------------------------
    print("\nMeasuring AFTER optimization...")

    after = measure_process(PID)

    print(f"CPU after: {after['cpu']} %")
    print(f"Memory after: {after['memory']:.2f} %")

    # ---------------------------------------------------------
    # 5. Restore original priority
    # ---------------------------------------------------------
    print("\nRestoring original priority...")

    restore_priority(PID, priority_before)

    restored = process.nice() == priority_before

    print(f"Priority restored: {process.nice()}")
    print(f"Rollback successful: {restored}")

    # ---------------------------------------------------------
    # 6. Save complete experiment
    # ---------------------------------------------------------
    log_optimization(
        pid=PID,
        process_name=process.name(),
        cpu_before=before["cpu"],
        memory_before=before["memory"],
        priority_before=priority_before,
        priority_after=priority_after,
        cpu_after=after["cpu"],
        memory_after=after["memory"],
        restored=restored
    )

    print("\nOptimization history saved successfully.")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


except psutil.NoSuchProcess:
    print(f"\nProcess with PID {PID} no longer exists.")

except psutil.AccessDenied:
    print(f"\nAccess denied while accessing PID {PID}.")

except Exception as e:
    print(f"\nError: {e}")