# ----------------------------------------------------------------------------
# Script: UnityAssetsManagerExportAllProfiles.py
# Description: Automates the batch export of all asset profiles using the
#              UnityAssetsManager Flask API (/api/batch-export).
#              Writes raw exports to assetsExports/Unity for later normalization.
#
# Version: 1.2.16
#
# Requirements:
#   - UnityAssetsManager server must be running (default: http://localhost:5003)
#   - python -m pip install requests
#
# Parameters:
#   -r, --resume                : Resume from the last successful profile
#   -s, --start_index           : Start index in the profile list (1-based)
#   -e, --end_index             : End index in the profile list (1-based)
#   -t, --template              : Export template to use (default: table markdown avec URL)
#   -f, --force                 : Force export even if the raw file already exists
#   -l, --lint_markdown_results : Run markdown linters on exported folders (default: enabled)
#   -u, --url                   : Base URL of the API (default: http://localhost:5003/api)
# ----------------------------------------------------------------------------

import argparse
import sys
import json
import requests
import concurrent.futures
import subprocess
from pathlib import Path
from datetime import datetime

# Import central config and utils
helpers_root = Path(__file__).resolve().parents[2]
if str(helpers_root) not in sys.path:
    sys.path.insert(0, str(helpers_root))
lib_root = helpers_root / "lib"
if str(lib_root) not in sys.path:
    sys.path.insert(0, str(lib_root))

try:
    from vaultConfig import DATA_DIR, cprint  # type: ignore
except ImportError:
    try:
        from _Helpers import vaultConfig as _cfg  # type: ignore
        DATA_DIR = _cfg.DATA_DIR
        cprint = _cfg.cprint
    except ImportError:
        print("Error: vaultConfig.py not found.")
        sys.exit(1)

try:
    from markdownUtils import format_markdown_path  # type: ignore
except ImportError:
    format_markdown_path = None

# Configuration local to UnityAssetsManager
SCRIPT_DIR = Path(__file__).parent
# Raw export directory used as input of the normalization step.
EXPORT_DIR = DATA_DIR / "assetsExports" / "Unity"
CACHE_DIR = SCRIPT_DIR / ".cache"
STATE_FILE = CACHE_DIR / "export_state.json"

# Defaults
DEFAULT_TEMPLATE = "table markdown avec URL"
DEFAULT_API_URL = "http://localhost:5003/api"
DEFAULT_WORKERS = 4  # Number of parallel exports
LINT_BATCH_SCRIPT = Path(r"H:\Sync\Scripts\Windows\04c_dev_scripts\run_linters.bat")


def load_state():
    """Load the last successful profile index from cache."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding='utf-8'))
        except Exception as e:
            cprint(f"❌ Error loading state file: {e}", "RED")
            return {}
    return {}


def save_state(profile_name, index):
    """Save the last successful profile to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps({
            "last_profile": profile_name,
            "last_index": index,
            "timestamp": datetime.now().isoformat()
        }, indent=2), encoding='utf-8'
    )


def expected_output_suffix(template_name: str) -> str:
    """Infer extension from template name to track generated raw files."""
    normalized = (template_name or "").lower()
    if "csv" in normalized:
        return ".csv"
    if "json" in normalized:
        return ".json"
    if "txt" in normalized or "texte" in normalized:
        return ".txt"
    return ".md"


def export_profile(api_url, profile, template, output_file):
    """Unit function for profile export (used by workers)."""
    payload = {"profile": profile, "template": template, "output_path": str(output_file.absolute())}
    try:
        resp = requests.post(f"{api_url}/batch-export", json=payload, timeout=60)
        return profile, resp.status_code, resp.json()
    except Exception as e:
        return profile, 0, {"error": {"message": str(e)}}


