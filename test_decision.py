from monitor import get_processes
from analyzer import analyze_processes
from decision_engine import get_optimization_candidates


processes = get_processes()

results = analyze_processes(processes)

candidates = get_optimization_candidates(results)


print("\n" + "=" * 80)
print("OPTIMIZATION CANDIDATES")
print("=" * 80)

if not candidates:
    print("No processes currently require optimization.")
else:

    print(
        f"{'PID':<8}"
        f"{'PROCESS':<30}"
        f"{'CPU %':<10}"
        f"{'MEM %':<10}"
        f"{'DECISION'}"
    )

    print("-" * 80)

    for process in candidates:

        print(
            f"{process['pid']:<8}"
            f"{str(process['name'])[:28]:<30}"
            f"{process['cpu']:<10.1f}"
            f"{process['memory']:<10.1f}"
            f"SAFE TO OPTIMIZE"
        )