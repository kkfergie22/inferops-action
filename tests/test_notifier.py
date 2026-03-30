import sys
import os
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from notifier import post_to_discord, post_to_slack, post_github_summary

@patch('httpx.Client.post')
def test_discord_payload(mock_post):
    payload = {"summary": "Build failed", "root_cause": "Typo", "fix": "Fix typo", "patch": "+fix"}
    post_to_discord("http://fake-webhook", payload, "org/repo", "123")
    
    # Verify post was called
    mock_post.assert_called_once()
    
    # Check payload structure
    args, kwargs = mock_post.call_args
    assert args[0] == "http://fake-webhook"
    json_data = kwargs["json"]
    assert json_data["username"] == "InferOps Debugger"
    
@patch('httpx.Client.post')
def test_slack_payload(mock_post):
    payload = {"summary": "Build failed"}
    post_to_slack("http://fake-webhook", payload, "org/repo", "123")
    
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://fake-webhook"
    assert "blocks" in kwargs["json"]

@patch('builtins.open', new_callable=mock_open)
@patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": "/fake/summary.md"})
def test_github_summary(mock_file):
    payload = {"summary": "Build failed", "patch": "+fix"}
    post_github_summary(payload, "org/repo", "123")
    
    mock_file.assert_called_once_with("/fake/summary.md", "a")
    mock_file().write.assert_called_once()
    written_data = mock_file().write.call_args[0][0]
    assert "Build failed" in written_data
    assert "```diff\n+fix\n```" in written_data
