import csv
import time
from datetime import datetime
import psutil

from adaptive_analyzer import AdaptiveAnalyzer


OUTPUT_FILE = "process_monitoring_dataset.csv"

FIELDS = [
    "timestamp",
    "pid",
    "process_name",
    "cpu_percent",
    "memory_percent",
    "status",
    "category",
    "candidate"
]

analyzer = AdaptiveAnalyzer()

# Create CSV with header
with open(OUTPUT_FILE, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=FIELDS)
    writer.writeheader()

print("Dataset collection started.")
print("Data will be saved to:", OUTPUT_FILE)
print("Press Ctrl+C to stop.\n")

cycle = 0

try:
    while True:
        cycle += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rows = []

        for process in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent", "status"]
        ):
            try:
                pid = process.info["pid"]
                name = process.info["name"]
                cpu = process.info["cpu_percent"]
                memory = process.info["memory_percent"]
                status = process.info["status"]

                # IMPORTANT:
                # adaptive_analyzer.py expects "cpu" and "memory"
                process_data = {
                    "pid": pid,
                    "name": name,
                    "cpu": cpu,
                    "memory": memory,
                    "status": status
                }

                result = analyzer.analyze(process_data)

                category = result.get("category", "")
                candidate = result.get("safe_candidate", False)

                rows.append({
                    "timestamp": timestamp,
                    "pid": pid,
                    "process_name": name,
                    "cpu_percent": cpu,
                    "memory_percent": memory,
                    "status": status,
                    "category": category,
                    "candidate": candidate
                })

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
                KeyError
            ):
                continue

        # Save this cycle
        with open(OUTPUT_FILE, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writerows(rows)

        print(
            f"Cycle {cycle}: "
            f"collected {len(rows)} process observations"
        )

        time.sleep(3)

except KeyboardInterrupt:
    print("\nDataset collection stopped.")
    print("Dataset saved as:", OUTPUT_FILE)