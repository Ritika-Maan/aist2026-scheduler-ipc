from task import Job


def assign_rms_priorities(tasks):
    """Shorter period = higher priority (0 is highest). Static."""
    for i, t in enumerate(sorted(tasks, key=lambda t: t.period)):
        t.priority = i


def simulate(tasks, policy, horizon):
    """Preemptive uniprocessor sim. policy = 'RMS' or 'EDF'. Returns finished jobs."""
    if policy == "RMS":
        assign_rms_priorities(tasks)
        key = lambda j: (j.task.priority, j.release)
    elif policy == "EDF":
        key = lambda j: (j.abs_deadline, j.release)
    else:
        raise ValueError("policy must be 'RMS' or 'EDF'")

    # generate every job released before the horizon
    releases = []
    for t in tasks:
        r = t.arrival
        while r < horizon:
            releases.append(Job(t, r, r + t.deadline, t.wcet))
            r += t.period
    releases.sort(key=lambda j: j.release)

    time, i, ready, done = 0.0, 0, [], []
    while i < len(releases) or ready:
        if not ready:                       # idle: jump to next release
            time = max(time, releases[i].release)
        while i < len(releases) and releases[i].release <= time:
            ready.append(releases[i])
            i += 1

        job = min(ready, key=key)           # pick highest priority
        if job.start is None:
            job.start = time

        next_rel = releases[i].release if i < len(releases) else float("inf")
        run = min(job.remaining, next_rel - time)   # run until done or preempted
        time += run
        job.remaining -= run

        if job.remaining <= 1e-9:
            job.finish = time
            ready.remove(job)
            done.append(job)
    return done


def metrics(jobs):
    n = len(jobs)
    missed = sum(j.missed for j in jobs)
    max_late = max(j.finish - j.abs_deadline for j in jobs)
    return {"jobs": n, "missed": missed,
            "miss_rate": missed / n, "max_lateness": max_late}