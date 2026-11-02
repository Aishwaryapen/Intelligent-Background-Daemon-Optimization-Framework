import csv
import matplotlib.pyplot as plt


HISTORY_FILE = "optimization_history.csv"


cpu_before = []
cpu_after = []
trial_numbers = []


with open(HISTORY_FILE, "r", newline="") as file:
    reader = csv.DictReader(file)

    trial = 1

    for row in reader:
        before = float(row["cpu_before"])
        after = float(row["cpu_after"])

        # Ignore the invalid 0 -> 0 integration test
        if before == 0 and after == 0:
            continue

        trial_numbers.append(trial)
        cpu_before.append(before)
        cpu_after.append(after)

        trial += 1


plt.figure(figsize=(9, 5))

plt.plot(
    trial_numbers,
    cpu_before,
    marker="o",
    label="CPU Before Optimization"
)

plt.plot(
    trial_numbers,
    cpu_after,
    marker="o",
    label="CPU After Optimization"
)

plt.xlabel("Trial Number")
plt.ylabel("CPU Usage (%)")

plt.title("CPU Usage Before and After Process Optimization")

plt.xticks(trial_numbers)

plt.legend()
plt.grid(True)

plt.tight_layout()

plt.savefig("cpu_optimization_comparison.png", dpi=300)

plt.show()

print("Graph saved as:")
print("cpu_optimization_comparison.png")