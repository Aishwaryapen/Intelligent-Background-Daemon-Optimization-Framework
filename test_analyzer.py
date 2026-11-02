from monitor import get_processes
from analyzer import analyze_processes


processes = get_processes()

results = analyze_processes(processes)

print("\n" + "=" * 80)
print("RESOURCE ANALYSIS")
print("=" * 80)

print(
    f"{'PID':<8}"
    f"{'PROCESS':<30}"
    f"{'CPU %':<10}"
    f"{'MEM %':<10}"
    f"{'DECISION'}"
)

print("-" * 80)

for process in results[:30]:

    print(
        f"{process['pid']:<8}"
        f"{str(process['name'])[:28]:<30}"
        f"{process['cpu']:<10.1f}"
        f"{process['memory']:<10.1f}"
        f"{process['category']}"
    )