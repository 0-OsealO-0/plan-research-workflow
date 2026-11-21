"""Shared runtime helpers for the plan-research-workflow scripts.

The scripts must run with whatever Python the user has. Only the .docx
features need python-docx; when the current interpreter lacks it, re-exec the
same script with the DSH bundled runtime that ships python-docx.
"""

import os
import subprocess
import sys

def _dsh_home() -> str:
    env = os.environ.get("DSH_HOME")
    if env:
        return env
    return os.path.join(os.path.expanduser("~"), ".dsh")


BUNDLED_PYTHON = os.path.join(
    _dsh_home(), "dsh-runtimes", "dsh-primary-runtime",
    "dependencies", "python", "python.exe",
)
INSTALL_HINT = (
    "此功能需要 python-docx。\n"
    "任选其一：pip install python-docx\n"
    "或改读 Markdown 交付（--format md）。"
)


def _candidates():
    env = os.environ.get("PAPERFLOW_PYTHON")
    if env:
        yield env
    yield BUNDLED_PYTHON


def ensure_docx():
    """Return the docx module, re-running this script under a runtime that has it."""
    try:
        import docx  # noqa: F401

        return docx
    except ImportError:
        pass

    if os.environ.get("PAPERFLOW_REEXEC") != "1":
        me = os.path.abspath(sys.executable)
        script = os.path.abspath(sys.argv[0]) if sys.argv and sys.argv[0] else ""
        if not script or not os.path.isfile(script):
            sys.stderr.write(
                INSTALL_HINT
                + "\n[note] 当前解释器缺 python-docx，且不是从脚本文件运行（如 python -c），"
                  "无法自动切换解释器。请把代码写成 .py 文件再运行。\n"
            )
            raise SystemExit(2)
        for py in _candidates():
            if not py or not os.path.isfile(py):
                continue
            if os.path.abspath(py) == me:
                continue
            env = dict(os.environ, PAPERFLOW_REEXEC="1")
            code = subprocess.call([py, script] + sys.argv[1:], env=env)
            raise SystemExit(code)

    sys.stderr.write(INSTALL_HINT + "\n")
    raise SystemExit(2)
