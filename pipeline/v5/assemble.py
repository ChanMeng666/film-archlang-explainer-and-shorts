#!/usr/bin/env python3
"""Encode v5 explainer from the frame sequence, mix audio, render cutdowns."""
from __future__ import annotations

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, "/workspace/archlang-spectacle/pipeline/v5")
sys.path.insert(0, "/workspace/archlang-spectacle/pipeline/v4")

from engine import (
    CHAPTERS_META, FPS, INT5, OUT, chapter_starts, draw_progress, draw_header,
    draw_lower_third, draw_chapter_burst,
)
from scenes import SCENES

ROOT = Path("/workspace/archlang-spectacle")
SEQ = INT5 / "seq"
VID = OUT / "videos"
CL = INT5 / "clips"
AUD = ROOT / "source/audio"
VID.mkdir(parents=True, exist_ok=True)
CL.mkdir(parents=True, exist_ok=True)

META_BY_KEY = {m[0]: m for m in CHAPTERS_META}


def run(cmd, tail=8):
    print("+", " ".join(str(c) for c in cmd[:10]), "...")
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if r.returncode != 0:
        print(r.stdout[-4000:])
        raise SystemExit(f"ffmpeg failed: {r.returncode}")
    lines = [ln for ln in r.stdout.splitlines() if ln][-tail:]
    for ln in lines:
        print(ln)
    return r


def probe(path: Path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path),
    ], text=True).strip()
    print(f"  {path.name} duration={out}")
    return float(out)


def measure_lufs(path: Path):
    r = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    integ = None
    for ln in r.stdout.splitlines():
        if "I:" in ln and "LUFS" in ln:
            print(" ", ln.strip())
            try:
                integ = float(ln.split("I:")[1].split("LUFS")[0].strip())
            except Exception:
                pass
    return integ


def encode_seq(seq_dir: Path, dest: Path, fps=FPS):
    run([
        "ffmpeg", "-y", "-framerate", str(fps), "-i", str(seq_dir / "%05d.png"),
        "-r", str(fps), "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "18",
        "-preset", "veryfast", "-movflags", "+faststart", "-an", str(dest),
    ], tail=4)


def mix_audio(silent: Path, dest: Path, duration: float, starts: dict, music_ss: float = 3.0):
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
    ev = starts
    events = []
    if "hook" in ev:
        events.append(("who", 0.38, ev["hook"] + 0.20))
    if "write" in ev or "type" in ev:
        base = ev.get("write", ev.get("type")) + 1.15
        for i in range(7):
            events.append(("clk", 0.26, base + i * 1.05))
    if "compile" in ev:
        events.append(("arr", 0.34, ev["compile"] + 0.08))
        events.append(("opn", 0.34, ev["compile"] + 0.40))
        for off in (1.20, 2.40, 3.50, 4.50):
            events.append(("plk", 0.36, ev["compile"] + off))
    if "themes" in ev:
        events.append(("gho", 0.36, ev["themes"] + 0.08))
        events.append(("plk", 0.32, ev["themes"] + 1.55))
    if "describe" in ev:
        events.append(("tik", 0.34, ev["describe"] + 0.12))
        for off in (1.15, 1.85, 2.55, 3.25):
            events.append(("tik", 0.32, ev["describe"] + off))
    if "lint" in ev:
        events.append(("tik", 0.40, ev["lint"] + 0.10))
        events.append(("plk", 0.34, ev["lint"] + 1.30))
    if "fix" in ev:
        events.append(("who", 0.30, ev["fix"] + 1.20))
        events.append(("cnf", 0.46, ev["fix"] + 3.30))
    if "param" in ev:
        events.append(("tik", 0.32, ev["param"] + 0.10))
        for off in (1.55, 3.35, 5.15, 6.90):
            events.append(("tik", 0.30, ev["param"] + off))
    if "rise" in ev:
        events.append(("who", 0.38, ev["rise"] + 0.10))
        events.append(("gho", 0.28, ev["rise"] + 4.20))
    if "export" in ev:
        events.append(("arr", 0.34, ev["export"] + 0.12))
        events.append(("opn", 0.32, ev["export"] + 0.85))
    if "mcp" in ev:
        events.append(("gho", 0.32, ev["mcp"] + 0.10))
        for i, off in enumerate((2.00, 2.35, 2.70, 3.05)):
            events.append(("clk", 0.30, ev["mcp"] + off))
        events.append(("opn", 0.36, ev["mcp"] + 3.60))
    if "end" in ev:
        events.append(("cnf", 0.50, ev["end"] + 0.12))

    # drop events past duration
    events = [(k, v, t) for k, v, t in events if 0 <= t < duration - 0.05]

    used_keys = []
    for k, _, _ in events:
        if k not in used_keys:
            used_keys.append(k)

    fade_out_start = max(0.0, duration - 2.6)
    cmd = ["ffmpeg", "-y", "-i", str(silent), "-ss", str(music_ss), "-i", str(mus)]
    key_to_idx = {}
    for i, k in enumerate(used_keys):
        cmd += ["-i", str(files[k])]
        key_to_idx[k] = i + 2

    filt = [
        f"[1:a]volume=0.62,afade=t=in:st=0:d=1.1,afade=t=out:st={fade_out_start:.3f}:d=2.5,"
        f"atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,"
        f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[mus]"
    ]
    mix_ins = ["[mus]"]
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
    filt.append(
        "".join(mix_ins)
        + f"amix=inputs={len(mix_ins)}:duration=first:dropout_transition=0:normalize=0,"
        f"loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
    )
    cmd += [
        "-filter_complex", ";".join(filt),
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-shortest", "-movflags", "+faststart", str(dest),
    ]
    run(cmd, tail=5)


