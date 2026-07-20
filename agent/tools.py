import pathlib
import subprocess

from typing import Tuple
from langchain_core.tools import tool


PROJECT_ROOT = pathlib.Path.cwd() / "generated_project"

def safe_path_for_project(path: str) -> pathlib.Path:
    p = (PROJECT_ROOT / path).resolve()
    if PROJECT_ROOT.resolve() not in p.parents and PROJECT_ROOT.resolve() != p.parent and PROJECT_ROOT.resolve() != p:
        raise ValueError("Attempt to write outside the project directory")
    return p


@tool
def write_files(path: str, content:str) -> str:
    """Writes content to a file at the specified path in the project root"""
    p = safe_path_for_project(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return f"WROTE:{p}"




@tool
def read_file(path:str) -> str:
    """Reads contents from a file at the specified path within the project root
    when architect node gives a task like modify "index.html" to add the display then it could add the pre made things like buttons
    the coder agent must read what is in the file before it write a new file otherwise it could overwrite the file

    """

    p = safe_path_for_project(path)
    if not p.exists():
        return ""
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

@tool
def get_current_directory() -> str:
    """Returns the current working directory"""
    return str(PROJECT_ROOT)

@tool
def list_files(dicrectory: str = ".") -> str:
    """List all files in the specified directory within the project root"""

    p = safe_path_for_project(dicrectory)
    if not p.is_dir():
        return f"ERROR: {p} is not a directory"
    files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]

    return "\n".join(files) if files else """No files found"""

@tool
def run_cmd(cmd:str, cwd: str = None, timeout: int = None) -> Tuple[int, str,str]:
    """Runs a shell command in the specified directory and returns the result."""
    cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT
    res = subprocess.run(cmd, shell=True, cwd=str(cwd_dir), capture_output=True, text=True, timeout=timeout)
    return res.returncode, res.stdout, res.stderr





def init_project_root():
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    return str(PROJECT_ROOT)






















