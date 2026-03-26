
# ================================================
# RETAIL MBR PIPELINE
# Master Runner — One Click Runs Everything
# Author: Vaibhav Shankdhar
# ================================================

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ------------------------------------------------
# Paths
# ------------------------------------------------
BASE_DIR   = Path.cwd()
PYTHON_DIR = BASE_DIR / 'python'

# ------------------------------------------------
# Colours for terminal output
# ------------------------------------------------
class C:
    BLUE    = '\033[94m'
    GREEN   = '\033[92m'
    RED     = '\033[91m'
    YELLOW  = '\033[93m'
    BOLD    = '\033[1m'
    RESET   = '\033[0m'

def log(msg, color=C.RESET):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{color}[{timestamp}] {msg}{C.RESET}")

def header(msg):
    print(f"\n{C.BOLD}{C.BLUE}{'='*55}")
    print(f"  {msg}")
    print(f"{'='*55}{C.RESET}\n")

def success(msg):
    log(f"✅ {msg}", C.GREEN)

def error(msg):
    log(f"❌ {msg}", C.RED)

def info(msg):
    log(f"ℹ️  {msg}", C.YELLOW)

# ------------------------------------------------
# Run a Python script
# ------------------------------------------------
def run_script(script_name, description):
    script_path = PYTHON_DIR / script_name
    info(f"Running: {description}...")

    start = time.time()
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR)
    )
    elapsed = round(time.time() - start, 1)

    if result.returncode == 0:
        success(f"{description} — done in {elapsed}s")
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                print(f"     {line}")
        return True
    else:
        error(f"{description} — FAILED")
        if result.stderr.strip():
            for line in result.stderr.strip().split('\n'):
                print(f"     {C.RED}{line}{C.RESET}")
        return False

# ================================================
# PIPELINE STEPS
# ================================================
def run_pipeline(send_email=True):

    header("RETAIL MBR PIPELINE — STARTING")
    print(f"  📅 Run Date : {datetime.now().strftime('%d %B %Y, %H:%M')}")
    print(f"  📁 Root Dir : {BASE_DIR}\n")

    results = {}
    total_start = time.time()

    # ----------------------------------------
    # STEP 1: Load warehouse from MySQL
    # ----------------------------------------
    header("STEP 1 of 4 — Data Warehouse Export")
    results['warehouse'] = run_script(
        '01_load_warehouse.py',
        'SQL → master_kpi.csv export'
    )
    if not results['warehouse']:
        error("Warehouse export failed — stopping pipeline.")
        return

    # ----------------------------------------
    # STEP 2: Build charts
    # ----------------------------------------
    header("STEP 2 of 4 — Chart Generation")
    results['charts'] = run_script(
        '02_build_charts.py',
        'KPI chart builder'
    )
    if not results['charts']:
        error("Chart generation failed — stopping pipeline.")
        return

    # ----------------------------------------
    # STEP 3: Generate PDF
    # ----------------------------------------
    header("STEP 3 of 4 — PDF Report Generation")
    results['pdf'] = run_script(
        '03_generate_pdf.py',
        'MBR PDF generator'
    )
    if not results['pdf']:
        error("PDF generation failed — stopping pipeline.")
        return

    # ----------------------------------------
    # STEP 4: Send email (optional)
    # ----------------------------------------
    if send_email:
        header("STEP 4 of 4 — Email Delivery")
        results['email'] = run_script(
            '04_send_email.py',
            'MBR email delivery'
        )
    else:
        info("Email skipped — use --email flag to send")
        results['email'] = None

    # ----------------------------------------
    # SUMMARY
    # ----------------------------------------
    total_elapsed = round(time.time() - total_start, 1)

    header("PIPELINE COMPLETE — SUMMARY")
    print(f"  {'Step':<30} {'Status'}")
    print(f"  {'-'*45}")

    steps = [
        ('Warehouse Export',    results['warehouse']),
        ('Chart Generation',    results['charts']),
        ('PDF Report',          results['pdf']),
        ('Email Delivery',      results['email']),
    ]

    all_passed = True
    for step, result in steps:
        if result is True:
            status = f"{C.GREEN}✅ PASSED{C.RESET}"
        elif result is False:
            status = f"{C.RED}❌ FAILED{C.RESET}"
            all_passed = False
        else:
            status = f"{C.YELLOW}⏭️  SKIPPED{C.RESET}"
        print(f"  {step:<30} {status}")

    print(f"\n  ⏱️  Total time : {total_elapsed}s")

    if all_passed:
        print(f"\n{C.BOLD}{C.GREEN}")
        print("  🎉 All steps completed successfully!")
        print(f"  📊 Dashboard : http://localhost:8501")
        print(f"  📄 PDF saved : output/")
        print(f"{C.RESET}")
    else:
        print(f"\n{C.RED}  ⚠️  Pipeline completed with errors.{C.RESET}")

# ================================================
# ENTRY POINT
# ================================================
if __name__ == '__main__':
    # Check for --email flag
    send_email = '--email' in sys.argv
    run_pipeline(send_email=send_email)