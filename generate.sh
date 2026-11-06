#!/usr/bin/env bash
# Regenerate ArchLang spectacle marketing assets (box-local).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BLENDER="${BLENDER:-blender}"
mkdir -p "$ROOT/output/images" "$ROOT/output/videos" "$ROOT/output/previews"

echo "==> [1/4] Code-to-form hero"
"$BLENDER" --background --python "$ROOT/source/blender/01_code_to_form.py"

echo "==> [2/4] Recursive courtyard"
"$BLENDER" --background --python "$ROOT/source/blender/02_recursive_courtyard.py"

echo "==> [3/4] A-frame monument"
"$BLENDER" --background --python "$ROOT/source/blender/03_aframe_monument.py"

echo "==> [4/4] Assemble video frames + encode"
"$BLENDER" --background --python "$ROOT/source/blender/04_assemble_video.py"
FRAMES="$ROOT/output/videos/frames_assemble"
ffmpeg -y -framerate 12 -i "$FRAMES/frame_%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart \
  "$ROOT/output/videos/04-code-assemble.mp4"
ffmpeg -y -i "$ROOT/output/videos/04-code-assemble.mp4" -t 5 \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -an \
  "$ROOT/output/videos/04-code-assemble-loop5s.mp4"

cp -f "$ROOT/output/images/"*.png "$ROOT/output/previews/" 2>/dev/null || true
cp -f "$ROOT/output/videos/05-courtyard-grow-scored.mp4" "$ROOT/output/previews/" 2>/dev/null || true
cp -f "$ROOT/output/videos/04-code-assemble.mp4" "$ROOT/output/videos/04-code-assemble-loop5s.mp4" "$ROOT/output/previews/"


echo "==> [v2] Improved stills (real SVG projection)"
"$BLENDER" --background --python "$ROOT/source/blender/01_code_to_form_v2.py"
"$BLENDER" --background --python "$ROOT/source/blender/02_recursive_courtyard_v2.py"
"$BLENDER" --background --python "$ROOT/source/blender/03_aframe_monument_v2.py"

echo "==> [v2] Courtyard DEPTH grow motion"
"$BLENDER" --background --python "$ROOT/source/blender/05_courtyard_grow.py"
"$ROOT/pipeline/score_courtyard_grow.sh"

echo "==> Score assemble videos (real Mixkit + Kenney audio)"
"$ROOT/pipeline/score_assemble.sh"

echo "Done. Previews in $ROOT/output/previews/"
ls -lah "$ROOT/output/previews/"

# Full final package (preferred):
#   ./pipeline/generate_final.sh   or   make final
