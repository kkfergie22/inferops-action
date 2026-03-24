import os


def main():
    print("🚀 InferOps is running")

    repo = os.getenv("GITHUB_REPOSITORY")
    run_id = os.getenv("GITHUB_RUN_ID")

    print(f"Repository: {repo}")
    print(f"Run ID: {run_id}")


if __name__ == "__main__":
    main()
