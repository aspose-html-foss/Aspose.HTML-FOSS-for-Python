"""Root conftest.py — project-wide pytest configuration.

Conditionally ignores ``src/aspose_html/js/`` from doctest collection
when the optional ``quickjs`` package is not installed.  This satisfies
AC-9: ``pytest --doctest-modules src/aspose_html/js/`` must skip cleanly
when quickjs is absent, rather than failing with an ImportError.
"""
from __future__ import annotations

from pathlib import Path

collect_ignore_glob: list[str] = []

try:
    import quickjs  # noqa: F401
except ImportError:
    # When quickjs is absent, skip all js/ source files from doctest
    # collection.  Tests in tests/test_js/ are skipped separately via
    # pytest.importorskip("quickjs") at the top of the test module.
    _js_dir = Path(__file__).parent / "src" / "aspose_html" / "js"
    collect_ignore_glob.append(str(_js_dir / "*.py"))
