import os
import sys
from github_utils import fetch_workflow_logs, extract_error_lines
from analyzer import analyze_failure
from notifier import post_github_summary, post_to_discord, post_to_slack

def get_env_or_default(name: str, default: str = "") -> str:
    return os.getenv(name, default)

def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        print(f"❌ Missing required env var: {name}")
        sys.exit(1)
    return value

def main():
    print("🚀 InferOps is analyzing the failure...")

    # Required variables
    repo = get_required_env("GITHUB_REPOSITORY")
    token = get_required_env("INPUT_GITHUB_TOKEN")
    run_id = get_required_env("GITHUB_RUN_ID")
    
    # LLM Config
    provider = get_env_or_default("INPUT_LLM_PROVIDER", "openai")
    model = get_env_or_default("INPUT_LLM_MODEL", "")
    
    api_key = get_env_or_default(f"INPUT_{provider.upper()}_API_KEY")
    if not api_key:
        print(f"❌ Missing API key for provider {provider}. Please set {provider.upper()}_API_KEY.")
        sys.exit(1)
        
    # Notification Config
    discord_url = get_env_or_default("INPUT_DISCORD_WEBHOOK_URL")
    slack_url = get_env_or_default("INPUT_SLACK_WEBHOOK_URL")
    
    # Options
    suggest_patch = get_env_or_default("INPUT_SUGGEST_PATCH", "false").lower() == "true"
    max_log_lines = int(get_env_or_default("INPUT_MAX_LOG_LINES", "200"))

    # Step 1: Fetch logs
    print(f"🔍 Fetching logs for run {run_id} in {repo}...")
    try:
        logs = fetch_workflow_logs(repo, run_id, token)
        print(f"✅ Fetched {len(logs)} log files.")
    except Exception as e:
        print(f"❌ Failed to fetch logs: {e}")
        # If we can't fetch logs, there's nothing to analyze. We shouldn't fail the build though, 
        # since it's already failed. Just exit.
        sys.exit(0)

    # Step 2: Extract relevant error lines
    error_context = extract_error_lines(logs, max_lines=max_log_lines)
    
    # Step 3: Analyze with LLM
    print(f"🧠 Analyzing failure with {provider.capitalize()}...")
    try:
        analysis = analyze_failure(error_context, provider, api_key, model, suggest_patch)
        print("✅ Analysis complete.")
    except Exception as e:
        print(f"❌ LLM Analysis failed: {e}")
        sys.exit(0)

    # Step 4: Dispatch Notifications
    print("💬 Dispatching notifications...")
    post_github_summary(analysis, repo, run_id)
    
    if discord_url:
        post_to_discord(discord_url, analysis, repo, run_id)
    
    if slack_url:
        post_to_slack(slack_url, analysis, repo, run_id)

    print("🏁 InferOps finished successfully.")

if __name__ == "__main__":
    main()
