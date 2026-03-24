import os
import httpx
import zipfile
import io

GITHUB_API_URL = "https://api.github.com"


def fetch_workflow_logs(repo: str, run_id: str, token: str) -> dict:
    """
    Fetch workflow logs for a given run_id and return a dictionary of filename -> content.
    """
    url = f"{GITHUB_API_URL}/repos/{repo}/actions/runs/{run_id}/logs"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    with httpx.Client(timeout=60) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()

    # Zip is returned as bytes
    z = zipfile.ZipFile(io.BytesIO(response.content))
    logs = {}
    for file_name in z.namelist():
        with z.open(file_name) as f:
            logs[file_name] = f.read().decode(errors="ignore")
    return logs
