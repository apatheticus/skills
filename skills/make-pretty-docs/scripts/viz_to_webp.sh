#!/usr/bin/env bash
#
# viz_to_webp.sh — convert a rendered HyperFrames composition into a
# GitHub-safe, seamless-loop animated WebP under a hard size budget.
#
# Reads <composition-dir>/render.mp4 (produced by `hyperframes render`),
# extracts frames with ffmpeg, and assembles a looping WebP with img2webp.
# Fails loudly if the output exceeds 2.5 MB so an oversized asset can never
# be committed.
#
# Usage:
#   viz_to_webp.sh <composition-dir> <output.webp> [fps] [width] [quality]
#
# Defaults: fps=15  width=1200  quality=68
#
# Dependencies: bash, coreutils, ffmpeg, img2webp (from Google's webp tools).
#   macOS ffmpeg is usually built WITHOUT libwebp, so img2webp is shipped
#   separately: `brew install webp`.

set -euo pipefail

die() { printf 'viz_to_webp: %s\n' "$1" >&2; exit 1; }

# --- arguments ---------------------------------------------------------------
[ "$#" -ge 2 ] || die "usage: viz_to_webp.sh <composition-dir> <output.webp> [fps] [width] [quality]"

comp_dir=$1
output=$2
fps=${3:-15}
width=${4:-1200}
quality=${5:-68}

max_bytes=2621440   # 2.5 MiB hard budget

# --- dependency checks -------------------------------------------------------
command -v ffmpeg >/dev/null 2>&1 || die "ffmpeg not found on PATH."
command -v img2webp >/dev/null 2>&1 || die "img2webp not found. On macOS: brew install webp"

# --- input validation --------------------------------------------------------
mp4="$comp_dir/render.mp4"
[ -d "$comp_dir" ] || die "composition dir not found: $comp_dir"
[ -f "$mp4" ] || die "render.mp4 not found in $comp_dir (run: npx hyperframes render --quality high --output render.mp4)"

case "$fps" in (*[!0-9]*|'') die "fps must be a positive integer: $fps";; esac
case "$width" in (*[!0-9]*|'') die "width must be a positive integer: $width";; esac
case "$quality" in (*[!0-9]*|'') die "quality must be an integer: $quality";; esac

# Per-frame duration in ms. img2webp -d wants milliseconds; d = round(1000/fps).
delay=$(( (1000 + fps / 2) / fps ))

# --- extract frames ----------------------------------------------------------
frames_dir="$comp_dir/frames"
rm -rf "$frames_dir"
mkdir -p "$frames_dir"

ffmpeg -y -loglevel error -i "$mp4" \
  -vf "fps=${fps},scale=${width}:-2" \
  "$frames_dir/f_%04d.png"

# zsh/bash-portable glob check: make sure frames were actually produced.
set -- "$frames_dir"/f_*.png
[ -e "$1" ] || die "no frames extracted from $mp4"

# --- assemble WebP -----------------------------------------------------------
img2webp -loop 0 -d "$delay" -lossy -q "$quality" -m 6 "$frames_dir"/f_*.png -o "$output"
[ -f "$output" ] || die "img2webp produced no output at $output"

# --- size budget -------------------------------------------------------------
bytes=$(wc -c < "$output")
bytes=$(( bytes + 0 ))   # strip any leading whitespace from wc

if [ "$bytes" -gt "$max_bytes" ]; then
  rm -f "$output"
  printf 'viz_to_webp: output %d bytes exceeds budget %d bytes (2.5 MB). Deleted.\n' "$bytes" "$max_bytes" >&2
  printf 'Remedies, in order:\n' >&2
  printf '  1. Shorten the loop duration (fewer frames).\n' >&2
  printf '  2. Lower quality (current -q %s; try %s).\n' "$quality" "$(( quality - 8 ))" >&2
  printf '  3. Reduce width (current %s; try %s).\n' "$width" "$(( width - 240 ))" >&2
  printf '  4. Simplify motion so more regions stay static between frames.\n' >&2
  exit 1
fi

printf 'OK %s %d bytes\n' "$output" "$bytes"
