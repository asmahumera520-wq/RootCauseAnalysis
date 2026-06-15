"""
diff_parser.py
Reads a git diff / patch file and extracts meaningful info for the AI prompt.
"""

import re


def parse_git_diff(diff_text: str) -> dict:
    """
    Parse a unified git diff and return a structured summary.

    Returns:
        files_changed  : list of file paths that were modified
        additions      : list of {file, line} for added lines
        deletions      : list of {file, line} for removed lines
        summary        : one human-readable sentence
        patch_snippet  : first 60 lines of the diff (for AI context)
    """

    if not diff_text or not diff_text.strip():
        return {
            "files_changed": [],
            "additions": [],
            "deletions": [],
            "summary": "No git diff provided.",
            "patch_snippet": "",
        }

    lines = diff_text.splitlines()

    files_changed = []
    additions     = []
    deletions     = []
    current_file  = None

    file_pat = re.compile(r'^\+\+\+ b/(.+)$')

    for line in lines:
        # Detect file being changed
        m = file_pat.match(line)
        if m:
            current_file = m.group(1).strip()
            if current_file not in files_changed and current_file != '/dev/null':
                files_changed.append(current_file)
            continue

        # Added lines (skip the +++ header itself)
        if line.startswith('+') and not line.startswith('+++'):
            content = line[1:].strip()
            if content:
                additions.append({"file": current_file, "line": content})

        # Removed lines (skip the --- header itself)
        elif line.startswith('-') and not line.startswith('---'):
            content = line[1:].strip()
            if content:
                deletions.append({"file": current_file, "line": content})

    summary = (
        f"{len(files_changed)} file(s) changed "
        f"({', '.join(files_changed) or 'unknown'}). "
        f"{len(additions)} line(s) added, {len(deletions)} line(s) removed."
    )

    return {
        "files_changed": files_changed,
        "additions":     additions[:20],   # cap at 20 to keep prompt short
        "deletions":     deletions[:20],
        "summary":       summary,
        "patch_snippet": "\n".join(lines[:60]),
    }
