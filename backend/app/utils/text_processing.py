"""
Text Processing Utilities — cleaning and normalization for code and documentation text.
"""

import re


def clean_text(text: str) -> str:
    """Remove excessive whitespace and normalize line endings."""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove trailing whitespace per line
    lines = [line.rstrip() for line in text.split("\n")]
    # Collapse more than 3 consecutive blank lines into 2
    cleaned_lines: list[str] = []
    blank_count = 0
    for line in lines:
        if line == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned_lines.append(line)
        else:
            blank_count = 0
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def extract_imports(content: str, language: str) -> list[str]:
    """Extract import statements from source code for metadata."""
    imports: list[str] = []

    if language == "python":
        for match in re.finditer(r"^(?:from\s+\S+\s+)?import\s+.+$", content, re.MULTILINE):
            imports.append(match.group().strip())
    elif language in ("javascript", "typescript"):
        for match in re.finditer(r"^import\s+.+$", content, re.MULTILINE):
            imports.append(match.group().strip())
        for match in re.finditer(r"^const\s+.+\s*=\s*require\(.+\)", content, re.MULTILINE):
            imports.append(match.group().strip())
    elif language == "java":
        for match in re.finditer(r"^import\s+.+;$", content, re.MULTILINE):
            imports.append(match.group().strip())
    elif language in ("go",):
        for match in re.finditer(r'^import\s+(?:\([\s\S]*?\)|".+")$', content, re.MULTILINE):
            imports.append(match.group().strip())

    return imports[:20]  # Cap at 20 imports


def extract_parent_context(content: str, language: str) -> str | None:
    """Extract the enclosing class/module name for context."""
    if language == "python":
        match = re.search(r"^class\s+(\w+)", content, re.MULTILINE)
        if match:
            return f"class {match.group(1)}"
    elif language in ("java", "csharp", "kotlin"):
        match = re.search(r"(?:public|private|protected)?\s*class\s+(\w+)", content)
        if match:
            return f"class {match.group(1)}"
    elif language in ("javascript", "typescript"):
        match = re.search(r"(?:export\s+)?class\s+(\w+)", content)
        if match:
            return f"class {match.group(1)}"
        match = re.search(r"(?:export\s+)?(?:default\s+)?function\s+(\w+)", content)
        if match:
            return f"function {match.group(1)}"
    elif language in ("cpp", "c"):
        match = re.search(r"class\s+(\w+)", content)
        if match:
            return f"class {match.group(1)}"
        match = re.search(r"namespace\s+(\w+)", content)
        if match:
            return f"namespace {match.group(1)}"
    return None
