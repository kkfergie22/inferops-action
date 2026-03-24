import os
import httpx
import zipfile
import io

GITHUB_API_URL = "https://api.github.com"


def get_latest_failed_run(repo: str, token: str, branch: str = "main") -> str:
    """
    Get the run_id of the latest failed workflow on the given branch.
    """
    url = f"{GITHUB_API_URL}/repos/{repo}/actions/runs"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"branch": branch, "status": "failure", "per_page": 1}

    with httpx.Client(timeout=30) as client:
        r = client.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        runs = data.get("workflow_runs", [])
        if not runs:
            raise RuntimeError(f"No failed runs found for branch {branch}")
        return runs[0]["id"]


def fetch_workflow_logs(repo: str, run_id: str, token: str) -> dict:
    """
    Fetch workflow logs for a given run_id.
    Returns a dict of filename -> log content (string).
    """
    url = f"{GITHUB_API_URL}/repos/{repo}/actions/runs/{run_id}/logs"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    # follow_redirects=True handles GitHub 302 redirects automatically
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()

    # GitHub returns a zip file
    z = zipfile.ZipFile(io.BytesIO(response.content))
    logs = {}
    for fname in z.namelist():
        with z.open(fname) as f:
            logs[fname] = f.read().decode(errors="ignore")
    return logs

