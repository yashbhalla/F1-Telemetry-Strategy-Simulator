import sys
from pathlib import Path


def add_project_root():
    # If running inside notebooks/, go up one level
    project_root = Path(__file__).resolve().parent
    if project_root.name == "notebooks":
        project_root = project_root.parent

    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    return project_root
