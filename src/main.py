import os
from github_utils import fetch_workflow_logs


def get_required_env(name: str):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def main():
    print("🚀 InferOps is running")

    repo = get_required_env("GITHUB_REPOSITORY")
    run_id = get_required_env("GITHUB_RUN_ID")
    token = get_required_env("INPUT_GITHUB_TOKEN")  # GitHub token input

    logs = fetch_workflow_logs(repo, run_id, token)

    print(f"✅ Fetched {len(logs)} log files")
    # Print first 500 chars of each log
    for fname, content in logs.items():
        print(f"--- {fname} ---")
        print(content[:500])
        print("...")


if __name__ == "__main__":
    main()
