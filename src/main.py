import os
from github_utils import get_latest_failed_run, fetch_workflow_logs


def get_required_env(name: str):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def main():
    print("🚀 InferOps is running")

    # Required GitHub info
    repo = get_required_env("GITHUB_REPOSITORY")
    branch = os.getenv("GITHUB_REF_NAME", "main")  # fallback to main branch
    token = get_required_env("INPUT_GITHUB_TOKEN")

    # Step 1: Find latest failed run
    run_id = get_latest_failed_run(repo, token, branch)
    print(f"🔍 Latest failed run_id: {run_id}")

    # Step 2: Fetch logs
    logs = fetch_workflow_logs(repo, run_id, token)
    print(f"✅ Fetched {len(logs)} log files")

    # Step 3: Print snippet from each log
    for fname, content in logs.items():
        print(f"\n--- {fname} ---")
        snippet = "\n".join(content.splitlines()[-20:])  # last 20 lines
        print(snippet)
        print("...")


if __name__ == "__main__":
    main()
