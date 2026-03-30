import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from github_utils import extract_error_lines

def test_extract_error_lines_basic():
    logs = {
        "job_log.txt": "line1\nline2\nError: missing file\nfailed to run\nline5"
    }
    extracted = extract_error_lines(logs, 100)
    assert "Error:" in extracted
    assert "failed" in extracted

def test_extract_error_lines_no_errors():
    logs = {
        "job_log.txt": "line1\nline2\nline3"
    }
    extracted = extract_error_lines(logs, 100)
    assert "last lines" in extracted
    assert "line3" in extracted
