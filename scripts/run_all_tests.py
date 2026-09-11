"""
Automated Test Runner and Evidence Generator.
Executes pytest with coverage and captures untampered test logs.
"""

from pathlib import Path
import subprocess
import sys

def main():
    root = Path(__file__).resolve().parent.parent
    evidence_dir = root / "evidence" / "tests"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    report_file = evidence_dir / "pytest_report.txt"

    print("Running test suite via pytest and recording evidence...")
    cmd = [
        sys.executable, "-m", "pytest", "tests/", "-v",
        "--cov=src/avatar_system", "--cov-report=term-missing"
    ]
    
    proc = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
    
    full_output = (
        f"TEST EXECUTION RUN LOG\n"
        f"Timestamp: {subprocess.check_output(['powershell', '-Command', 'Get-Date -Format o'], text=True).strip()}\n"
        f"Command: {' '.join(cmd)}\n"
        f"Exit Code: {proc.returncode}\n\n"
        f"STDOUT:\n{proc.stdout}\n\n"
        f"STDERR:\n{proc.stderr}\n"
    )
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(full_output)
        
    print(f"Test run completed with exit code {proc.returncode}.")
    print(f"Saved test evidence: {report_file}")
    sys.exit(proc.returncode)

if __name__ == "__main__":
    main()
