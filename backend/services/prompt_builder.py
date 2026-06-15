"""
prompt_builder.py
Assembles all incident data into a rich, structured prompt for the Gemini AI.
"""


def build_rca_prompt(
    title: str,
    severity: str,
    timeline: str,
    affected_systems: str,
    parsed_logs: dict,
    parsed_diff: dict,
) -> str:
    """
    Build the master prompt that tells Gemini exactly what to write
    and in which format.  The more detailed this prompt, the better
    the RCA that comes back.
    """

    # ── Format log section ────────────────────────────────────────
    key_errors_text = "\n".join(
        f"  • {e}" for e in parsed_logs.get("key_errors", [])
    ) or "  • No errors extracted"

    services_text = ", ".join(parsed_logs.get("services_mentioned", [])) or "Unknown"

    stack_text = parsed_logs.get("stack_trace_summary", "None found")

    # ── Format diff section ───────────────────────────────────────
    files_text = "\n".join(
        f"  • {f}" for f in parsed_diff.get("files_changed", [])
    ) or "  • No files listed"

    additions_text = "\n".join(
        f"  + [{item['file']}]  {item['line']}"
        for item in parsed_diff.get("additions", [])[:10]
    ) or "  None"

    deletions_text = "\n".join(
        f"  - [{item['file']}]  {item['line']}"
        for item in parsed_diff.get("deletions", [])[:10]
    ) or "  None"

    patch_snippet = parsed_diff.get("patch_snippet", "Not provided")

    # ── Assemble the prompt ───────────────────────────────────────
    prompt = f"""You are a Principal Site Reliability Engineer (SRE) with 15+ years of
experience writing Root Cause Analysis (RCA) documents for Fortune 500 companies.

Your task: analyse the incident data below and produce a **complete, professional,
and actionable RCA report** in clean Markdown.

═══════════════════════════════════════════════════════════
INCIDENT DETAILS
═══════════════════════════════════════════════════════════
Title            : {title}
Severity         : {severity}
Affected Systems : {affected_systems or "Not specified"}
Incident Date    : (see timeline)

═══════════════════════════════════════════════════════════
INCIDENT TIMELINE  (provided by the on-call engineer)
═══════════════════════════════════════════════════════════
{timeline or "No timeline provided."}

═══════════════════════════════════════════════════════════
ERROR LOG ANALYSIS
═══════════════════════════════════════════════════════════
Total Error / Fatal Lines : {parsed_logs.get("error_count", 0)}
First Error Seen          : {parsed_logs.get("first_error_time", "N/A")}
Last Error Seen           : {parsed_logs.get("last_error_time", "N/A")}
Services Involved         : {services_text}

Key Error Messages:
{key_errors_text}

Stack Trace (first occurrence):
{stack_text}

═══════════════════════════════════════════════════════════
RECENT CODE CHANGES  (git diff)
═══════════════════════════════════════════════════════════
Summary  : {parsed_diff.get("summary", "No diff provided")}

Files Changed:
{files_text}

Lines Added (new code):
{additions_text}

Lines Removed (old code):
{deletions_text}

Raw Patch Snippet:
{patch_snippet}

═══════════════════════════════════════════════════════════
OUTPUT REQUIREMENTS
═══════════════════════════════════════════════════════════
Write the RCA using EXACTLY the following Markdown sections — do not skip any:

## 🔍 Executive Summary
[2–3 clear sentences. What happened, when, and the key impact.]

## ⏱️ Timeline of Events
[Bullet list, chronological. Use timestamps from the data provided.]

## 🎯 Root Cause
[Precise technical explanation of WHY this happened.
 Reference the specific log error or code change that caused it.]

## ⚡ Contributing Factors
[Other things that amplified or delayed resolution.]

## 💥 Impact Assessment
[Users/services affected, duration, estimated business impact.]

## 🔧 Resolution Steps Taken
[What was done to fix the issue, step by step.]

## ✅ Action Items
Use this table format:
| # | Action | Owner | Priority | Deadline |
|---|--------|-------|----------|----------|
| 1 | ...    | ...   | High     | 1 week   |

## 🛡️ Prevention Measures
[Concrete changes to prevent recurrence — code, process, monitoring.]

## 📚 Lessons Learned
[3–5 bullet points the team should remember.]

Be technical, be specific, and base everything on the data provided above.
Do NOT invent facts not supported by the input.
Use professional tone throughout.
"""
    return prompt
