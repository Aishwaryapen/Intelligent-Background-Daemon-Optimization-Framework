import csv
import os
from datetime import datetime


HISTORY_FILE = "optimization_history.csv"


def log_optimization(
    pid,
    process_name,
    cpu_before,
    memory_before,
    priority_before,
    priority_after,
    cpu_after,
    memory_after,
    restored
):
    file_exists = os.path.exists(HISTORY_FILE)

    with open(HISTORY_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "pid",
                "process_name",
                "cpu_before",
                "memory_before",
                "priority_before",
                "priority_after",
                "cpu_after",
                "memory_after",
                "restored"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pid,
            process_name,
            round(cpu_before, 2),
            round(memory_before, 2),
            priority_before,
            priority_after,
            round(cpu_after, 2),
            round(memory_after, 2),
            restored
        ])


def get_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)