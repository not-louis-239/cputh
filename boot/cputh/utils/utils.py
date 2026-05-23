import subprocess as subp

def check_pyright_installed() -> bool:
    """Check if pyright is available on PATH."""
    try:
        subp.run(
            ["pyright", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subp.CalledProcessError):
        return False
