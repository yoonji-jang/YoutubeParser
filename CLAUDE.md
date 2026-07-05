# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Install dependencies:
```
pip install -r requirement.txt
```
`requirement.txt` is stale — it's missing packages that the code actually imports (`google-api-python-client` / `googleapiclient`, `openpyxl`, `tqdm`, `webdriver-manager`). Install those manually if setting up a fresh environment.

Run each analysis mode from source, from the repo root (mirrors the `run/<mode>/run_*.bat` launchers, which invoke the packaged `.exe` instead):
```
python main.py --va -input run/video/input_video.txt                      # video analysis
python main.py --ia -input run/influencer/input_influencer.txt --yc --yv  # influencer analysis (channel/video)
python main.py --yb -input run/bulk/input_bulk.txt                        # channel bulk analysis
python main.py --tc -input run/tech_community/input_tech_community.txt    # tech community analysis
```
The `.vscode/launch.json` debug config runs `--va -input run/video/input_video.txt` by default.

Build the standalone Windows executable:
```
pyinstaller YoutubeParser.spec
```
The `.bat` launchers under `run/<mode>/` invoke the built exe via a relative `..\..\YoutubeParser.exe`, so they only work when `YoutubeParser.exe` sits at the repo root (next to `src/` and `run/`) and are run from within their own `run/<mode>/` folder — double-clicking them is fine since Windows sets cwd to the `.bat`'s own directory.

There is no test suite and no linter configuration in this repo.

## Architecture

**Entry point (`main.py`)** parses CLI flags and dispatches to exactly one of four analysis pipelines: `--va` (video), `--ia` (influencer), `--yb` (channel bulk), `--tc` (tech community). Each pipeline reads its own `-input <file>` config and is otherwise independent — there is no shared orchestration beyond dispatch.

**Layout**: source code lives under `src/`, split by role; runtime config/launchers/generated output live under `run/`, split by mode. They are kept separate so users driving the tool via the `.bat` files never need to touch `src/`.
```
src/
  core/            # shared by all 4 modes
    driver.py                 # selenium driver instances
    excel_func.py              # output writer (csv/xlsx)
    youtube_parser.py          # YouTube page scraping (Selenium + BeautifulSoup)
    youtube_video_analysis.py  # YouTube Data API v3 wrapper + dev-key rotation
  video/           analysis.py, input_parser.py
  influencer/      analysis.py, input_parser.py
  bulk/            analysis.py, input_parser.py
  tech_community/  analysis.py, input_parser.py, parser.py, post_analysis.py
run/
  video/           input_video.txt, run_video_analysis.bat, (output lands here)
  influencer/      input_influencer.txt, run_influencer_analysis.bat, (output lands here)
  bulk/            input_bulk.txt, run_bulk_analysis.bat, (output lands here)
  tech_community/  input_tech_community.txt, run_tech_community_analysis.bat, (output lands here)
```
All internal imports use absolute paths rooted at `src` (e.g. `from src.core.driver import *`, `from src.video.input_parser import parse_input_data`), so `main.py` must stay at the repo root and be run with the repo root as the working directory / on `sys.path`.

**Shared Selenium driver (`src/core/driver.py`)**: module-level `driver` and `driver_video` headless Chrome instances are created once at import time and reused across every pipeline via `from src.core.driver import *`. Any change to browser options/headless behavior affects all four modes simultaneously.

**Per-pipeline structure**: video, influencer, and bulk analysis each follow the same three-stage shape, split across two files per mode plus the shared `core` modules:
1. `<mode>/input_parser.py` — reads a `KEY=VALUE`-per-line `.txt` config (hand-rolled parsing, not JSON/YAML) into a tuple of typed values (dates parsed as `time.struct_time`, comma-separated lists split manually).
2. `<mode>/analysis.py` — orchestrator: loops over keywords/channels, calls the scraper to collect video thumbnails/links, then calls the analysis step to enrich each with stats, then writes output.
3. Scrape + enrich: `core/youtube_parser.py` (Selenium + BeautifulSoup, scrolls YouTube search/channel pages to collect video links) feeds into `core/youtube_video_analysis.py` (YouTube Data API v3 calls per video/channel ID).

**Influencer analysis (`src/influencer/analysis.py`) is the outlier**: instead of a plain keyword/date sweep, it reads rows from an input Excel workbook (one sheet for channels, one for videos, row/column range configured in the input `.txt`) and writes stats back into the same workbook cells in place — including downloading and embedding channel/video thumbnail images directly into cells via `openpyxl`.

**Tech community analysis (`--tc`) does not use the YouTube API at all** — `src/tech_community/parser.py` and `src/tech_community/post_analysis.py` scrape non-YouTube forum sites (quasarzone, coolenjoy) by keyword/date via Selenium + BeautifulSoup, with separate CSS-selector logic per site.

