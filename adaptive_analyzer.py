import time


class AdaptiveAnalyzer:

    def __init__(
        self,
        cpu_threshold=20,
        memory_threshold=5,
        required_checks=3
    ):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.required_checks = required_checks

        # Stores consecutive high-resource observations
        self.history = {}

    def analyze(self, process):
        """
        Analyze a process using recent resource observations.
        """

        pid = process["pid"]
        cpu = process["cpu"]
        memory = process["memory"]

        # Create history entry for a new process
        if pid not in self.history:
            self.history[pid] = {
                "high_cpu_checks": 0,
                "high_memory_checks": 0,
                "last_seen": time.time()
            }

        record = self.history[pid]

        record["last_seen"] = time.time()

        # Check CPU usage
        if cpu >= self.cpu_threshold:
            record["high_cpu_checks"] += 1
        else:
            record["high_cpu_checks"] = 0

        # Check memory usage
        if memory >= self.memory_threshold:
            record["high_memory_checks"] += 1
        else:
            record["high_memory_checks"] = 0

        # Persistent high CPU
        if record["high_cpu_checks"] >= self.required_checks:
            return {
                "category": "PERSISTENT HIGH CPU",
                "reason": (
                    f"CPU remained above "
                    f"{self.cpu_threshold}% for "
                    f"{record['high_cpu_checks']} checks"
                ),
                "safe_candidate": True
            }

        # Persistent high memory
        if record["high_memory_checks"] >= self.required_checks:
            return {
                "category": "PERSISTENT HIGH MEMORY",
                "reason": (
                    f"Memory remained above "
                    f"{self.memory_threshold}% for "
                    f"{record['high_memory_checks']} checks"
                ),
                "safe_candidate": True
            }

        # Temporary spike
        if cpu >= self.cpu_threshold:
            return {
                "category": "TEMPORARY HIGH CPU",
                "reason": "CPU usage is currently high but not persistent",
                "safe_candidate": False
            }

        if memory >= self.memory_threshold:
            return {
                "category": "TEMPORARY HIGH MEMORY",
                "reason": "Memory usage is currently high but not persistent",
                "safe_candidate": False
            }

        return {
            "category": "NORMAL",
            "reason": "Resource usage is within normal range",
            "safe_candidate": False
        }

    def cleanup(self, active_pids):
        """
        Remove processes that are no longer running.
        """

        active_pids = set(active_pids)

        old_pids = [
            pid
            for pid in self.history
            if pid not in active_pids
        ]

        for pid in old_pids:
            del self.history[pid]