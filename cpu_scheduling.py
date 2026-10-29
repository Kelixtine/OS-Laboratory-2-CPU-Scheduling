
# ============================================================
# CPU Scheduling Algorithms
# BCA151 - Operating Systems Laboratory
# ============================================================

# Modified dataset for FCFS, SJF, Priority, and Round Robin
PROCESSES = [
    {"pid": "P1", "at": 0, "bt": 5, "priority": 3},
    {"pid": "P2", "at": 0, "bt": 3, "priority": 1},
    {"pid": "P3", "at": 0, "bt": 7, "priority": 4},
    {"pid": "P4", "at": 0, "bt": 2, "priority": 2},
]

# Separate dataset for SRTF
SRTF_PROCESSES = [
    {"pid": "P1", "at": 0, "bt": 8, "priority": 2},
    {"pid": "P2", "at": 1, "bt": 4, "priority": 1},
    {"pid": "P3", "at": 2, "bt": 2, "priority": 4},
    {"pid": "P4", "at": 3, "bt": 1, "priority": 3},
]

# Change this value to 4 and 1 for Step 22
RR_QUANTUM = 2


def fcfs(processes):
    """First Come, First Served scheduling."""
    time = 0
    gantt = []
    results = []

    for p in sorted(processes, key=lambda x: (x["at"], x["pid"])):
        start = max(time, p["at"])
        finish = start + p["bt"]

        gantt.append((p["pid"], start, finish))
        results.append({
            **p,
            "ct": finish,
            "first_start": start,
        })
        time = finish

    return results, gantt


def non_preemptive(processes, mode="sjf"):
    """Non-preemptive Shortest Job First or Priority scheduling."""
    time = 0
    remaining = [p.copy() for p in processes]
    results = []
    gantt = []

    while remaining:
        ready = [p for p in remaining if p["at"] <= time]

        if not ready:
            time = min(p["at"] for p in remaining)
            ready = [p for p in remaining if p["at"] <= time]

        if mode == "sjf":
            selected = min(
                ready,
                key=lambda p: (p["bt"], p["at"], p["pid"])
            )
        else:
            # Lower priority number means higher priority
            selected = min(
                ready,
                key=lambda p: (
                    p["priority"], p["at"], p["pid"]
                )
            )

        start = time
        finish = start + selected["bt"]

        gantt.append((selected["pid"], start, finish))
        results.append({
            **selected,
            "ct": finish,
            "first_start": start,
        })

        time = finish
        remaining.remove(selected)

    return results, gantt


def round_robin(processes, quantum):
    """Round Robin scheduling."""
    if quantum <= 0:
        raise ValueError("Time quantum must be greater than zero.")

    ordered = sorted(processes, key=lambda p: (p["at"], p["pid"]))
    remaining = {p["pid"]: p["bt"] for p in ordered}
    first_start = {}
    completion = {}
    gantt = []
    ready_queue = []
    index = 0
    time = 0

    while index < len(ordered) or ready_queue:
        if not ready_queue:
            time = max(time, ordered[index]["at"])

            while index < len(ordered) and ordered[index]["at"] <= time:
                ready_queue.append(ordered[index]["pid"])
                index += 1

        pid = ready_queue.pop(0)
        process = next(p for p in ordered if p["pid"] == pid)

        if pid not in first_start:
            first_start[pid] = time

        start = time
        run_time = min(quantum, remaining[pid])
        time += run_time
        remaining[pid] -= run_time

        gantt.append((pid, start, time))

        # Add processes arriving during this time slice
        while index < len(ordered) and ordered[index]["at"] <= time:
            ready_queue.append(ordered[index]["pid"])
            index += 1

        if remaining[pid] > 0:
            ready_queue.append(pid)
        else:
            completion[pid] = time

    results = []

    for p in ordered:
        results.append({
            **p,
            "ct": completion[p["pid"]],
            "first_start": first_start[p["pid"]],
        })

    return results, gantt


def srtf(processes):
    """Shortest Remaining Time First scheduling."""
    ordered = sorted(processes, key=lambda p: (p["at"], p["pid"]))
    remaining = {p["pid"]: p["bt"] for p in ordered}
    first_start = {}
    completion = {}
    gantt = []
    time = 0
    completed = 0
    current_pid = None
    segment_start = 0

    while completed < len(ordered):
        ready = [
            p for p in ordered
            if p["at"] <= time and remaining[p["pid"]] > 0
        ]

        if not ready:
            if current_pid is not None:
                gantt.append((current_pid, segment_start, time))
                current_pid = None

            time += 1
            continue

        selected = min(
            ready,
            key=lambda p: (
                remaining[p["pid"]], p["at"], p["pid"]
            )
        )
        pid = selected["pid"]

        if pid != current_pid:
            if current_pid is not None:
                gantt.append((current_pid, segment_start, time))

            current_pid = pid
            segment_start = time

        if pid not in first_start:
            first_start[pid] = time

        remaining[pid] -= 1
        time += 1

        if remaining[pid] == 0:
            completion[pid] = time
            completed += 1
            gantt.append((current_pid, segment_start, time))
            current_pid = None

    results = []

    for p in ordered:
        results.append({
            **p,
            "ct": completion[p["pid"]],
            "first_start": first_start[p["pid"]],
        })

    return results, gantt


def display(title, results, gantt):
    """Display Gantt chart, process metrics, and averages."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    print("\nGantt Chart:")
    print(" | ".join(
        f"{pid} [{start}-{finish}]"
        for pid, start, finish in gantt
    ))

    print("\nProcess Metrics:")
    print(
        f"{'PID':<8}{'AT':>5}{'BT':>6}"
        f"{'CT':>6}{'TAT':>7}{'WT':>7}{'RT':>7}"
    )

    total_wt = 0
    total_tat = 0
    total_rt = 0

    for p in sorted(results, key=lambda x: x["pid"]):
        tat = p["ct"] - p["at"]
        wt = tat - p["bt"]
        rt = p["first_start"] - p["at"]

        total_wt += wt
        total_tat += tat
        total_rt += rt

        print(
            f"{p['pid']:<8}{p['at']:>5}{p['bt']:>6}"
            f"{p['ct']:>6}{tat:>7}{wt:>7}{rt:>7}"
        )

    count = len(results)

    print(f"\nAverage Waiting Time: {total_wt / count:.2f} ms")
    print(f"Average Turnaround Time: {total_tat / count:.2f} ms")
    print(f"Average Response Time: {total_rt / count:.2f} ms")


def main():
    results, gantt = fcfs(PROCESSES)
    display("1. FCFS", results, gantt)

    results, gantt = non_preemptive(PROCESSES, mode="sjf")
    display("2. NON-PREEMPTIVE SJF", results, gantt)

    results, gantt = non_preemptive(PROCESSES, mode="priority")
    display("3. NON-PREEMPTIVE PRIORITY", results, gantt)

    results, gantt = round_robin(PROCESSES, quantum=RR_QUANTUM)
    display(
        f"4. ROUND ROBIN (QUANTUM = {RR_QUANTUM})",
        results,
        gantt,
    )

    results, gantt = srtf(SRTF_PROCESSES)
    display(
        "5. SRTF (SEPARATE ARRIVAL-TIME DATASET)",
        results,
        gantt,
    )


if __name__ == "__main__":
    main()
