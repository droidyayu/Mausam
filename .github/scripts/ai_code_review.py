import os
import requests
import json
import sys

# Debug flag
DEBUG = True

def debug_log(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

# === CONFIG ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("[ERROR] GITHUB_TOKEN is not set!", file=sys.stderr)
    exit(1)
else:
    debug_log(f"GITHUB_TOKEN starts with: {GITHUB_TOKEN[:6]}... (length: {len(GITHUB_TOKEN)})")

REPO = os.getenv("GITHUB_REPOSITORY")  # Format: owner/repo
if not REPO:
    print("[ERROR] GITHUB_REPOSITORY is not set!", file=sys.stderr)
    exit(1)
else:
    debug_log(f"GITHUB_REPOSITORY: {REPO}")

PR_NUMBER = os.getenv("GITHUB_REF").split("/")[2]
if not PR_NUMBER:
    print("[ERROR] GITHUB_REF is not set or not in the correct format!", file=sys.stderr)
    exit(1)
else:
    debug_log(f"GITHUB_REF: {PR_NUMBER}")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[ERROR] GEMINI_API_KEY is not set!", file=sys.stderr)
    exit(1)
else:
    debug_log(f"GEMINI_API_KEY starts with: {GEMINI_API_KEY[:6]}... (length: {len(GEMINI_API_KEY)})")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
debug_log(f"HEADERS: {HEADERS}")


def get_changed_files():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/files"
    print(f"[INFO] Fetching changed files from: {url}")
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"[ERROR] GitHub API error {response.status_code}: {response.text}")
        return []
    return response.json()


def clean_gemini_comment(comment):
    """
    Clean and format Gemini's response for GitHub inline comments.
    - Trims whitespace
    - Limits length to 650 chars
    - Removes excessive blank lines
    """
    comment = comment.strip()
    comment = '\n'.join([line.rstrip() for line in comment.splitlines() if line.strip() != ''])
    max_length = 650
    if len(comment) > max_length:
        comment = comment[:max_length] + "…"
    return comment

def generate_review_comment(diff_hunk, filename):
    prompt = f"""
You're a senior Android reviewer. Carefully review this code diff from `{filename}`.

- Only return specific, actionable, and concise inline review comments.
- Use clear markdown formatting for code, lists, or warnings.
- Avoid generic feedback. Focus on deprecated APIs, performance, testability, and Android best practices.
- Each comment should be suitable for direct posting as a GitHub inline review.
- If the diff is fine, return a short positive note.

Diff:
{diff_hunk}
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    debug_log(f"Gemini API URL: {url}")
    debug_log(f"Request headers: {headers}")
    debug_log(f"Request data: {json.dumps(data)}")
    response = requests.post(url, headers=headers, data=json.dumps(data))
    debug_log(f"Response status: {response.status_code}")
    debug_log(f"Response text: {response.text}")
    if response.status_code == 200:
        result = response.json()
        comment = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        comment = clean_gemini_comment(comment)
        debug_log(f"Extracted comment: {comment}")
        return comment or "⚠️ No useful feedback was generated."
    else:
        print(f"[ERROR] Gemini API error {response.status_code}: {response.text}")
        return "⚠️ Gemini API error."

# Minimal test for Gemini API integration
if __name__ == "__main__":
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": "Explain how AI works in a few words"}
                ]
            }
        ]
    }
    debug_log(f"Gemini API URL: {url}")
    debug_log(f"Request headers: {headers}")
    debug_log(f"Request data: {json.dumps(data)}")
    response = requests.post(url, headers=headers, data=json.dumps(data))
    debug_log(f"Response status: {response.status_code}")
    debug_log(f"Response text: {response.text}")
    if response.status_code == 200:
        result = response.json()
        print("Gemini API test response:")
        print(result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", ""))
    else:
        print(f"[ERROR] Gemini API error {response.status_code}: {response.text}")


def get_latest_commit_sha():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"[ERROR] Failed to get latest commit SHA: {response.status_code} - {response.text}")
        return None
    return response.json()["head"]["sha"]


def post_inline_comment(body, path, position):
    sha = get_latest_commit_sha()
    if not sha:
        return
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/comments"
    payload = {
        "body": body,
        "commit_id": sha,
        "path": path,
        "position": position
    }
    print(f"[INFO] Posting comment to {path} at position {position}")
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 201:
        print(f"[ERROR] Failed to post comment: {response.status_code} - {response.text}")
    else:
        print(f"[INFO] Comment posted on {path}")


def fetch_file_content(repo, path):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        # If file is not binary
        if data.get('encoding') == 'base64':
            import base64
            return base64.b64decode(data['content']).decode('utf-8', errors='replace')
        else:
            return data.get('content', '')
    else:
        print(f"[ERROR] Could not fetch {path}: {response.status_code}")
        return ''

def generate_test_coverage_comment(source_code, test_code, source_filename, test_filename):
    prompt = f"""
