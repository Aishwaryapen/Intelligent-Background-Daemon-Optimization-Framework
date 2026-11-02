import time

print("Test workload started.")
print("PID:", __import__("os").getpid())

while True:
    # Perform some CPU work
    total = 0

    for i in range(10_000_000):
        total += i * i

    time.sleep(0.2)