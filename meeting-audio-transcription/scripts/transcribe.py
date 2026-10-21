#!/usr/bin/env python3
"""Transcribe a 16kHz mono WAV with mlx-whisper (Apple Silicon).

Usage: transcribe.py <input.wav> <output.txt> [language]   (default: en)
Writes timestamped segments 'HH:MM:SS  text'; prints 'DONE <n> segments'.
Run via ~/.venvs/transcribe/bin/python as a background job (model download ~1.5 GB on first use).
"""
import sys

import mlx_whisper


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit("usage: transcribe.py <input.wav> <output.txt> [language]")
    src, dst = sys.argv[1], sys.argv[2]
    lang = sys.argv[3] if len(sys.argv) > 3 else "en"

    result = mlx_whisper.transcribe(
        src,
        path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
        language=lang,
        verbose=False,
    )

    lines = []
    for s in result["segments"]:
        ts = int(s["start"])
        lines.append(f"{ts // 3600:02d}:{ts % 3600 // 60:02d}:{ts % 60:02d}  {s['text'].strip()}")

    with open(dst, "w") as f:
        f.write("\n".join(lines))
    print("DONE", len(result["segments"]), "segments")


if __name__ == "__main__":
    main()
