import os
import sys
from github_utils import get_latest_failed_run, fetch_workflow_logs


def get_required_env(name: str) -> str:
    """Fetch a required environment variable or exit if missing."""
    value = os.getenv(name)
    if not value:
        print(f"❌ Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def print_log_snippet(logs: dict, lines: int = 20):
    """Print the last `lines` lines of each log file."""
    for fname, content in logs.items():
        print(f"\n--- {fname} ---")
        snippet = "\n".join(content.splitlines()[-lines:])
        print(snippet)
        print("...")


def main():
    try:
        print("🚀 InferOps is running")

        # Required GitHub info
        repo = get_required_env("GITHUB_REPOSITORY")
        branch = os.getenv("GITHUB_REF_NAME", "main")
        token = get_required_env("INPUT_GITHUB_TOKEN")

        # Step 1: Find latest failed run
        run_id = get_latest_failed_run(repo, token, branch)
        if not run_id:
            print("✅ No failed runs found. Nothing to do.")
            return  # exit code 0 is fine here

        print(f"🔍 Latest failed run_id: {run_id}")

        # Step 2: Fetch logs
        logs = fetch_workflow_logs(repo, run_id, token)
        print(f"✅ Fetched {len(logs)} log files")

        # Step 3: Print snippet from each log (last 20 lines)
        print_log_snippet(logs, lines=20)

    except Exception as e:
        # Catch any unexpected error, print to stderr, fail the action
        print(f"💥 Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
