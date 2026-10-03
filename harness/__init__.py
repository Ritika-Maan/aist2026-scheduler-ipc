"""Experiment harness: co-simulation of core/ (scheduler) and ipc/ (IPC layer).

core/ and ipc/ are frozen and use flat imports (`from task import Task`), so both
directories are put on sys.path here. Nothing in core/ or ipc/ is modified.
Time unit throughout: milliseconds.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _sub in ("ipc", "core"):
    _p = os.path.join(ROOT, _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)
