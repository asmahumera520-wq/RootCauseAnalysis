"""
log_parser.py
Reads raw error-log text and pulls out the important bits for the AI prompt.
"""

import re
from collections import Counter


def parse_logs(log_text: str) -> dict:
    """
    Extract key information from a raw log file string.

    Returns a dict with:
        - error_count      : total ERROR / FATAL lines
        - key_errors       : list of unique error messages (top 10)
        - first_error_time : timestamp of the very first error
        - last_error_time  : timestamp of the last error
        - stack_trace_summary : first stack-trace found (if any)
        - services_mentioned  : unique service/class names seen
        - log_snippet      : first 40 lines of the log (for context)
    """

    if not log_text or not log_text.strip():
        return {
            "error_count": 0,
            "key_errors": [],
            "first_error_time": "N/A",
            "last_error_time": "N/A",
            "stack_trace_summary": "No logs provided.",
            "services_mentioned": [],
            "log_snippet": "",
        }

    lines = log_text.splitlines()

    # ── Patterns ──────────────────────────────────────────────────
    error_pattern   = re.compile(r'\b(ERROR|FATAL|CRITICAL|EXCEPTION|WARN)\b', re.IGNORECASE)
    timestamp_pat   = re.compile(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}(:\d{2})?')
    service_pat     = re.compile(r'\b([A-Z][a-zA-Z0-9]+(?:Service|Handler|Manager|Controller|Client|Server|Exception))\b')
    stacktrace_pat  = re.compile(r'^\s+at\s|^\s+Caused by|java\.\w+\.\w+Exception|Traceback \(most recent')

    error_lines     = []
    timestamps      = []
    services        = []
    stack_lines     = []
    in_stack        = False

    for line in lines:
        # Collect timestamps from any line
        ts = timestamp_pat.search(line)
        if ts:
            timestamps.append(ts.group())

        # Focus on error lines
        if error_pattern.search(line):
            error_lines.append(line.strip())
            in_stack = False          # reset; a new error starts

        # Detect stack trace continuation
        if stacktrace_pat.search(line):
            in_stack = True

        if in_stack and len(stack_lines) < 15:
            stack_lines.append(line.rstrip())

        # Collect service / class names
        svcs = service_pat.findall(line)
        services.extend(svcs)

    # ── Deduplicate error messages (keep top 10 most common) ──────
    def clean_error(line):
        """Strip timestamps and IDs so similar lines collapse."""
        line = timestamp_pat.sub('', line)
        line = re.sub(r'\b[0-9a-f\-]{8,}\b', '<ID>', line)   # UUIDs / hex IDs
        line = re.sub(r'\b\d+\b', '<N>', line)                # plain numbers
        return line.strip()

    cleaned = [clean_error(l) for l in error_lines]
    counter = Counter(cleaned)
    key_errors = [msg for msg, _ in counter.most_common(10)]

    return {
        "error_count":        len(error_lines),
        "key_errors":         key_errors,
        "first_error_time":   timestamps[0]  if timestamps else "N/A",
        "last_error_time":    timestamps[-1] if timestamps else "N/A",
        "stack_trace_summary": "\n".join(stack_lines[:15]) if stack_lines else "No stack traces found.",
        "services_mentioned": list(dict.fromkeys(services))[:10],   # unique, ordered
        "log_snippet":        "\n".join(lines[:40]),
    }
