# InferOps CI/CD Failure Analyzer 🚀

A GitHub Action that automatically analyzes your CI/CD workflow failures using Large Language Models (LLMs) and posts actionable summaries, root causes, and fix suggestions directly to your GitHub Job Summary, Discord, and Slack.

## Features ✨
- **Intelligent Error Analysis**: Summarizes dense logs into 1-2 sentence insights.
- **Root Cause & Fix Guidance**: Clearly identifies why a job failed and gives step-by-step instructions on how to fix it.
- **Multi-LLM Support**: Works with **OpenAI** (`gpt-4o`, `gpt-4o-mini`, etc.) out of the box, and supports **Google Gemini** (`gemini-2.5-flash`, etc.).
- **Smart Log Extraction**: Avoids hitting token limits by dynamically extracting the most relevant error lines spanning multiple log files.
- **Multi-Platform Notifications**: Push alerts to **Discord** and **Slack** via webhooks.
- **Diff Patch Suggestions**: Optional stretch feature where the LLM can generate a patch to instantly fix code errors.

## Usage 🛠️

Add the `InferOps Debugger` step to the very end of your workflow job. Use the `if: failure()` condition so it only runs when a step before it fails.

```yaml
jobs:
  build_and_test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # ... your other steps (tests, builds, etc.) ...
      
      - name: InferOps CI Failure Analyzer
        if: failure()
        uses: kkfergie22/inferops-action@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          llm_provider: openai    # 'openai' or 'gemini'
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          # Optional Integrations:
          discord_webhook_url: ${{ secrets.DISCORD_WEBHOOK_URL }}
          slack_webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Inputs 配置

| Input | Required | Default | Description |
|---|---|---|---|
| `github_token` | ✅ Yes | — | Your GitHub Token (`${{ secrets.GITHUB_TOKEN }}`) |
| `openai_api_key` | 🟠 Cond. | — | Required if `llm_provider` is `openai` |
| `gemini_api_key` | 🟠 Cond. | — | Required if `llm_provider` is `gemini` |
| `llm_provider` | ❌ No | `openai` | The LLM backend to use: `openai` or `gemini` |
| `llm_model` | ❌ No | Provider default | Override the model (e.g. `gpt-4o`) |
| `discord_webhook_url` | ❌ No | — | Incoming Discord webhook URL for notifications |
| `slack_webhook_url` | ❌ No | — | Incoming Slack webhook URL for notifications |
| `suggest_patch` | ❌ No | `false` | Instructs the LLM to try producing a `diff` patch |
| `max_log_lines` | ❌ No | `200` | Max relevant log lines sent to the LLM |

## Support 💬
Open an issue if you encounter problems! 