You are an expert software reviewer. Analyze the following source code and its unit tests.

Source file: {source_filename}
---
{source_code}

Test file: {test_filename}
---
{test_code}

List any important test scenarios that are missing or weakly covered. Format your answer as a markdown bullet list suitable for a GitHub code review comment. If all important scenarios are covered, reply with a short positive note.
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    debug_log(f"[Coverage] Gemini prompt: {prompt[:200]}...")
    response = requests.post(url, headers=headers, data=json.dumps(data))
    debug_log(f"[Coverage] Response status: {response.status_code}")
    debug_log(f"[Coverage] Response text: {response.text}")
    if response.status_code == 200:
        result = response.json()
        comment = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        comment = clean_gemini_comment(comment)
        return comment
    else:
        print(f"[ERROR] Gemini API error {response.status_code}: {response.text}")
        return None

def post_pr_comment(body):
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    payload = {"body": body}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 201:
        print(f"[ERROR] Failed to post PR comment: {response.status_code} - {response.text}")
    else:
        print(f"[INFO] PR summary comment posted.")

import re

def is_test_file(filename):
    # Detects test files by name or directory
    filename_lower = filename.lower()
    test_dirs = ["test", "tests", "androidtest", "unittest", "integrationtest"]
    if any(f"/{d}/" in filename_lower or f"\\{d}\\" in filename_lower for d in test_dirs):
        return True
    if re.search(r'(test.*\.(kt|java|py|js|ts|swift|go|rb|cpp|c|cs|php)$)|(_test\.(py|js|ts|go|rb|cpp|c|cs|php)$)', filename_lower):
        return True
    if re.search(r'(Test|_test|test_)[A-Za-z0-9_]*\.(kt|java|py|js|ts|swift|go|rb|cpp|c|cs|php)$', filename):
        return True
    return False

def infer_source_filename(test_filename):
    # Remove test-related directory
    source_filename = re.sub(r'[/\\](test|tests|androidTest|unitTest|integrationTest)[/\\]', '/main/', test_filename, flags=re.IGNORECASE)
    # Remove Test or _test from filename
    source_filename = re.sub(r'(Test|_test)(\.[a-z0-9]+)$', r'\2', source_filename, flags=re.IGNORECASE)
    # Remove test_ prefix
    source_filename = re.sub(r'test_', '', source_filename, flags=re.IGNORECASE)
    return source_filename

def find_test_file_for_source(source_filename):
    """
    Given a source file, return the expected test file path (if it exists) in test or androidTest.
    """
    test_dirs = ["test", "androidTest"]
    base = os.path.basename(source_filename)
    name, ext = os.path.splitext(base)
    test_patterns = [f"{name}_test{ext}", f"Test{name}{ext}"]
    candidates = []
    for d in test_dirs:
        for pattern in test_patterns:
            test_path = source_filename.replace("/main/", f"/{d}/").replace(base, pattern)
            candidates.append(test_path)
    return candidates

