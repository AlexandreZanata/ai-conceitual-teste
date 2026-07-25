"""Quality scan caps — line limits waived; cyclomatic remains."""

# File/function line caps removed (project waiver). Do not re-enable without ask.
MAX_FILE_LINES = None
MAX_FUNCTION_LINES = None
MAX_CYCLOMATIC = 10

SOURCE_SUFFIXES = {
    ".kt",
    ".kts",
    ".java",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".py",
    ".cpp",
    ".cc",
    ".cxx",
    ".hpp",
    ".h",
    ".hh",
}

SKIP_DIR_NAMES = {
    ".git",
    ".local",
    ".gradle",
    "build",
    "node_modules",
    "dist",
    "coverage",
    ".venv",
    "venv",
    "__pycache__",
    "agent-rules",
    "agent-harness",
    ".cursor",
}