def ensure_markdown_h1(markdown_file: Path):
    """Prepend a H1 title matching the file stem when it is missing."""
    if markdown_file.suffix.lower() != ".md" or not markdown_file.exists():
        return

    heading = f"# {markdown_file.stem}"
    content = markdown_file.read_text(encoding="utf-8")
    lines = content.splitlines()

    if lines and lines[0].strip() == heading:
        return

    if not content:
        new_content = f"{heading}\n"
    else:
        new_content = f"{heading}\n\n{content.lstrip('\r\n')}"

    markdown_file.write_text(new_content, encoding="utf-8")


def add_markdown_h1_titles(directories):
    """Add file-name H1 titles to exported markdown files before linting."""
    unique_directories = sorted({Path(directory).resolve() for directory in directories})
    if not unique_directories:
        return

    for directory in unique_directories:
        for markdown_file in sorted(directory.rglob("*.md")):
            cprint(f"📝 Adding title to {markdown_file}", "CYAN")
            ensure_markdown_h1(markdown_file)


def run_markdown_lint(directories):
    """Format tables and run the markdown lint batch script on each exported directory."""
    unique_directories = sorted({Path(directory).resolve() for directory in directories})
    if not unique_directories:
        return

    add_markdown_h1_titles(unique_directories)

    for directory in unique_directories:
        # 1. Format tables first (as the batch script doesn't do it)
        if format_markdown_path:
            cprint(f"🧹 Formatting markdown tables in {directory}", "CYAN")
            format_markdown_path(directory)

        # 2. Run the legacy batch script for general linting if available
        if LINT_BATCH_SCRIPT.exists():
            cprint(f"🔍 Running additional linters in {directory}", "CYAN")
            completed = subprocess.run(["cmd", "/c", str(LINT_BATCH_SCRIPT), str(directory)], check=False, )
            if completed.returncode != 0:
                cprint(f"⚠️ Markdown lint reported issues (non-blocking) for {directory}", "YELLOW")
        else:
            cprint(f"⚠️ External lint script not found: {LINT_BATCH_SCRIPT}", "YELLOW")