def render_playlist(name: str, playlist: list, w: int, h: int):
    """Render a cutdown with its own sequential chapter chrome."""
    from PIL import Image as Im

    dest_dir = INT5 / f"seq_{name}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    total = sum(p[1] for p in playlist)
    n = int(round(total * FPS))
    print(f"rendering {name}: {n} frames ({total:.2f}s) {w}x{h}")

    def which(t):
        acc = 0.0
        for i, m in enumerate(playlist):
            d = m[1]
            if t < acc + d - 1e-6 or i == len(playlist) - 1:
                return i, t - acc, d
            acc += d
        return len(playlist) - 1, 0.0, playlist[-1][1]

    for i in range(n):
        t = i / FPS
        idx, local, dur = which(t)
        key = playlist[idx][0]
        img = SCENES[key](local, dur, w, h)
        draw_progress(img, t, total, img.size[0], img.size[1])
        draw_header(img, idx, len(playlist), playlist[idx][2], img.size[0])
        draw_lower_third(img, idx + 1, playlist[idx][3], playlist[idx][4],
                         local, img.size[0], img.size[1])
        if h <= w:
            draw_chapter_burst(img, idx + 1, playlist[idx][3], local,
                               img.size[0], img.size[1])
        rgb = Im.new("RGB", img.size, (245, 242, 234))
        rgb.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        rgb.save(dest_dir / f"{i:05d}.png")
        if i % 48 == 0:
            print(f"  {name} {i}/{n} t={t:.2f}")
            sys.stdout.flush()
    print(f"done {name} {n}")
    return dest_dir, total


def playlist_from_keys(items):
    """items: list of (key, duration). Titles come from CHAPTERS_META."""
    out = []
    for key, dur in items:
        m = META_BY_KEY[key]
        out.append((key, dur, m[2], m[3], m[4]))
    return out


def encode_and_score(seq_dir: Path, dest: Path, duration: float, starts: dict, music_ss=3.0):
    silent = CL / (dest.stem + "_silent.mp4")
    encode_seq(seq_dir, silent)
    mix_audio(silent, dest, duration, starts, music_ss=music_ss)
    d = probe(dest)
    lufs = measure_lufs(dest)
    return d, lufs


def explainer_starts():
    starts, total = chapter_starts()
    ev = {CHAPTERS_META[i][0]: starts[i] for i in range(len(CHAPTERS_META))}
    ev["type"] = ev["write"]
    return ev, total


def main():
    ev, total = explainer_starts()
    print("=== encode + score explainer ===")
    n_frames = len(list(SEQ.glob("*.png")))
    print(f"seq frames: {n_frames} expected {int(round(total * FPS))}")
    if n_frames < int(round(total * FPS)) - 2:
        raise SystemExit(f"incomplete sequence: {n_frames}")
    d, lufs = encode_and_score(SEQ, VID / "01-explainer-1080.mp4", total, ev, music_ss=3.0)
    print(f"explainer {d:.2f}s  LUFS={lufs}")

    print("=== wow cutdown ===")
    wow = playlist_from_keys([
        ("hook", 6.0), ("compile", 7.0), ("rise", 10.0), ("end", 4.0),
    ])
    wow_dir, wow_total = render_playlist("wow", wow, 1920, 1080)
    wow_ev = {}
    acc = 0.0
    for key, dur in [("hook", 6.0), ("compile", 7.0), ("rise", 10.0), ("end", 4.0)]:
        wow_ev[key] = acc
        acc += dur
    d, lufs = encode_and_score(wow_dir, VID / "02-wow-cutdown-1080.mp4", wow_total, wow_ev, music_ss=3.0)
    print(f"wow {d:.2f}s  LUFS={lufs}")

    print("=== agent cutdown ===")
    agent = playlist_from_keys([
        ("describe", 6.5), ("lint", 6.5), ("fix", 5.5), ("mcp", 6.5), ("end", 3.5),
    ])
    agent_dir, agent_total = render_playlist("agent", agent, 1920, 1080)
    agent_ev = {}
    acc = 0.0
    for key, dur in [("describe", 6.5), ("lint", 6.5), ("fix", 5.5), ("mcp", 6.5), ("end", 3.5)]:
        agent_ev[key] = acc
        acc += dur
    d, lufs = encode_and_score(agent_dir, VID / "03-agent-cutdown-1080.mp4",
                               agent_total, agent_ev, music_ss=12.0)
    print(f"agent {d:.2f}s  LUFS={lufs}")

    print("=== vertical 9:16 cutdown ===")
    vert = playlist_from_keys([
        ("hook", 6.0), ("compile", 7.0), ("rise", 8.0), ("end", 4.0),
    ])
    vert_dir, vert_total = render_playlist("vert", vert, 1080, 1920)
    vert_ev = {}
    acc = 0.0
    for key, dur in [("hook", 6.0), ("compile", 7.0), ("rise", 8.0), ("end", 4.0)]:
        vert_ev[key] = acc
        acc += dur
    d, lufs = encode_and_score(vert_dir, VID / "04-vertical-9x16.mp4",
                               vert_total, vert_ev, music_ss=3.0)
    print(f"vertical {d:.2f}s  LUFS={lufs}")
    print("ALL DONE")


if __name__ == "__main__":
    main()