def test_file_exists(repo, test_candidates):
    for test_path in test_candidates:
        url = f"https://api.github.com/repos/{repo}/contents/{test_path}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return test_path
    return None

def generate_basic_test_file(source_code, source_filename, test_filename):
    prompt = f"""
You are an expert Android/Kotlin developer. Given the following source file, generate a basic but meaningful unit test file in Kotlin using JUnit, with filename: {test_filename}. Only output valid Kotlin code, no explanation.
Source file: {source_filename}
---
{source_code}
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        code = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return code
    else:
        print(f"[ERROR] Gemini API error {response.status_code}: {response.text}")
        return None

def generate_test_code_for_missing_scenarios(source_code, test_filename, missing_scenarios):
    prompt = f"""
You are an expert Android/Kotlin developer. Given the following source file and a list of missing test scenarios, generate Kotlin/JUnit test code for those scenarios and output only the code (no explanation). Append to {test_filename}.
Source file:
---
{source_code}
---
Missing scenarios:
{missing_scenarios}
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        code = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return code
    else:
        print(f"[ERROR] Gemini API error {response.status_code}: {response.text}")
        return None

def main():
    print("[INFO] Starting AI code review process...")
    files = get_changed_files()
    if not files:
        print("[INFO] No changed files found.")
        return

    coverage_comments = []
    test_generation_comments = []

    for f in files:
        filename = f.get("filename", "")
        status = f.get("status", "")
        hunk = f.get("patch", "")

        print(f"[INFO] Processing file: {filename} (status: {status})")

        # --- Regular code review for Kotlin/Java ---
        if filename.endswith((".kt", ".java")) and not is_test_file(filename):
            if hunk and status in ["modified", "added"]:
                comment = generate_review_comment(hunk, filename)
                post_inline_comment(comment, filename, position=1)

            # --- Check for missing test file ---
            test_candidates = find_test_file_for_source(filename)
            test_path = test_file_exists(REPO, test_candidates)
            if not test_path:
                source_code = fetch_file_content(REPO, filename)
                # Pick first candidate for new test file name
                new_test_filename = test_candidates[0]
                test_code = generate_basic_test_file(source_code, filename, new_test_filename)
                if test_code:
                    test_generation_comments.append(f"**Auto-generated test file suggestion for `{filename}`:**\nCreate `{new_test_filename}` with the following content:\n\n```kotlin\n{test_code}\n```")

        # --- Test coverage analysis ---
        if is_test_file(filename):
            test_code = fetch_file_content(REPO, filename)
            source_filename = infer_source_filename(filename)
            source_code = fetch_file_content(REPO, source_filename) if source_filename else ''
            if source_code:
                coverage_comment = generate_test_coverage_comment(source_code, test_code, source_filename, filename)
                if coverage_comment and not any(x in coverage_comment.lower() for x in ["all important scenarios are covered", "no missing test"]):
                    coverage_comments.append(f"**Test coverage review for `{filename}`:**\n{coverage_comment}")
                    # Try to extract missing scenarios and generate code
                    missing = coverage_comment
                    test_stub_code = generate_test_code_for_missing_scenarios(source_code, filename, missing)
                    if test_stub_code:
                        test_generation_comments.append(f"**Suggested test stubs for `{filename}`:**\nAdd the following code to improve coverage:\n\n```kotlin\n{test_stub_code}\n```")

    # Post summary comment if any missing/weak coverage is found or test files generated
    summary_sections = []
    if coverage_comments:
        summary_sections.append("\n\n".join(coverage_comments))
    if test_generation_comments:
        summary_sections.append("\n\n".join(test_generation_comments))
    if summary_sections:
        summary = "\n\n---\n\n".join(summary_sections)
        post_pr_comment(summary)



if __name__ == "__main__":
    main()
