import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """After a full test run, print the ONE TABLE of the eval report (``barrels.report``, the same table as
    ``python barrels/tools/report.py``): what runs today vs the v1 front end, on the train frames only — test
    frames are refused inside ``report.run_arm``. It is about 10 s of segmenting and detecting, so it runs only
    when the whole suite ran (no ``-k`` / ``-m``, no single file or test named, not ``--collect-only``), is
    skipped at once when the data or the model files are missing, and is switched off with ``BARRELS_NO_REPORT=1``.
    The table never changes the test result: any failure in here is reported as one line."""
    if os.environ.get("BARRELS_NO_REPORT"):
        return
    opt = config.option
    if getattr(opt, "keyword", "") or getattr(opt, "markexpr", "") or getattr(opt, "collectonly", False):
        return
    if any("::" in a or a.endswith(".py") for a in config.args):
        return
    try:
        import time
        from barrels import io, report as rp
        cand, base = rp.default_arms()
        if not (Path(cand.model_path).exists() and Path(base.model_path).exists() and io.RAW_DIR.is_dir() and rp.labeled_stems()):
            return
        t0 = time.time()
        rep = rp.make_report(cand, base)
        if not rep.rows:
            return
        terminalreporter.write_sep("=", "eval report: candidate (today) vs baseline (v1 front end), train frames")
        terminalreporter.write_line(rp.format_text(rep))
        terminalreporter.write_line(f"(eval report: {time.time() - t0:.1f} s; BARRELS_NO_REPORT=1 turns it off; python barrels/tools/report.py --help for other arms)")
    except Exception as e:  # noqa: BLE001 — the report must never break the suite
        terminalreporter.write_line(f"eval report skipped: {type(e).__name__}: {e}")
