#!/usr/bin/env python3
"""Re-assemble v4 explainer + cutdowns: zoomed replay, xfades, louder bed."""
from __future__ import annotations
import subprocess
from pathlib import Path

ROOT = Path("/workspace/archlang-spectacle")
FR = ROOT / "output/v4/intermediates/frames"
CL = ROOT / "output/v4/intermediates/clips"
VID = ROOT / "output/v4/videos"
AUD = ROOT / "source/audio"
REP = ROOT / "output/v4/intermediates/replay"
CD = CL / "cutdowns"
ST = ROOT / "output/v4/stills"
for p in (CL, VID, CD):
    p.mkdir(parents=True, exist_ok=True)

FADE = 0.45


def run(cmd, tail=8):
    print("+", " ".join(str(c) if not str(c).startswith(" ") else c[:40] for c in cmd[:8]), "...")
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:])
        raise SystemExit(f"ffmpeg failed: {r.returncode}")
    lines = [ln for ln in r.stdout.splitlines() if ln][-tail:]
    for ln in lines:
        print(ln)
    return r


def enc_still(src: Path, dur: float, dest: Path):
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(src), "-t", f"{dur:.3f}",
        "-r", "24", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18",
        "-preset", "veryfast", "-movflags", "+faststart", str(dest),
    ], tail=2)


def xfade_concat(clips: list[Path], durs: list[float], dest: Path, fade: float = FADE):
    assert len(clips) == len(durs)
    n = len(clips)
    args = ["ffmpeg", "-y"]
    for c in clips:
        args += ["-i", str(c)]
    parts = []
    offsets = []
    running = durs[0]
    last = "[0:v]"
    for i in range(1, n):
        off = running - fade
        offsets.append(off)
        out = f"[v{i}]" if i < n - 1 else "[vout]"
        parts.append(f"{last}[{i}:v]xfade=transition=fade:duration={fade}:offset={off:.4f}{out}")
        last = out
        running = running + durs[i] - fade
    fc = ";".join(parts)
    args += ["-filter_complex", fc, "-map", "[vout]", "-r", "24",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
             str(dest)]
    run(args, tail=4)
    print(f"  xfade duration expected {running:.3f}s  offsets {[round(o,2) for o in offsets]}")
    return running, [0.0] + offsets  # chapter start = when incoming clip begins to fade in


def chapter_starts(durs, fade=FADE):
    starts = [0.0]
    running = durs[0]
    for d in durs[1:]:
        starts.append(running - fade)
        running = running + d - fade
    return starts, running


