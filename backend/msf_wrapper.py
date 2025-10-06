import subprocess
import tempfile
import os
from typing import Tuple

def run_msfconsole_safe(commands: str, timeout: int = 300) -> Tuple[int, str, str]:
    """Run msfconsole using a temporary resource file to avoid shell injection.
    Writes commands to a temp file and runs: msfconsole -q -r <tmpfile>
    Returns: (exit_code, stdout, stderr)
    """
    from shutil import which
    msf_path = which('msfconsole')
    if not msf_path:
        return (127, '', 'msfconsole not found on PATH')
    # Write commands to temp rc file
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.rc') as f:
        f.write(commands)
        f.write('\nexit\n')
        tmp_path = f.name
    try:
        res = subprocess.run([msf_path, '-q', '-r', tmp_path],
                             capture_output=True, text=True, timeout=timeout)
        stdout = res.stdout or ''
        stderr = res.stderr or ''
        return (res.returncode, stdout, stderr)
    except subprocess.TimeoutExpired as e:
        return (124, '', f"Timeout after {timeout}s: {str(e)}")
    except Exception as e:
        return (1, '', f"Execution error: {str(e)}")
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
