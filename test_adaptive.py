from monitor import get_processes
from adaptive_analyzer import AdaptiveAnalyzer


# PID of the controlled test workload
TEST_PID = 18368

analyzer = AdaptiveAnalyzer(
    cpu_threshold=20,
    memory_threshold=5,
    required_checks=3
)


print("\n" + "=" * 90)
print("ADAPTIVE RESOURCE ANALYSIS")
print("=" * 90)

print(f"Monitoring test workload PID: {TEST_PID}")

for check in range(5):

    print(
        f"\n--- Monitoring Check {check + 1} ---"
    )

    processes = get_processes()

    # Find our specific test workload
    target = None

    for process in processes:

        if process["pid"] == TEST_PID:
            target = process
            break

    if target is None:

        print(
            f"Process {TEST_PID} was not found."
        )

        break

    result = analyzer.analyze(
        target
    )

    print(
        f"Process : {target['name']}"
    )

    print(
        f"CPU     : {target['cpu']:.1f}%"
    )

    print(
        f"Memory  : {target['memory']:.1f}%"
    )

    print(
        f"Category: {result['category']}"
    )

    print(
        f"Reason  : {result['reason']}"
    )

    print(
        f"Candidate: {result['safe_candidate']}"
    )


print("\n" + "=" * 90)
print("ADAPTIVE ANALYSIS COMPLETE")
print("=" * 90)