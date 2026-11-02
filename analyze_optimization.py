import csv


HISTORY_FILE = "optimization_history.csv"


def load_valid_trials():
    """
    Load only valid optimization trials.

    Records where both CPU measurements are 0 are
    ignored because they were integration tests.
    """

    trials = []

    with open(HISTORY_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cpu_before = float(row["cpu_before"])
            cpu_after = float(row["cpu_after"])

            if cpu_before == 0 and cpu_after == 0:
                continue

            trials.append({
                "cpu_before": cpu_before,
                "cpu_after": cpu_after,
                "memory_before": float(row["memory_before"]),
                "memory_after": float(row["memory_after"]),
                "restored": row["restored"].lower() == "true"
            })

    return trials


trials = load_valid_trials()

print("=" * 70)
print("OPTIMIZATION PERFORMANCE ANALYSIS")
print("=" * 70)

print(f"\nValid optimization trials: {len(trials)}")

if not trials:
    print("No valid trials found.")
    exit()


# ---------------------------------------------------------
# Calculate averages
# ---------------------------------------------------------

avg_cpu_before = sum(t["cpu_before"] for t in trials) / len(trials)
avg_cpu_after = sum(t["cpu_after"] for t in trials) / len(trials)

avg_memory_before = sum(
    t["memory_before"] for t in trials
) / len(trials)

avg_memory_after = sum(
    t["memory_after"] for t in trials
) / len(trials)


# ---------------------------------------------------------
# CPU improvement statistics
# ---------------------------------------------------------

cpu_decreased = sum(
    1 for t in trials
    if t["cpu_after"] < t["cpu_before"]
)

cpu_increased = sum(
    1 for t in trials
    if t["cpu_after"] > t["cpu_before"]
)

cpu_unchanged = sum(
    1 for t in trials
    if t["cpu_after"] == t["cpu_before"]
)


# ---------------------------------------------------------
# Rollback statistics
# ---------------------------------------------------------

successful_rollbacks = sum(
    1 for t in trials
    if t["restored"]
)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print("\nCPU RESULTS")
print("-" * 70)

print(f"Average CPU before optimization : {avg_cpu_before:.2f}%")
print(f"Average CPU after optimization  : {avg_cpu_after:.2f}%")

print(f"\nCPU decreased in {cpu_decreased} trial(s)")
print(f"CPU increased in {cpu_increased} trial(s)")
print(f"CPU unchanged in {cpu_unchanged} trial(s)")


print("\nMEMORY RESULTS")
print("-" * 70)

print(f"Average memory before : {avg_memory_before:.2f}%")
print(f"Average memory after  : {avg_memory_after:.2f}%")


print("\nROLLBACK RESULTS")
print("-" * 70)

print(
    f"Successful rollbacks: "
    f"{successful_rollbacks}/{len(trials)}"
)


print("\nTRIAL DETAILS")
print("-" * 70)

for index, trial in enumerate(trials, start=1):

    print(
        f"Trial {index}: "
        f"CPU {trial['cpu_before']:.1f}% → "
        f"{trial['cpu_after']:.1f}%, "
        f"Memory {trial['memory_before']:.2f}% → "
        f"{trial['memory_after']:.2f}%, "
        f"Rollback={trial['restored']}"
    )


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)