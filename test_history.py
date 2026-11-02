from optimization_history import log_optimization, get_history


print("=" * 60)
print("OPTIMIZATION HISTORY TEST")
print("=" * 60)

log_optimization(
    pid=9296,
    process_name="python.exe",
    cpu_before=85.4,
    memory_before=0.13,
    priority_before=32,
    priority_after=16384,
    cpu_after=98.9,
    memory_after=0.13,
    restored=True
)

print("\nOptimization record added successfully.")

history = get_history()

print(f"\nTotal history records: {len(history)}")

print("\nLatest record:")
print(history[-1])

print("\nHistory test completed.")