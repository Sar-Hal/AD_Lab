import time
import matplotlib.pyplot as plt
from ping3 import ping

TARGET = "10.2.0.84"   # change host here
INTERVAL = 1           # seconds between pings
WINDOW = 100           # points to keep on graph

times = []
latencies = []

plt.ion()
fig, ax = plt.subplots()

start_time = time.time()

print(f"Pinging {TARGET}... (Ctrl+C to stop)")

while True:
    try:
        t0 = time.time()

        delay = ping(TARGET, timeout=2)

        now = time.time() - start_time

        if delay is None:
            latency_ms = None
            print(f"[{now:.1f}s] Timeout")
        else:
            latency_ms = delay * 1000
            print(f"[{now:.1f}s] {latency_ms:.2f} ms")

        times.append(now)
        latencies.append(latency_ms if latency_ms is not None else 0)

        # Keep sliding window
        if len(times) > WINDOW:
            times.pop(0)
            latencies.pop(0)

        # Plot
        ax.clear()
        ax.plot(times, latencies)
        ax.set_title(f"Live Ping Latency → {TARGET}")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Latency (ms)")
        ax.grid()

        plt.pause(0.01)

        time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\nStopped.")
        break
