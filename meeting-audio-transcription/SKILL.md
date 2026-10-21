---
name: meeting-audio-transcription
description: Transcribe meeting audio/video and summarize to notes.
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [transcription, whisper, meetings, obsidian]
    related_skills: [obsidian, notion-meeting-transcripts]
---

# Meeting Audio/Video → Transcript → Obsidian Summary

Full pipeline: local media file → timestamped transcript (Whisper, on-device) → structured meeting-summary note routed into Greg's vault.

## When to use
- Greg shares a meeting recording (mp4/wav/m4a, often `GMT…_Recording…` named) and asks for a transcript and/or summary.
- A referenced transcript attachment turns out to be a stub and the source recording must be transcribed instead.
- A meeting summary needs filing into the Obsidian vault with the dated-note convention (pairs with the obsidian skill).

## Step 1 — Inspect the media first
- Confirm existence/size with search_files (target='files'); get duration with `mdls -name kMDItemDurationSeconds <file>`. **No ffprobe/ffmpeg/Homebrew on this Mac** — `mdls` is the duration source.
- Before doing anything, sanity-check any attached transcript text the user provides: attachments are sometimes truncated fragments (e.g. 51 bytes = one line). Report truncation instead of summarizing a stub.
- Filenames like `GMT20261015-160311_Recording...` encode the meeting start: `GMT` + `YYYYMMDD-HHMMSS` **UTC**; convert to local (EDT = UTC−4, EST = UTC−5) for the note date.
- Whisper timestamps are relative to audio start; if the recording began mid-meeting, say so in the summary header.

## Step 2 — Extract audio (macOS built-in)
```bash
afconvert -f WAVE -d LEI16@16000 -c 1 input.mp4 output.wav
```
16 kHz mono WAV is exactly what Whisper wants (~160 MB per 90 min). Put the WAV next to the source file unless told otherwise.

## Step 3 — Environment (check before installing)
```bash
~/.venvs/transcribe/bin/python -c "import mlx_whisper" && echo READY
```
If missing: `python3 -m venv ~/.venvs/transcribe && ~/.venvs/transcribe/bin/pip install mlx-whisper`.
- **PyPI read-times out on this network** (15 s read timeouts, retries). Run the install as a background terminal job with notify=true; a foreground attempt will hit the 420 s cap. Mirror fallback if pypi keeps failing: `-i https://pypi.tuna.tsinghua.edu.cn/simple`.
- mlx-whisper (Apple Silicon Metal) is preferred over openai-whisper/faster-whisper here.

## Step 4 — Transcribe
Run `scripts/transcribe.py` (in this skill) as a **background terminal job** — 89 min of audio takes minutes on M-series, plus a ~1.5 GB model download on first use:
```bash
~/.venvs/transcribe/bin/python ~/.hermes/skills/productivity/meeting-audio-transcription/scripts/transcribe.py \
  /abs/path/input.wav /abs/path/output_transcript.txt en
```
Model: `mlx-community/whisper-large-v3-turbo`. Output format: `HH:MM:SS  text` per segment. Job prints `DONE <n> segments` on success — watch for `DONE`/`Traceback`.

## Step 5 — Summarize
Read the WHOLE transcript (paginated `read_file` — an 89-min meeting is ~95 KB / ~1800 lines; two reads). Then write the note matching the target folder's existing convention (check sibling notes first — e.g. Loomstate WMS notes use `Title_Summary_YYYY-MM-DD.md`). Standard structure:
1. H1 title, then the single meeting timestamp header: `**Date:**` weekday + meeting date (from GMT filename) + local start time (UTC→EDT/EST) + duration — one wall-clock stamp for when the meeting took place, at the top only. Then `**Attendees/parties:**` and `**Source:**` with wikilink to the transcript copy.
2. Background (1–2 bullets: meeting purpose, context).
3. Thematic `##` sections — findings, config walkthrough, risks (no timestamps in headings or body).
4. `## Decisions` (numbered).
5. `## Action items` — markdown table `| Owner | Action |` with deadlines where stated.
6. `## Schedule notes` (next session, cadence) if discussed.
Capture concrete specifics (numbers, module names, settings, passwords shared in calls, deadlines) — Greg treats these notes as the project record. Keep timestamps ONLY in the header stamp and in the attached full transcript — no per-section or per-item timestamps in the summary.

## Step 6 — Route into the vault
- Destination folder dictated by Greg → use EXACTLY as typed (see obsidian skill for vault conventions: `~/Greggy-AI`).
- Copy the transcript into an `attachments/` subfolder of the target folder (matches `RF Smart Pick-to-Carton Beta/attachments/` precedent) and wikilink it from the note: `[[attachments/GMT..._transcript.txt|full timestamped transcript]]`.
- Cross-link related meeting notes with bare wikilinks when sibling notes exist.
- Verify both files on disk (search_files target='files' on the target folder) before claiming done — Greg expects proof, not inference.

## Pitfalls
- `notify` param rejects stringified booleans; pass real `true` or a patterns list like `["DONE", "Traceback"]`.
- Interrupted side-effecting commands (orphan recovery) may have completed anyway — always re-check state (`import` check, `ls`) before retrying installs/writes.
- Don't summarize from memory of the call — read the full transcript first; details like exact dimensions, counts (e.g. ~6,460 bins, ~150K containers), and per-owner actions come from the text.
- Scrubbing/verification: transcript file should have roughly `duration_secs / 3` lines; wildly fewer = something failed.
- Summary timestamp style (Greg's preference): ONE meeting stamp at the top (date + local start + duration); no inline timestamps in sections, decisions, or action items — granular timing lives in the attached transcript only.
- Version bump pattern for this skill: doc-structure additions are minor — patch content and bump the patch/minor version in frontmatter.