def main():
    parser = argparse.ArgumentParser(description="Optimized automate asset profile exports via UAM API.")
    parser.add_argument("-r", "--resume", action="store_true", help="Resume from the last successful profile")
    parser.add_argument("-s", "--start_index", type=int, help="Start index (1-based)")
    parser.add_argument("-e", "--end_index", type=int, help="End index (1-based)")
    parser.add_argument("-t", "--template", default=DEFAULT_TEMPLATE, help=f"Export template (default: {DEFAULT_TEMPLATE})")
    parser.add_argument("-f", "--force", action="store_true", help="Force export even if raw output file already exists")
    parser.add_argument("-w", "--workers", type=int, default=DEFAULT_WORKERS, help=f"Parallel workers (default: {DEFAULT_WORKERS})")
    parser.add_argument(
        "-l",
        "--lint_markdown_results",
        dest="lint_markdown_results",
        action="store_true",
        default=True,
        help="Run markdown linters on exported folders (default: enabled)"
    )
    parser.add_argument(
        "--no-lint_markdown_results", dest="lint_markdown_results", action="store_false", help="Disable markdown linting on exported folders"
    )
    parser.add_argument("-u", "--url", default=DEFAULT_API_URL, help=f"API Base URL (default: {DEFAULT_API_URL})")
    parser.add_argument("--no-reload", action="store_true", help="Skip initial API reload")

    args = parser.parse_args()
    api_url = args.url.rstrip('/')

    # 0. Pre-flight checks
    try:
        # Check connection & data
        test_resp = requests.get(f"{api_url}/test", timeout=5).json()
        if not test_resp.get("has_data"):
            cprint("❌ Server reports NO DATA LOADED. Check server config/setup.", "RED", bold=True)
            sys.exit(1)
        cprint(f"✅ Connected to UnityAssetsManager v{test_resp.get('version')} (Source: {test_resp.get('source_type')})", "GREEN")

        # Optional reload to ensure fresh cache
        if not args.no_reload:
            cprint("🔄 Triggering server-side data reload...", "CYAN")
            requests.post(f"{api_url}/reload", timeout=10)

        # Validate template
        templates_resp = requests.get(f"{api_url}/templates").json()
        available_templates = [t['name'] for t in templates_resp.get('templates', [])]
        if args.template not in available_templates:
            cprint(f"❌ Template '{args.template}' not found on server.", "RED", bold=True)
            cprint(f"Available: {', '.join(available_templates[:5])}...", "YELLOW")
            sys.exit(1)

        # Fetch profiles
        profiles_resp = requests.get(f"{api_url}/profiles")
        profiles_resp.raise_for_status()
        profiles = sorted(profiles_resp.json())
    except Exception as e:
        cprint(f"❌ Pre-flight check failed: {e}", "RED", bold=True)
        sys.exit(1)

    total = len(profiles)
    cprint(f"🔍 Found {total} profiles on server", "CYAN")

    # 2. Determine range
    start_idx = 0
    end_idx = total

    if args.resume:
        state = load_state()
        last_idx = state.get("last_index", 0)
        if 0 < last_idx < total:
            start_idx = last_idx
            cprint(f"🔃 Resuming from index {start_idx + 1} ({profiles[start_idx]})", "YELLOW")
        elif last_idx >= total and not args.force:
            cprint("✅ Cycle already finished. Use --force to restart from index 1.", "GREEN")
            return

    if args.start_index:
        start_idx = max(0, args.start_index - 1)

    if args.end_index:
        end_idx = min(total, args.end_index)

    target_profiles = profiles[start_idx:end_idx]
    if not target_profiles:
        cprint("⚠️ No profiles to process in the specified range.", "YELLOW")
        return

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    cprint(f"🚀 Processing profiles {start_idx + 1} to {end_idx} using {args.workers} workers", "GREEN", bold=True)
    exported_directories = {EXPORT_DIR}

    # 3. Parallel execution loop
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_profile = {}

        for i, profile in enumerate(target_profiles):
            if "default" in profile.lower() or "all_columns" in profile.lower():
                continue

            current_global_idx = start_idx + i
            output_file = EXPORT_DIR / f"{profile}{expected_output_suffix(args.template)}"

            if not args.force and output_file.exists():
                cprint(f"⏩ Skipping {profile}: already exists", "WHITE")
                save_state(profile, current_global_idx + 1)
                exported_directories.add(output_file.parent)
                continue

            future = executor.submit(export_profile, api_url, profile, args.template, output_file)
            future_to_profile[future] = (profile, current_global_idx, output_file.parent)

        completed = 0
        for future in concurrent.futures.as_completed(future_to_profile):
            profile, status_code, data = future.result()
            _, global_idx, output_directory = future_to_profile[future]
            completed += 1

            if status_code == 200 and data.get("status") == "success":
                save_state(profile, global_idx + 1)
                exported_directories.add(output_directory)
                cprint(f"✅ [{completed}/{len(future_to_profile)}] {profile}: Exported ({data.get('count')} rows)", "GREEN")
            else:
                error_msg = data.get("error", {}).get("message", "Unknown error")
                cprint(f"❌ [{completed}/{len(future_to_profile)}] {profile}: FAILED - {error_msg}", "RED", bold=True)
                # We stop the whole batch on error to investigate
                executor.shutdown(wait=False, cancel_futures=True)
                sys.exit(1)

    # 4. Final stats
    try:
        final_stats = requests.get(f"{api_url}/stats").json()
        cprint(f"\n✨ All {len(future_to_profile)} requested profiles processed successfully.", "GREEN", bold=True)
        cprint(f"📊 Total items in source: {final_stats.get('total_rows')}", "CYAN")
    except (Exception):
        pass

    if args.lint_markdown_results:
        run_markdown_lint(exported_directories)


if __name__ == "__main__":
    main()
