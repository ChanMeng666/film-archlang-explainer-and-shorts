#!/usr/bin/env bash
# Encode + score courtyard-grow with the same real Mixkit/Kenney audio stack.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTA="$ROOT/output/audio"
V="$ROOT/output/videos"
FRAMES="$V/frames_courtyard_grow"
mkdir -p "$OUTA" "$ROOT/output/previews"

[[ -d "$FRAMES" ]] || { echo "Missing frames $FRAMES"; exit 1; }
n=$(ls "$FRAMES"/frame_*.png 2>/dev/null | wc -l)
[[ "$n" -gt 10 ]] || { echo "Too few frames: $n"; exit 1; }

# Silent master
ffmpeg -y -framerate 12 -i "$FRAMES/frame_%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart \
  "$V/05-courtyard-grow.mp4"

# Ensure WAV assets exist (reuse from assemble score)
need_wav() {
  local name="$1" src="$2"
  if [[ ! -f "$OUTA/$name" ]]; then
    ffmpeg -y -i "$src" -ar 48000 -ac 2 "$OUTA/$name" </dev/null
  fi
}
need_wav vastness.wav "$ROOT/source/audio/music/vastness-andrew-ev-mixkit-184.mp3"
need_wav tick_001.wav "$ROOT/source/audio/sfx/kenney/tick_001.ogg"
need_wav tick_002.wav "$ROOT/source/audio/sfx/kenney/tick_002.ogg"
need_wav tick_004.wav "$ROOT/source/audio/sfx/kenney/tick_004.ogg"
need_wav click_001.wav "$ROOT/source/audio/sfx/kenney/click_001.ogg"
need_wav confirmation_002.wav "$ROOT/source/audio/sfx/kenney/confirmation_002.ogg"
need_wav pluck_001.wav "$ROOT/source/audio/sfx/kenney/pluck_001.ogg"
need_wav open_002.wav "$ROOT/source/audio/sfx/kenney/open_002.ogg"
need_wav arrow-whoosh-1492.wav "$ROOT/source/audio/sfx/mixkit/arrow-whoosh-1492.mp3"
need_wav cinematic-whoosh-fast-transition-1489.wav "$ROOT/source/audio/sfx/mixkit/cinematic-whoosh-fast-transition-1489.mp3"

DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$V/05-courtyard-grow.mp4")

# Bed: Vastness from 30s + ring whooshes on each depth birth (~0.5,1.5,2.5,3.5,4.5s) + ticks + settle
ffmpeg -y \
  -ss 30 -t "$DUR" -i "$OUTA/vastness.wav" \
  -i "$OUTA/tick_001.wav" -i "$OUTA/tick_002.wav" -i "$OUTA/tick_004.wav" \
  -i "$OUTA/click_001.wav" \
  -i "$OUTA/arrow-whoosh-1492.wav" \
  -i "$OUTA/cinematic-whoosh-fast-transition-1489.wav" \
  -i "$OUTA/open_002.wav" -i "$OUTA/pluck_001.wav" -i "$OUTA/confirmation_002.wav" \
  -filter_complex "\
    [0:a]afade=t=in:st=0:d=0.3,afade=t=out:st=$(python3 -c "print(max(0, float('$DUR')-0.45))"):d=0.4,volume=0.26[music];\
    [1:a]volume=0.45,adelay=400|400[t1];\
    [2:a]volume=0.42,adelay=900|900[t2];\
    [3:a]volume=0.45,adelay=1400|1400[t3];\
    [4:a]volume=0.40,adelay=2000|2000[c1];\
    [1:a]volume=0.42,adelay=2600|2600[t4];\
    [2:a]volume=0.42,adelay=3200|3200[t5];\
    [3:a]volume=0.42,adelay=3800|3800[t6];\
    [4:a]volume=0.38,adelay=4400|4400[c2];\
    [5:a]volume=0.52,adelay=500|500[w1];\
    [5:a]volume=0.48,adelay=1500|1500[w2];\
    [5:a]volume=0.48,adelay=2500|2500[w3];\
    [6:a]volume=0.38,adelay=3500|3500[w4];\
    [5:a]volume=0.50,adelay=4500|4500[w5];\
    [7:a]volume=0.50,adelay=5200|5200[op];\
    [8:a]volume=0.65,adelay=5600|5600[pl];\
    [9:a]volume=0.55,adelay=5900|5900[conf];\
    [music][t1][t2][t3][c1][t4][t5][t6][c2][w1][w2][w3][w4][w5][op][pl][conf]amix=inputs=17:duration=first:dropout_transition=0:normalize=0[mix];\
    [mix]alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11[out]" \
  -map "[out]" -t "$DUR" -ar 48000 -ac 2 -c:a aac -b:a 192k "$OUTA/courtyard-grow-bed.m4a" </dev/null

ffmpeg -y -i "$V/05-courtyard-grow.mp4" -i "$OUTA/courtyard-grow-bed.m4a" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart \
  "$V/05-courtyard-grow-scored.mp4" </dev/null

cp -f "$V/05-courtyard-grow-scored.mp4" "$ROOT/output/previews/"
echo "Wrote $V/05-courtyard-grow-scored.mp4"
ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,duration -show_entries format=duration -of default=nw=1 "$V/05-courtyard-grow-scored.mp4"
