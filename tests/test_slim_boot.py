"""The deployed app needs only requirements.txt: boot it and visit every page.

Runs in a fresh interpreter so a heavy package imported by some other test
cannot hide a missing or unwanted dependency. The CI `slim` job installs only
requirements.txt plus pytest and runs this file; it needs nothing else.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = ("pymc", "arviz", "scipy", "pytensor", "matplotlib", "sklearn")

SCRIPT = """
import json, sys
from streamlit.testing.v1 import AppTest

def _page(name):
    import app
    from dashboard.theme import apply_theme
    from dashboard.utils.session_manager import AppState
    AppState.init()
    apply_theme(AppState.theme())
    dict((t, fn) for t, _, fn in app.PAGES)[name]()

results = {}
shell = AppTest.from_file("expert_dashboard.py", default_timeout=60).run()
results["expert_dashboard.py"] = [str(e.value) for e in shell.exception]
import app
for title, _, _ in app.PAGES:
    at = AppTest.from_function(_page, args=(title,), default_timeout=60).run()
    results[title] = [str(e.value) for e in at.exception]
heavy = sorted(m for m in %r if m in sys.modules)
print(json.dumps({"results": results, "heavy": heavy}))
""" % (
    FORBIDDEN,
)


def test_slim_install_boots_and_every_page_renders(tmp_path):
    script = tmp_path / "boot_pages.py"  # from_function needs a real source file
    script.write_text(SCRIPT)
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    assert out["heavy"] == [], f"runtime imported model-only packages: {out['heavy']}"
    assert set(out["results"]) >= {
        "expert_dashboard.py",
        "Predict",
        "Neighborhoods",
        "How the model works",
        "Diagnostics",
        "Data notes",
    }
    assert all(errs == [] for errs in out["results"].values()), out["results"]
