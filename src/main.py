import os
from github_utils import get_latest_failed_run, fetch_workflow_logs
import openai


def get_required_env(name: str):
    """Fetch required environment variable or raise error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def extract_errors(logs: dict[str, str]) -> dict[str, list[str]]:
    """
    Extract lines containing 'ERROR' or 'FAIL' from workflow logs.
    Returns a dict mapping file names to lists of error lines.
    """
    error_lines = {}
    for fname, content in logs.items():
        lines = [
            line for line in content.splitlines() if "ERROR" in line or "FAIL" in line
        ]
        if lines:
            error_lines[fname] = lines
    return error_lines


def summarize_errors(errors: dict[str, list[str]]) -> str:
    """
    Summarize errors using OpenAI API. Returns a concise summary.
    """
    openai_api_key = os.getenv("INPUT_OPENAI_API_KEY")
    if not openai_api_key:
        return "⚠️ OpenAI API key not provided. Skipping summary."

    openai.api_key = openai_api_key
    text_to_summarize = "\n".join(
        f"{fname}:\n" + "\n".join(lines[-10:]) for fname, lines in errors.items()
    )

    prompt = f"Summarize the following CI workflow errors in plain English:\n{text_to_summarize}"

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def main():
    print("🚀 InferOps is running")

    # Required GitHub info
    repo = get_required_env("GITHUB_REPOSITORY")
    branch = os.getenv("GITHUB_REF_NAME", "main")
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

    # Step 3: Extract errors
    errors = extract_errors(logs)
    total_errors = sum(len(lines) for lines in errors.values())
    print(f"⚠️ Total errors found: {total_errors}")

    # Step 4: Summarize errors
    summary = summarize_errors(errors) if errors else "✅ No errors found."
    print("\n📝 Summary:\n", summary)

    # Step 5: Set GitHub Action outputs
    print(f"::set-output name=error_count::{total_errors}")
    print(f"::set-output name=summary::{summary}")

    # Optional: fail workflow if too many errors
    if total_errors > 10:
        raise RuntimeError(f"❌ Workflow failed with {total_errors} errors")


if __name__ == "__main__":
    main()
