#!/usr/bin/env bash
# Remux real royalty-free music + SFX onto the silent assemble videos.
# Requires: source/audio assets already downloaded (see source/audio/CREDITS.md).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTA="$ROOT/output/audio"
V="$ROOT/output/videos"
mkdir -p "$OUTA" "$ROOT/output/previews"

need() { [[ -f "$1" ]] || { echo "Missing $1 — restore from source/audio or re-download (CREDITS.md)"; exit 1; }; }
need "$ROOT/source/audio/music/vastness-andrew-ev-mixkit-184.mp3"
need "$ROOT/source/audio/sfx/kenney/tick_001.ogg"
need "$ROOT/source/audio/sfx/mixkit/arrow-whoosh-1492.mp3"
need "$V/04-code-assemble.mp4"

# WAV workspace
ffmpeg -y -i "$ROOT/source/audio/music/vastness-andrew-ev-mixkit-184.mp3" -ar 48000 -ac 2 "$OUTA/vastness.wav" </dev/null
for f in tick_001 tick_002 tick_004 click_001 click_002 click_003 confirmation_002 pluck_001 pluck_002 open_002; do
  ffmpeg -y -i "$ROOT/source/audio/sfx/kenney/${f}.ogg" -ar 48000 -ac 2 "$OUTA/${f}.wav" </dev/null
done
ffmpeg -y -i "$ROOT/source/audio/sfx/mixkit/arrow-whoosh-1492.mp3" -ar 48000 -ac 2 "$OUTA/arrow-whoosh-1492.wav" </dev/null
ffmpeg -y -i "$ROOT/source/audio/sfx/mixkit/cinematic-whoosh-fast-transition-1489.mp3" -ar 48000 -ac 2 "$OUTA/cinematic-whoosh-fast-transition-1489.wav" </dev/null

# 6s main bed
ffmpeg -y \
  -ss 20 -t 6 -i "$OUTA/vastness.wav" \
  -i "$OUTA/tick_001.wav" -i "$OUTA/tick_002.wav" -i "$OUTA/tick_004.wav" \
  -i "$OUTA/click_001.wav" -i "$OUTA/click_002.wav" -i "$OUTA/click_003.wav" \
  -i "$OUTA/arrow-whoosh-1492.wav" -i "$OUTA/cinematic-whoosh-fast-transition-1489.wav" \
  -i "$OUTA/open_002.wav" -i "$OUTA/pluck_001.wav" -i "$OUTA/confirmation_002.wav" -i "$OUTA/pluck_002.wav" \
  -filter_complex "\
    [0:a]afade=t=in:st=0:d=0.35,afade=t=out:st=5.4:d=0.55,volume=0.28[music];\
    [1:a]volume=0.55,adelay=350|350[t1];[2:a]volume=0.50,adelay=700|700[t2];[3:a]volume=0.55,adelay=1050|1050[t3];\
    [4:a]volume=0.45,adelay=1400|1400[c1];[5:a]volume=0.45,adelay=1750|1750[c2];[6:a]volume=0.45,adelay=2100|2100[c3];\
    [1:a]volume=0.50,adelay=2500|2500[t4];[3:a]volume=0.50,adelay=2900|2900[t5];\
    [4:a]volume=0.40,adelay=3300|3300[c4];[5:a]volume=0.40,adelay=3700|3700[c5];\
    [7:a]volume=0.55,adelay=800|800[w1];[8:a]volume=0.40,adelay=2200|2200[w2];\
    [9:a]volume=0.50,adelay=4500|4500[op];[10:a]volume=0.70,adelay=4800|4800[pl1];\
    [11:a]volume=0.55,adelay=5000|5000[conf];[12:a]volume=0.65,adelay=5300|5300[pl2];\
    [music][t1][t2][t3][c1][c2][c3][t4][t5][c4][c5][w1][w2][op][pl1][conf][pl2]amix=inputs=17:duration=first:dropout_transition=0:normalize=0[mix];\
    [mix]alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11[out]" \
  -map "[out]" -t 6 -ar 48000 -ac 2 -c:a aac -b:a 192k "$OUTA/assemble-main-bed.m4a" </dev/null

# 5s loop bed
ffmpeg -y \
  -ss 45 -t 5 -i "$OUTA/vastness.wav" \
  -i "$OUTA/tick_001.wav" -i "$OUTA/tick_002.wav" -i "$OUTA/tick_004.wav" \
  -i "$OUTA/click_001.wav" -i "$OUTA/arrow-whoosh-1492.wav" \
  -i "$OUTA/pluck_001.wav" -i "$OUTA/confirmation_002.wav" \
  -filter_complex "\
    [0:a]afade=t=in:st=0:d=0.25,afade=t=out:st=4.6:d=0.35,volume=0.26[music];\
    [1:a]volume=0.48,adelay=300|300[t1];[2:a]volume=0.45,adelay=800|800[t2];[3:a]volume=0.48,adelay=1300|1300[t3];\
    [4:a]volume=0.40,adelay=1800|1800[c1];[1:a]volume=0.45,adelay=2300|2300[t4];[2:a]volume=0.45,adelay=2800|2800[t5];\
    [5:a]volume=0.50,adelay=600|600[w1];[6:a]volume=0.60,adelay=3600|3600[pl];[7:a]volume=0.50,adelay=4000|4000[conf];\
    [music][t1][t2][t3][c1][t4][t5][w1][pl][conf]amix=inputs=10:duration=first:dropout_transition=0:normalize=0[mix];\
    [mix]alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11[out]" \
  -map "[out]" -t 5 -ar 48000 -ac 2 -c:a aac -b:a 192k "$OUTA/assemble-loop-bed.m4a" </dev/null

ffmpeg -y -i "$V/04-code-assemble.mp4" -i "$OUTA/assemble-main-bed.m4a" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart \
  "$V/04-code-assemble-scored.mp4" </dev/null
ffmpeg -y -i "$V/04-code-assemble-loop5s.mp4" -i "$OUTA/assemble-loop-bed.m4a" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart \
  "$V/04-code-assemble-loop5s-scored.mp4" </dev/null
if [[ -f "$V/04-code-assemble-24fps.mp4" ]]; then
  ffmpeg -y -i "$V/04-code-assemble-24fps.mp4" -i "$OUTA/assemble-main-bed.m4a" \
    -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart \
    "$V/04-code-assemble-24fps-scored.mp4" </dev/null || true
fi
cp -f "$V/04-code-assemble-scored.mp4" "$V/04-code-assemble-loop5s-scored.mp4" "$ROOT/output/previews/"
echo "Scored videos ready:"
ls -lah "$V"/04-code-assemble*-scored.mp4
