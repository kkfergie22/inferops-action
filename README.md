# InferOps

AI-powered CI/CD failure analyzer for GitHub Actions.

## Usage

```yaml
- name: InferOps Debugger
  if: failure()
  uses: your-username/inferops-action@v1
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
