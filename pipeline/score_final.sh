#!/usr/bin/env bash
# Encode 24fps finals + score with Mixkit Vastness / Kenney / Mixkit whoosh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTA="$ROOT/output/audio"
VF="$ROOT/output/videos/final"
PREV="$ROOT/output/previews/final"
mkdir -p "$OUTA" "$VF" "$PREV"

need_wav() {
  local name="$1" src="$2"
  if [[ ! -f "$OUTA/$name" ]]; then
    ffmpeg -y -i "$src" -ar 48000 -ac 2 "$OUTA/$name" </dev/null 2>/dev/null
  fi
}
need_wav vastness.wav "$ROOT/source/audio/music/vastness-andrew-ev-mixkit-184.mp3"
need_wav tick_001.wav "$ROOT/source/audio/sfx/kenney/tick_001.ogg"
need_wav tick_002.wav "$ROOT/source/audio/sfx/kenney/tick_002.ogg"
need_wav tick_004.wav "$ROOT/source/audio/sfx/kenney/tick_004.ogg"
need_wav click_001.wav "$ROOT/source/audio/sfx/kenney/click_001.ogg"
need_wav click_002.wav "$ROOT/source/audio/sfx/kenney/click_002.ogg"
need_wav click_003.wav "$ROOT/source/audio/sfx/kenney/click_003.ogg"
need_wav confirmation_002.wav "$ROOT/source/audio/sfx/kenney/confirmation_002.ogg"
need_wav pluck_001.wav "$ROOT/source/audio/sfx/kenney/pluck_001.ogg"
need_wav pluck_002.wav "$ROOT/source/audio/sfx/kenney/pluck_002.ogg"
need_wav open_002.wav "$ROOT/source/audio/sfx/kenney/open_002.ogg"
need_wav arrow-whoosh-1492.wav "$ROOT/source/audio/sfx/mixkit/arrow-whoosh-1492.mp3"
need_wav cinematic-whoosh-fast-transition-1489.wav "$ROOT/source/audio/sfx/mixkit/cinematic-whoosh-fast-transition-1489.mp3"

encode_silent() {
  local frames="$1" out="$2" fps="$3"
  ffmpeg -y -framerate "$fps" -i "$frames/frame_%04d.png" \
    -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart "$out"
}

# --- 04 assemble 6s ---
FA="$ROOT/output/videos/frames_assemble_final"
encode_silent "$FA" "$VF/04-code-assemble-final.mp4" 24
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VF/04-code-assemble-final.mp4")
ffmpeg -y \
  -ss 20 -t "$DUR" -i "$OUTA/vastness.wav" \
  -i "$OUTA/tick_001.wav" -i "$OUTA/tick_002.wav" -i "$OUTA/tick_004.wav" \
  -i "$OUTA/click_001.wav" -i "$OUTA/click_002.wav" -i "$OUTA/click_003.wav" \
  -i "$OUTA/arrow-whoosh-1492.wav" -i "$OUTA/cinematic-whoosh-fast-transition-1489.wav" \
  -i "$OUTA/open_002.wav" -i "$OUTA/pluck_001.wav" -i "$OUTA/confirmation_002.wav" -i "$OUTA/pluck_002.wav" \
  -filter_complex "\
    [0:a]afade=t=in:st=0:d=0.3,afade=t=out:st=$(python3 -c "print(max(0,float('$DUR')-0.5))"):d=0.45,volume=0.27[music];\
    [1:a]volume=0.55,adelay=350|350[t1];[2:a]volume=0.50,adelay=700|700[t2];[3:a]volume=0.55,adelay=1050|1050[t3];\
    [4:a]volume=0.45,adelay=1400|1400[c1];[5:a]volume=0.45,adelay=1750|1750[c2];[6:a]volume=0.45,adelay=2100|2100[c3];\
    [1:a]volume=0.50,adelay=2500|2500[t4];[3:a]volume=0.50,adelay=2900|2900[t5];\
    [4:a]volume=0.40,adelay=3300|3300[c4];[5:a]volume=0.40,adelay=3700|3700[c5];\
    [7:a]volume=0.55,adelay=800|800[w1];[8:a]volume=0.40,adelay=2200|2200[w2];\
    [9:a]volume=0.50,adelay=4500|4500[op];[10:a]volume=0.70,adelay=4800|4800[pl1];\
    [11:a]volume=0.55,adelay=5000|5000[conf];[12:a]volume=0.65,adelay=5300|5300[pl2];\
    [music][t1][t2][t3][c1][c2][c3][t4][t5][c4][c5][w1][w2][op][pl1][conf][pl2]amix=inputs=17:duration=first:dropout_transition=0:normalize=0[mix];\
    [mix]alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11[out]" \
  -map "[out]" -t "$DUR" -ar 48000 -ac 2 -c:a aac -b:a 192k "$OUTA/assemble-final-bed.m4a" </dev/null
ffmpeg -y -i "$VF/04-code-assemble-final.mp4" -i "$OUTA/assemble-final-bed.m4a" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart \
  "$VF/04-code-assemble-final-scored.mp4" </dev/null

