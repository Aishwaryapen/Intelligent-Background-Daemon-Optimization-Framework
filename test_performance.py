import psutil

from performance import measure_process
from optimizer import lower_priority, restore_priority


# Use the PID of your test_workload.py
PID = 18368


process = psutil.Process(PID)

print("=" * 60)
print("PERFORMANCE MEASUREMENT")
print("=" * 60)

print("Process:", process.name())
print("PID:", PID)

# --------------------------------
# BEFORE OPTIMIZATION
# --------------------------------

print("\nMeasuring BEFORE optimization...")

before = measure_process(PID)

print("CPU:", round(before["cpu"], 2), "%")
print("Memory:", round(before["memory"], 2), "%")


# --------------------------------
# OPTIMIZATION
# --------------------------------

original_priority = process.nice()

print("\nApplying optimization...")

lower_priority(PID)

print("Priority changed to:", process.nice())


# --------------------------------
# AFTER OPTIMIZATION
# --------------------------------

print("\nMeasuring AFTER optimization...")

after = measure_process(PID)

print("CPU:", round(after["cpu"], 2), "%")
print("Memory:", round(after["memory"], 2), "%")


# --------------------------------
# RESTORE
# --------------------------------

print("\nRestoring original priority...")

restore_priority(PID, original_priority)

print("Priority restored to:", process.nice())


# --------------------------------
# SUMMARY
# --------------------------------

print("\n" + "=" * 60)
print("PERFORMANCE SUMMARY")
print("=" * 60)

print("CPU before :", round(before["cpu"], 2), "%")
print("CPU after  :", round(after["cpu"], 2), "%")

print("Memory before:", round(before["memory"], 2), "%")
print("Memory after :", round(after["memory"], 2), "%")

print("\nOptimization test completed.")