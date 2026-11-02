import csv
import matplotlib.pyplot as plt

HISTORY_FILE = "optimization_history.csv"

successful = 0
failed = 0

with open(HISTORY_FILE, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cpu_before = float(row["cpu_before"])
        cpu_after = float(row["cpu_after"])

        # Ignore the integration-test record
        if cpu_before == 0 and cpu_after == 0:
            continue

        if row["restored"].strip().lower() == "true":
            successful += 1
        else:
            failed += 1

total = successful + failed

if total == 0:
    print("No valid optimization trials found.")
    raise SystemExit

success_rate = successful / total * 100
failure_rate = failed / total * 100

plt.figure(figsize=(7, 5))

plt.bar(
    ["Successful Rollbacks", "Failed Rollbacks"],
    [successful, failed]
)

plt.ylabel("Number of Trials")
plt.title(f"Process Priority Rollback Results\nSuccess Rate: {success_rate:.1f}%")

plt.tight_layout()
plt.savefig("rollback_success_rate.png", dpi=300)
plt.show()

print(f"Valid trials: {total}")
print(f"Successful rollbacks: {successful}")
print(f"Failed rollbacks: {failed}")
print(f"Rollback success rate: {success_rate:.1f}%")
print("Graph saved as rollback_success_rate.png")