def mix_audio(silent: Path, dest: Path, duration: float, starts: dict, music_ss: float = 3.0):
    """Mix music + the SFX hits that `starts` actually requests."""
    mus = AUD / "music/valley-sunset-alejandro-magana-mixkit-127.mp3"
    files = {
        "who": AUD / "sfx/mixkit/cinematic-whoosh-fast-transition-1489.mp3",
        "arr": AUD / "sfx/mixkit/arrow-whoosh-1492.mp3",
        "gho": AUD / "sfx/mixkit/ghostly-whoosh-passing-1485.mp3",
        "clk": AUD / "sfx/kenney/click_002.ogg",
        "tik": AUD / "sfx/kenney/tick_002.ogg",
        "cnf": AUD / "sfx/kenney/confirmation_002.ogg",
        "opn": AUD / "sfx/kenney/open_002.ogg",
        "plk": AUD / "sfx/kenney/pluck_002.ogg",
    }
    # (file_key, vol, time) events actually used
    events = []
    ev = starts
    if "hook" in ev:
        events.append(("who", 0.38, ev["hook"] + 0.25))
    if "type" in ev:
        base = ev["type"] + 0.35
        for i in range(6):
            events.append(("clk", 0.30, base + i * 1.35))
    if "compile" in ev:
        events.append(("arr", 0.34, ev["compile"] + 0.05))
        events.append(("opn", 0.34, ev["compile"] + 0.35))
    if "themes" in ev:
        events.append(("gho", 0.36, ev["themes"] + 0.05))
        events.append(("plk", 0.32, ev["themes"] + 0.30))
    if "describe" in ev:
        events.append(("tik", 0.38, ev["describe"] + 0.08))
    if "lint" in ev:
        events.append(("tik", 0.40, ev["lint"] + 0.08))
    if "fix" in ev:
        events.append(("cnf", 0.46, ev["fix"] + 0.08))
    if "param" in ev:
        events.append(("tik", 0.34, ev["param"] + 0.08))
        events.append(("tik", 0.34, ev["param"] + 2.05))
        events.append(("tik", 0.34, ev["param"] + 4.05))
    if "rise" in ev:
        events.append(("who", 0.38, ev["rise"] + 0.08))
    if "export" in ev:
        events.append(("arr", 0.34, ev["export"] + 0.08))
    if "mcp" in ev:
        events.append(("gho", 0.34, ev["mcp"] + 0.08))
    if "end" in ev:
        events.append(("cnf", 0.50, ev["end"] + 0.12))

    used_keys = []
    for k, _, _ in events:
        if k not in used_keys:
            used_keys.append(k)

    fade_out_start = max(0.0, duration - 2.6)
    cmd = ["ffmpeg", "-y", "-i", str(silent), "-ss", str(music_ss), "-i", str(mus)]
    key_to_idx = {}
    for i, k in enumerate(used_keys):
        cmd += ["-i", str(files[k])]
        key_to_idx[k] = i + 2  # 0=video, 1=music

    filt = [
        f"[1:a]volume=0.62,afade=t=in:st=0:d=1.1,afade=t=out:st={fade_out_start:.3f}:d=2.5,"
        f"atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,"
        f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[mus]"
    ]
    mix_ins = ["[mus]"]
    # group events by file so we asplit the right number of times
    from collections import defaultdict
    grouped = defaultdict(list)
    for k, vol, tm in events:
        grouped[k].append((vol, tm))
    node_i = 0
    for k, hits in grouped.items():
        idx = key_to_idx[k]
        n = len(hits)
        src = f"[{idx}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
        if n == 1:
            labels = [f"s{k}0"]
            filt.append(f"{src}[{labels[0]}]")
        else:
            labels = [f"s{k}{i}" for i in range(n)]
            filt.append(f"{src},asplit={n}" + "".join(f"[{lab}]" for lab in labels))
        for lab, (vol, tm) in zip(labels, hits):
            ms = max(0, int(tm * 1000))
            out = f"n{node_i}"
            filt.append(f"[{lab}]volume={vol},adelay={ms}|{ms}[{out}]")
            mix_ins.append(f"[{out}]")
            node_i += 1
    filt.append("".join(mix_ins) + f"amix=inputs={len(mix_ins)}:duration=first:dropout_transition=0:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
    cmd += ["-filter_complex", ";".join(filt),
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest", "-movflags", "+faststart", str(dest)]
    run(cmd, tail=5)



def probe(path: Path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)
    ], text=True).strip()
    print(f"  {path.name} duration={out}")
    return float(out)


