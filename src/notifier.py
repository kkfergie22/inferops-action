import httpx
import os

def post_github_summary(payload: dict, repo: str, run_id: str):
    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_file:
        print("⚠️ GITHUB_STEP_SUMMARY environment variable not set. Skipping GitHub summary.")
        return

    content = "## 🔍 InferOps CI/CD Analyzer\n\n"
    content += f"**Job Run**: https://github.com/{repo}/actions/runs/{run_id}\n\n"
    content += f"### 📝 Summary\n{payload.get('summary', 'N/A')}\n\n"
    content += f"### 🚨 Root Cause\n{payload.get('root_cause', 'N/A')}\n\n"
    content += f"### 🛠️ Suggested Fix\n{payload.get('fix', 'N/A')}\n\n"

    if payload.get("patch"):
        content += f"### 💻 Patch\n```diff\n{payload['patch']}\n```\n\n"

    try:
        with open(summary_file, "a") as f:
            f.write(content)
        print("✅ Posted summary to GitHub Step Summary.")
    except Exception as e:
        print(f"❌ Failed to write to GITHUB_STEP_SUMMARY: {e}")

def post_to_discord(webhook_url: str, payload: dict, repo: str, run_id: str):
    if not webhook_url:
        return

    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"
    
    embed = {
        "title": "🚨 CI/CD Pipeline Failed",
        "url": run_url,
        "color": 16711680,  # Red
        "description": payload.get("summary", "N/A"),
        "fields": [
            {
                "name": "Repository",
                "value": repo,
                "inline": True
            },
            {
                "name": "🚨 Root Cause",
                "value": payload.get('root_cause', 'N/A')[:1024]
            },
            {
                "name": "🛠️ Suggested Fix",
                "value": payload.get('fix', 'N/A')[:1024]
            }
        ],
        "footer": {
            "text": "Analyzed by InferOps ✨"
        }
    }

    if payload.get("patch"):
        patch_text = payload["patch"][:1000]
        embed["fields"].append({
            "name": "💻 Patch",
            "value": f"```diff\n{patch_text}\n```"
        })

    data = {
        "username": "InferOps Debugger",
        "embeds": [embed]
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            client.post(webhook_url, json=data)
            print("✅ Sent notification to Discord.")
    except Exception as e:
        print(f"❌ Failed to send Discord notification: {e}")

def post_to_slack(webhook_url: str, payload: dict, repo: str, run_id: str):
    if not webhook_url:
        return

    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚨 CI/CD Pipeline Failed",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Repository:* {repo}\n*Run:* <{run_url}|View Run>\n\n*Summary:*\n{payload.get('summary', 'N/A')}"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🚨 Root Cause:*\n{payload.get('root_cause', 'N/A')}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🛠️ Suggested Fix:*\n{payload.get('fix', 'N/A')}"
            }
        }
    ]

    if payload.get("patch"):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*💻 Patch:*\n```\n{payload['patch'][:2000]}\n```"
            }
        })

    data = {"blocks": blocks}

    try:
        with httpx.Client(timeout=10.0) as client:
            client.post(webhook_url, json=data)
            print("✅ Sent notification to Slack.")
    except Exception as e:
        print(f"❌ Failed to send Slack notification: {e}")