# 5s loop cut from silent + loop-friendly bed
ffmpeg -y -i "$VF/04-code-assemble-final.mp4" -t 5 -c:v copy -an "$VF/04-code-assemble-loop5s-final.mp4" </dev/null
ffmpeg -y \
  -ss 45 -t 5 -i "$OUTA/vastness.wav" \
  -i "$OUTA/tick_001.wav" -i "$OUTA/tick_002.wav" -i "$OUTA/tick_004.wav" \
  -i "$OUTA/click_001.wav" -i "$OUTA/arrow-whoosh-1492.wav" \
  -i "$OUTA/pluck_001.wav" -i "$OUTA/confirmation_002.wav" \
  -filter_complex "\
    [0:a]afade=t=in:st=0:d=0.2,afade=t=out:st=4.55:d=0.4,volume=0.26[music];\
    [1:a]volume=0.48,adelay=300|300[t1];[2:a]volume=0.45,adelay=800|800[t2];[3:a]volume=0.48,adelay=1300|1300[t3];\
    [4:a]volume=0.40,adelay=1800|1800[c1];[1:a]volume=0.45,adelay=2300|2300[t4];[2:a]volume=0.45,adelay=2800|2800[t5];\
    [5:a]volume=0.50,adelay=600|600[w1];[6:a]volume=0.60,adelay=3600|3600[pl];[7:a]volume=0.50,adelay=4000|4000[conf];\
    [music][t1][t2][t3][c1][t4][t5][w1][pl][conf]amix=inputs=10:duration=first:dropout_transition=0:normalize=0[mix];\
    [mix]alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11[out]" \
  -map "[out]" -t 5 -ar 48000 -ac 2 -c:a aac -b:a 192k "$OUTA/assemble-loop-final-bed.m4a" </dev/null
ffmpeg -y -i "$VF/04-code-assemble-loop5s-final.mp4" -i "$OUTA/assemble-loop-final-bed.m4a" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart \
  "$VF/04-code-assemble-loop5s-final-scored.mp4" </dev/null

# --- 05 courtyard grow ---
FG="$ROOT/output/videos/frames_courtyard_grow_final"
encode_silent "$FG" "$VF/05-courtyard-grow-final.mp4" 24
DUR2=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VF/05-courtyard-grow-final.mp4")
ffmpeg -y \
  -ss 30 -t "$DUR2" -i "$OUTA/vastness.wav" \
  -i "$OUTA/tick_001.wav" -i "$OUTA/tick_002.wav" -i "$OUTA/tick_004.wav" \
  -i "$OUTA/click_001.wav" \
  -i "$OUTA/arrow-whoosh-1492.wav" -i "$OUTA/cinematic-whoosh-fast-transition-1489.wav" \
  -i "$OUTA/open_002.wav" -i "$OUTA/pluck_001.wav" -i "$OUTA/confirmation_002.wav" \
  -filter_complex "\
    [0:a]afade=t=in:st=0:d=0.3,afade=t=out:st=$(python3 -c "print(max(0,float('$DUR2')-0.45))"):d=0.4,volume=0.26[music];\
    [1:a]volume=0.45,adelay=400|400[t1];[2:a]volume=0.42,adelay=1000|1000[t2];[3:a]volume=0.45,adelay=1600|1600[t3];\
    [4:a]volume=0.40,adelay=2200|2200[c1];[1:a]volume=0.42,adelay=3000|3000[t4];[2:a]volume=0.42,adelay=3800|3800[t5];\
    [3:a]volume=0.42,adelay=4600|4600[t6];[4:a]volume=0.38,adelay=5400|5400[c2];\
    [5:a]volume=0.52,adelay=350|350[w1];[5:a]volume=0.48,adelay=1500|1500[w2];[5:a]volume=0.48,adelay=2700|2700[w3];\
    [6:a]volume=0.38,adelay=3900|3900[w4];[5:a]volume=0.50,adelay=5100|5100[w5];\
    [7:a]volume=0.50,adelay=5800|5800[op];[8:a]volume=0.65,adelay=6200|6200[pl];[9:a]volume=0.55,adelay=6500|6500[conf];\
    [music][t1][t2][t3][c1][t4][t5][t6][c2][w1][w2][w3][w4][w5][op][pl][conf]amix=inputs=17:duration=first:dropout_transition=0:normalize=0[mix];\
    [mix]alimiter=limit=0.95,loudnorm=I=-15:TP=-1.5:LRA=11[out]" \
  -map "[out]" -t "$DUR2" -ar 48000 -ac 2 -c:a aac -b:a 192k "$OUTA/courtyard-grow-final-bed.m4a" </dev/null
ffmpeg -y -i "$VF/05-courtyard-grow-final.mp4" -i "$OUTA/courtyard-grow-final-bed.m4a" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart \
  "$VF/05-courtyard-grow-final-scored.mp4" </dev/null

cp -f "$VF"/*-scored.mp4 "$PREV"/
cp -f "$ROOT/output/images/final"/*.png "$PREV"/ 2>/dev/null || true
echo "=== FINAL SCORED ==="
ls -lah "$VF"/*-scored.mp4 "$PREV"/
