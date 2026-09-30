from dataclasses import dataclass, field


@dataclass
class Task:
    name: str
    period: float
    wcet: float                # worst-case execution time
    deadline: float = None     # relative deadline; defaults to period
    arrival: float = 0.0       # first release time
    priority: int = 0          # lower number = higher priority (set by RMS)

    def __post_init__(self):
        if self.deadline is None:
            self.deadline = self.period

    @property
    def utilization(self):
        return self.wcet / self.period


@dataclass
class Job:
    task: Task
    release: float
    abs_deadline: float
    remaining: float
    start: float = None
    finish: float = None

    @property
    def missed(self):
        return self.finish is not None and self.finish > self.abs_deadline