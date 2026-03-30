import json
import os

system_prompt = """You are an expert DevOps and CI/CD engineer.
Your task is to analyze the following CI/CD job logs and determine why the job failed.

Read the logs carefully and provide a structured JSON response with the following fields:
- "summary": A 1-2 sentence high-level summary of the error.
- "root_cause": A detailed explanation of why the failure occurred.
- "fix": Actionable steps to fix the issue.
- "patch": If a code change can fix the issue, provide a git diff patch. Otherwise, return null.

Only return valid JSON containing these exact keys. Do not include markdown formatting like ```json in the output.
"""

def analyze_failure(logs: str, provider: str, api_key: str, model: str, suggest_patch: bool) -> dict:
    if not logs.strip():
        return {
            "summary": "No logs provided",
            "root_cause": "The log output was empty.",
            "fix": "Check if the step produced any output.",
            "patch": None
        }

    # If patch is not requested, tell LLM not to bother.
    prompt = system_prompt
    if not suggest_patch:
        prompt = prompt.replace(
            '- "patch": If a code change can fix the issue, provide a git diff patch. Otherwise, return null.',
            '- "patch": Always return null.'
        )

    user_content = f"Here are the logs of the failed job:\n\n{logs}"

    if provider.lower() == "openai":
        return _analyze_openai(prompt, user_content, api_key, model or "gpt-4o-mini")
    elif provider.lower() == "gemini":
        return _analyze_gemini(prompt, user_content, api_key, model or "gemini-2.5-flash")
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

def _analyze_openai(prompt: str, user_content: str, api_key: str, model: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ],
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "summary": "Failed to parse LLM output",
            "root_cause": "The LLM returned invalid JSON.",
            "fix": "Retry or check the logs manually.",
            "patch": None
        }

def _analyze_gemini(prompt: str, user_content: str, api_key: str, model: str) -> dict:
    from google import genai
    from google.genai import types
    from pydantic import BaseModel, Field
    
    class AnalysisResponse(BaseModel):
        summary: str = Field(description="A 1-2 sentence high-level summary of the error.")
        root_cause: str = Field(description="A detailed explanation of why the failure occurred.")
        fix: str = Field(description="Actionable steps to fix the issue.")
        patch: str | None = Field(description="A git diff patch if applicable, else null", default=None)

    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model=model,
        contents=[
            types.Content(role="user", parts=[
                types.Part.from_text(f"{prompt}\n\n{user_content}")
            ])
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnalysisResponse,
            temperature=0.2,
        ),
    )
    
    try:
        if response.text:
            return json.loads(response.text)
        return {
            "summary": "Empty response from LLM",
            "root_cause": "Gemini returned an empty response.",
            "fix": "Retry or check the logs manually.",
            "patch": None
        }
    except json.JSONDecodeError:
        return {
            "summary": "Failed to parse LLM output",
            "root_cause": "The LLM returned invalid JSON.",
            "fix": "Retry or check the logs manually.",
            "patch": None
        }
