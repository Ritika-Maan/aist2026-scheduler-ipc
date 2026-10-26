import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import harness  # noqa: E402,F401  (puts core/ and ipc/ on sys.path)