**YouTube Data API key rotation (`src/core/youtube_video_analysis.py`)**: `DEV_KEY` in the input config is a comma-separated list of API keys. `GetDevKeyAvailable`/`UseNextDevKey` track a module-level index and automatically advance to the next key whenever a response contains `quotaExceeded` or `API_KEY_INVALID`, falling through pipelines when all keys are exhausted (`RETURN_ERR = -1`, checked by callers after every request). The index (`GetDevKeyAvailable.key_ind`) only ever increases for the lifetime of the process — once a key is marked exhausted it is never revisited, even across separate keyword/channel loop iterations within the same run.

**Output (`src/core/excel_func.py`)**: every pipeline (except influencer analysis, which writes to its input workbook directly) converts its collected list-of-dicts to a DataFrame and writes to `.csv` or `.xlsx` based on the output path's extension, via `make_excel`. Output paths are resolved relative to the process's working directory — running via the `.bat` launchers (cwd = `run/<mode>/`) lands output next to that mode's input config.

## Known issues / gotchas

- **`main.py`'s `-input` default is stale**: it defaults to `"input_video.txt"` at the repo root, but that file was moved to `run/video/input_video.txt` during the `src/`/`run/` reorg and no longer exists at the root. Running without `-input` fails trying to open a nonexistent file — always pass `-input run/<mode>/input_<mode>.txt` explicitly (as the `.bat` launchers and `launch.json` already do).
- **Global dedup/rotation state is process-lifetime, not per-loop-iteration**: `youtube_video_analysis.py`'s module-level `vIDs` list dedups video IDs across the *entire* run of `--va`/`--yb`, so a video matching multiple keywords is only ever recorded under the first keyword it was seen under, not every keyword it matches. Combined with the dev-key rotation note above, this means behavior can depend on keyword/channel ordering in the input config.
- **`excel_func.py`'s `.xlsx` branch is likely broken**: `df.to_excel(output_path, encoding='utf-8-sig', index=False)` passes `encoding`, which `DataFrame.to_excel` does not accept (that kwarg is `to_csv`-only) — this can raise `TypeError` or otherwise misbehave depending on installed pandas/openpyxl versions. This affects any mode configured with an `OUTPUT`/`OUTPUT_EXCEL` path ending in `.xlsx` (e.g. some `input_tech_community.txt` configs use `.xlsx`); `.csv` output is unaffected. Verify pandas' current `to_excel` signature before relying on `.xlsx` output.
- **Dead/vestigial code** — don't assume these are load-bearing when tracing behavior or refactoring nearby code:
  - `driver.py:7-8` fetches `chromedriver.storage.googleapis.com/LATEST_RELEASE` into `version` at import time (on every run of every mode); the value is never used. Pure overhead, and that endpoint is deprecated for current Chrome anyway.
  - `excel_func.py`'s `Workbook`/`dataframe_to_rows`/`Font` hyperlink-styling block is entirely commented out; only the `to_csv`/`to_excel` write actually executes.
  - `core/youtube_parser.py`'s `get_video_data()` (BeautifulSoup-based stats scraping) is unused — `video/analysis.py` calls the API-based `run_VideoAnalysis` instead and its call to `get_video_data` is commented out.
  - `youtube_video_analysis.py`'s module-level `cIndex = make_enum(...)` is defined but never referenced anywhere (`influencer/analysis.py` defines its own separate `cIndex`).
- **Duplicate logic worth knowing about before extending**: all four `<mode>/input_parser.py` files repeat the identical "readlines → split on `=` → dict" parsing verbatim; `make_enum` is defined separately in both `youtube_video_analysis.py` and `influencer/analysis.py`; the `try: make_excel / except / driver.quit() / driver_video.quit()` teardown is repeated verbatim across `video`/`bulk`/`tech_community`'s `analysis.py`; `tech_community/parser.py`'s `search_quasarzone`/`search_coolenjoy` share an identical pagination/date-check skeleton differing only in CSS selectors; `youtube_video_analysis.py`'s `get_video_data`/`get_video_data_simple` are ~90% identical (only channel-info enrichment differs). None of this is broken, but changes to one copy likely need mirroring in the others until consolidated.

## Notes

- `run/<mode>/input_*.txt` files are runtime configuration (keywords, date ranges, output paths, and comma-separated YouTube Data API `DEV_KEY` lists) rather than source code — several are already tracked in git with real-looking API keys embedded. Treat these as machine-specific/secret-bearing config, not code to refactor.
- Korean-language strings appear throughout (input keywords, Excel column headers like `조회수`/`좋아요 수`/`구독자 수`); preserve them exactly when touching output schemas.
- Log messages follow a `"[Info] ..."` / `"[Warning] ..."` / `"[Error] ..."` prefix convention — match it in any new logging.
