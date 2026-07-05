import os
import sys
import tempfile
from pathlib import Path

from src.ui.config_io import write_key_value_txt

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_SCRIPT = REPO_ROOT / "main.py"

# Mirrors the `.bat` launchers under run/<mode>/: same entry point (main.py), same
# mode flag, same working directory convention (so relative OUTPUT paths land next
# to that mode's input config, exactly like running the launcher by hand).
MODE_INFO = {
    "video": {"flag": "--va", "run_dir": REPO_ROOT / "run" / "video"},
    "bulk": {"flag": "--yb", "run_dir": REPO_ROOT / "run" / "bulk"},
    "tech_community": {"flag": "--tc", "run_dir": REPO_ROOT / "run" / "tech_community"},
    "influencer": {"flag": "--ia", "run_dir": REPO_ROOT / "run" / "influencer"},
}


def write_temp_config(pairs):
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="youtubeparser_ui_")
    os.close(fd)
    write_key_value_txt(path, pairs)
    return path


def build_process_args(mode, config_pairs, extra_flags=None):
    """Build (program, arguments, working_dir, temp_config_path) for one analysis run.

    Launches `python -u main.py <mode flag> -input <temp config>` as a fresh subprocess,
    the same entry point the CLI and .bat launchers use, so it picks up none of the
    shared-driver/dev-key module state quirks a long-lived in-process run would hit.
    """
    info = MODE_INFO[mode]
    config_path = write_temp_config(config_pairs)
    args = ["-u", str(MAIN_SCRIPT), info["flag"], "-input", config_path]
    if extra_flags:
        args += extra_flags
    return sys.executable, args, str(info["run_dir"]), config_path
