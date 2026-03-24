import os
from github_utils import get_latest_failed_run, fetch_workflow_logs
import httpx


def get_required_env(name: str):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def get_workflow_run_status(repo: str, run_id: int, token: str):
    """
    Fetch the workflow run status and conclusion from GitHub API.
    """
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}"
    headers = {"Authorization": f"token {token}"}

    with httpx.Client(timeout=10.0) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # status: "completed", "in_progress", "queued"
        # conclusion: "success", "failure", "cancelled", "neutral", "skipped"
        return data["status"], data.get("conclusion")


def main():
    print("🚀 InferOps is running")

    # Required GitHub info
    repo = get_required_env("GITHUB_REPOSITORY")
    branch = os.getenv("GITHUB_REF_NAME", "main")  # fallback to main
    token = get_required_env("INPUT_GITHUB_TOKEN")

    # Step 1: Find latest failed run
    run_id = get_latest_failed_run(repo, token, branch)
    print(f"🔍 Latest failed run_id: {run_id}")

    # Step 2: Fetch logs
    try:
        logs = fetch_workflow_logs(repo, run_id, token)
        print(f"✅ Fetched {len(logs)} log files")
    except Exception as e:
        print(f"❌ Failed to fetch logs: {e}")
        logs = {}

    # Step 3: Detect errors in logs
    errors_found = []
    for fname, content in logs.items():
        snippet = "\n".join(content.splitlines()[-20:])
        if "error" in snippet.lower() or "failed" in snippet.lower():
            errors_found.append(fname)

    # Step 4: Check workflow run conclusion
    try:
        status, conclusion = get_workflow_run_status(repo, run_id, token)
    except Exception as e:
        print(f"❌ Failed to fetch workflow status: {e}")
        status, conclusion = "unknown", "unknown"

    # Step 5: Print summary
    print("\n📝 Summary:")
    print(f"Status: {status}, Conclusion: {conclusion}")
    if conclusion != "success" or errors_found:
        print(f"❌ Workflow failed or errors found in logs: {errors_found}")
        # Here you could set a proper exit code to fail the step
        os._exit(1)
    else:
        print("✅ Workflow passed with no errors detected")

    # Step 6: Optional snippet display
    for fname, content in logs.items():
        print(f"\n--- {fname} ---")
        snippet = "\n".join(content.splitlines()[-20:])
        print(snippet)
        print("...")


if __name__ == "__main__":
    main()
