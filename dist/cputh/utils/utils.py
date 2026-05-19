import subprocess

def check_pyright_installed() -> bool:
    """Check if pyright is available on PATH."""
    try:
        subprocess.run(
            ["pyright", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
