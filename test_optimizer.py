import time
import psutil

from optimizer import lower_priority, restore_priority


# CHANGE THIS to the PID printed by test_workload.py
PID = 18368


process = psutil.Process(PID)

print("=" * 60)
print("PROCESS OPTIMIZATION TEST")
print("=" * 60)

print("Process:", process.name())
print("PID:", PID)

# Save the original priority
original_priority = process.nice()

print("Original priority:", original_priority)

print("\nLowering process priority...")

lower_priority(PID)

print("New priority:", process.nice())

print("\nOptimization applied successfully.")

time.sleep(5)

print("\nRestoring original priority...")

restore_priority(PID, original_priority)

print("Restored priority:", process.nice())

print("\nRollback completed.")