def main():
    print("=== encode slides ===")
    enc_still(FR / "00_hook.png", 6.0, CL / "00_hook.mp4")
    run([
        "ffmpeg", "-y", "-framerate", "2.8235", "-i", str(FR / "typing/t%02d.png"),
        "-r", "24", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18",
        "-preset", "veryfast", str(CL / "01_type.mp4"),
    ], tail=2)
    enc_still(FR / "02_compile.png", 7.0, CL / "02_compile.mp4")
    enc_still(FR / "03_themes.png", 7.0, CL / "03_themes.mp4")
    enc_still(FR / "04_describe.png", 6.5, CL / "04_describe.mp4")
    enc_still(FR / "05_lint.png", 7.0, CL / "05_lint.mp4")
    enc_still(FR / "06_fix.png", 6.0, CL / "06_fix.mp4")
    for n, letter in [(2, "a"), (3, "b"), (4, "c"), (5, "d")]:
        enc_still(FR / f"07_param_{n}.png", 2.0, CL / f"07{letter}.mp4")
    enc_still(FR / "09_export.png", 6.5, CL / "09_export.mp4")
    enc_still(FR / "10_mcp.png", 6.0, CL / "10_mcp.mp4")
    enc_still(FR / "11_end.png", 6.0, CL / "11_end.mp4")

    print("=== zoomed courtyard replay + overlay ===")
    zoomed = CL / "08_replay_zoom.mp4"
    run([
        "ffmpeg", "-y", "-i", str(REP / "courtyard-light-1080.mp4"),
        "-i", str(FR / "08_overlay.png"),
        "-filter_complex",
        "[0:v]crop=1270:924:320:70,scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0xf5f2ea[z];"
        "[z][1:v]overlay=0:0,format=yuv420p[v]",
        "-map", "[v]", "-r", "24", "-c:v", "libx264", "-crf", "18",
        "-preset", "veryfast", "-an", str(zoomed),
    ], tail=3)
    # copy as 08_3d
    dest3d = CL / "08_3d.mp4"
    run(["ffmpeg", "-y", "-i", str(zoomed), "-t", "12", "-c", "copy", str(dest3d)], tail=2)

    explainer_clips = [
        CL / "00_hook.mp4", CL / "01_type.mp4", CL / "02_compile.mp4", CL / "03_themes.mp4",
        CL / "04_describe.mp4", CL / "05_lint.mp4", CL / "06_fix.mp4",
        CL / "07a.mp4", CL / "07b.mp4", CL / "07c.mp4", CL / "07d.mp4",
        CL / "08_3d.mp4", CL / "09_export.mp4", CL / "10_mcp.mp4", CL / "11_end.mp4",
    ]
    explainer_durs = [6.0, 8.5, 7.0, 7.0, 6.5, 7.0, 6.0, 2.0, 2.0, 2.0, 2.0, 12.0, 6.5, 6.0, 6.0]
    print("=== explainer xfade ===")
    silent = CL / "explainer_xfade_silent.mp4"
    xfade_concat(explainer_clips, explainer_durs, silent)
    starts, total = chapter_starts(explainer_durs)
    names = ["hook", "type", "compile", "themes", "describe", "lint", "fix",
             "param", "p3", "p4", "p5", "rise", "export", "mcp", "end"]
    ev = {n: s for n, s in zip(names, starts)}
    print("chapter starts", {k: round(v, 2) for k, v in ev.items()}, "total", round(total, 2))
    Path(CL / "chapter_starts.txt").write_text(
        "\n".join(f"{n}\t{s:.3f}" for n, s in zip(names, starts)) + f"\ntotal\t{total:.3f}\n"
    )

    print("=== score explainer ===")
    mix_audio(silent, VID / "01-explainer-1080.mp4", total, ev, music_ss=3.0)

    # --- wow cutdown ---
    print("=== wow cutdown ===")
    wow_clips = [CL / "00_hook.mp4", CL / "02_compile.mp4", dest3d, CL / "11_end.mp4"]
    # trim hook/compile/end via re-encode shorter? use existing full hook 6s, compile 7s, 3d 12s, end 6s
    # match previous selection: hook 5.5, compile 6.5, 3d 11.5, end 5
    run(["ffmpeg", "-y", "-i", str(CL / "00_hook.mp4"), "-t", "5.5", "-c", "copy", str(CD / "wow_hook.mp4")], 1)
    run(["ffmpeg", "-y", "-i", str(CL / "02_compile.mp4"), "-t", "6.5", "-c", "copy", str(CD / "wow_compile.mp4")], 1)
    run(["ffmpeg", "-y", "-i", str(dest3d), "-t", "11.5", "-c", "copy", str(CD / "wow_3d.mp4")], 1)
    run(["ffmpeg", "-y", "-ss", "1.0", "-i", str(CL / "11_end.mp4"), "-t", "5.0", "-c", "copy", str(CD / "wow_end.mp4")], 1)
    wow_d = [5.5, 6.5, 11.5, 5.0]
    wow_silent = CD / "wow_xfade_silent.mp4"
    xfade_concat([CD / "wow_hook.mp4", CD / "wow_compile.mp4", CD / "wow_3d.mp4", CD / "wow_end.mp4"], wow_d, wow_silent)
    ws, wt = chapter_starts(wow_d)
    mix_audio(wow_silent, VID / "02-wow-cutdown-1080.mp4", wt, {
        "hook": ws[0], "compile": ws[1], "rise": ws[2], "end": ws[3],
    }, music_ss=5.0)

    # --- agent cutdown ---
    print("=== agent cutdown ===")
    run(["ffmpeg", "-y", "-i", str(CL / "04_describe.mp4"), "-t", "6.0", "-c", "copy", str(CD / "ag_describe.mp4")], 1)
    run(["ffmpeg", "-y", "-i", str(CL / "05_lint.mp4"), "-t", "6.5", "-c", "copy", str(CD / "ag_lint.mp4")], 1)
    run(["ffmpeg", "-y", "-i", str(CL / "06_fix.mp4"), "-t", "6.0", "-c", "copy", str(CD / "ag_fix.mp4")], 1)
    run(["ffmpeg", "-y", "-i", str(CL / "10_mcp.mp4"), "-t", "5.5", "-c", "copy", str(CD / "ag_mcp.mp4")], 1)
    run(["ffmpeg", "-y", "-ss", "3.0", "-i", str(CL / "11_end.mp4"), "-t", "3.0", "-c", "copy", str(CD / "ag_end.mp4")], 1)
    ag_d = [6.0, 6.5, 6.0, 5.5, 3.0]
    ag_silent = CD / "agent_xfade_silent.mp4"
    xfade_concat([CD / "ag_describe.mp4", CD / "ag_lint.mp4", CD / "ag_fix.mp4", CD / "ag_mcp.mp4", CD / "ag_end.mp4"], ag_d, ag_silent)
    as_, at = chapter_starts(ag_d)
    mix_audio(ag_silent, VID / "03-agent-cutdown-1080.mp4", at, {
        "describe": as_[0], "lint": as_[1], "fix": as_[2], "mcp": as_[3], "end": as_[4],
    }, music_ss=24.0)

    # --- vertical ---
    print("=== vertical 9:16 ===")
    enc_still(ST / "02-courtyard-plan-3d-9x16.png", 5.5, CD / "v_hook.mp4")
    enc_still(ST / "01-code-plan-3d-9x16.png", 6.5, CD / "v_code.mp4")
    enc_still(FR / "11_end_9x16.png", 4.0, CD / "v_end.mp4")
    # zoomed 9:16 replay: model fills width
    run([
        "ffmpeg", "-y", "-ss", "1.2", "-i", str(REP / "courtyard-light-1080.mp4"),
        "-i", str(FR / "08_overlay_9x16.png"), "-t", "8.0",
        "-filter_complex",
        "[0:v]crop=1270:924:320:70,scale=1080:786,pad=1080:1920:0:420:color=0xf5f2ea[z];"
        "[z][1:v]overlay=0:0,format=yuv420p[v]",
        "-map", "[v]", "-r", "24", "-c:v", "libx264", "-crf", "18",
        "-preset", "veryfast", "-an", str(CD / "v_3d.mp4"),
    ], tail=3)
    vert_d = [5.5, 6.5, 8.0, 4.0]
    vert_silent = CD / "vert_xfade_silent.mp4"
    xfade_concat([CD / "v_hook.mp4", CD / "v_code.mp4", CD / "v_3d.mp4", CD / "v_end.mp4"], vert_d, vert_silent)
    vs, vt = chapter_starts(vert_d)
    mix_audio(vert_silent, VID / "04-vertical-9x16.mp4", vt, {
        "hook": vs[0], "compile": vs[1], "rise": vs[2], "end": vs[3],
    }, music_ss=12.0)

    print("=== done ===")
    for f in sorted(VID.glob("*.mp4")):
        probe(f)


if __name__ == "__main__":
    main()
