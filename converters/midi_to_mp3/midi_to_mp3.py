"""
midi_to_mp3.py
==============
Converter 2: MIDI File → MP3

Pipeline:
    MIDI  ──(FluidSynth + .sf2 SoundFont)──►  WAV  ──(pydub + ffmpeg)──►  MP3

Dependencies:
    pip install midi2audio pydub
    Windows : download fluidsynth from https://github.com/FluidSynth/fluidsynth/releases
              download ffmpeg from https://ffmpeg.org/download.html
              add both to system PATH
    Docker  : handled automatically via Dockerfile

Usage (CLI):
    python midi_to_mp3.py input.mid                        # → output/mp3/input.mp3
    python midi_to_mp3.py input.mid output/mp3/out.mp3     # custom output
    python midi_to_mp3.py input.mid output/mp3/out.mp3 192 # custom bitrate (kbps)

Usage (import):
    from converters.midi_to_mp3.midi_to_mp3 import convert
    convert("output/midi/result.mid", "output/mp3/result.mp3", bitrate="192k")
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

try:
    from .soundfont_finder import find_soundfont
except ImportError:
    from soundfont_finder import find_soundfont

# ── Dependency check ──────────────────────────────────────────────────────────

def _require(cmd: str, install_hint: str):
    """Raise a clear error if a CLI tool is missing. Works on Windows & Linux."""
    # Windows uses 'where', Linux/macOS uses 'which'
    checker = "where" if os.name == "nt" else "which"
    result = subprocess.run([checker, cmd], capture_output=True)
    if result.returncode != 0:
        raise EnvironmentError(
            f"Required tool '{cmd}' not found.\n"
            f"Install it:  {install_hint}"
        )

# ── Stage 1: MIDI → WAV ───────────────────────────────────────────────────────

def midi_to_wav(
    midi_path: str,
    wav_path: str,
    soundfont: str = None,
    sample_rate: int = 44100,
    gain: float = 1.0,
) -> str:
    """
    Render a MIDI file to WAV using FluidSynth.

    Parameters
    ----------
    midi_path   : path to input .mid file
    wav_path    : path to output .wav file
    soundfont   : path to .sf2 soundfont (auto-detected if None)
    sample_rate : audio sample rate Hz (default 44100)
    gain        : FluidSynth gain level (default 1.0)

    Returns
    -------
    str : path to generated WAV file
    """
    _require("fluidsynth", "Windows: download from https://github.com/FluidSynth/fluidsynth/releases and add to PATH")
    sf2 = find_soundfont(soundfont)

    cmd = [
        "fluidsynth",
        "-ni",
        "-g",  str(gain),
        "-r",  str(sample_rate),
        "-F",  wav_path,
        sf2,
        midi_path,
    ]

    print(f"[~] Rendering MIDI → WAV...")
    print(f"    MIDI      : {midi_path}")
    print(f"    SoundFont : {sf2}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"FluidSynth error:\n{result.stderr}")
    if not os.path.exists(wav_path):
        raise RuntimeError(f"FluidSynth ran but WAV not found at: {wav_path}")

    size_kb = os.path.getsize(wav_path) / 1024
    print(f"[✓] WAV created ({size_kb:.1f} KB) → {wav_path}")
    return wav_path

# ── Stage 2: WAV → MP3 ────────────────────────────────────────────────────────

def wav_to_mp3(wav_path: str, mp3_path: str, bitrate: str = "192k") -> str:
    """
    Convert a WAV file to MP3 using pydub + ffmpeg.

    Parameters
    ----------
    wav_path : path to input .wav file
    mp3_path : path to output .mp3 file
    bitrate  : MP3 bitrate string e.g. "128k", "192k", "320k"

    Returns
    -------
    str : path to generated MP3 file
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError("pydub not installed. Run:  pip install pydub")

    _require("ffmpeg", "Windows: download from https://ffmpeg.org/download.html and add to PATH")

    os.makedirs(os.path.dirname(mp3_path) if os.path.dirname(mp3_path) else ".", exist_ok=True)

    print(f"[~] Converting WAV → MP3 (bitrate={bitrate})...")
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3", bitrate=bitrate)

    size_kb   = os.path.getsize(mp3_path) / 1024
    duration_s = len(audio) / 1000.0
    print(f"[✓] MP3 created ({size_kb:.1f} KB, {duration_s:.1f}s) → {mp3_path}")
    return mp3_path

# ── Full pipeline ─────────────────────────────────────────────────────────────

def convert(
    midi_path: str,
    output_path: str = None,
    bitrate: str = "192k",
    soundfont: str = None,
    sample_rate: int = 44100,
    keep_wav: bool = False,
) -> str:
    """
    Full pipeline: MIDI → WAV (FluidSynth) → MP3 (pydub).

    Parameters
    ----------
    midi_path   : path to input .mid file
    output_path : path to output .mp3  (default: output/mp3/<midi_name>.mp3)
    bitrate     : MP3 bitrate e.g. "128k", "192k", "320k"
    soundfont   : path to .sf2 file (auto-detected if None)
    sample_rate : WAV sample rate Hz (default 44100)
    keep_wav    : if True, save the intermediate WAV alongside the MP3

    Returns
    -------
    str : path to generated MP3 file
    """
    midi_path = str(midi_path)
    if not os.path.exists(midi_path):
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")

    if output_path is None:
        stem = Path(midi_path).stem
        output_path = os.path.join("output", "mp3", f"{stem}.mp3")

    # Use a proper temp file that works on both Windows and Linux
    tmp_wav = os.path.join(tempfile.gettempdir(), f"emosynth_tmp_{os.getpid()}.wav")

    try:
        wav_path = tmp_wav
        midi_to_wav(
            midi_path,
            wav_path,
            soundfont=soundfont,
            sample_rate=sample_rate,
        )

        wav_to_mp3(tmp_wav, output_path, bitrate=bitrate)

        if keep_wav:
            wav_final = str(Path(output_path).with_suffix(".wav"))
            os.makedirs(os.path.dirname(wav_final) if os.path.dirname(wav_final) else ".", exist_ok=True)
            os.rename(tmp_wav, wav_final)
            print(f"[i] WAV kept → {wav_final}")
        else:
            if os.path.exists(tmp_wav):
                os.remove(tmp_wav)

    except Exception as e:
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)
        raise e

    print(f"\n[✓] Done! MP3 ready → {output_path}")
    return output_path


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python midi_to_mp3.py <input.mid> [output.mp3] [bitrate_kbps]")
        print("Example: python midi_to_mp3.py output/midi/output.mid output/mp3/result.mp3 192")
        sys.exit(1)

    midi_in     = sys.argv[1]
    mp3_out     = sys.argv[2] if len(sys.argv) > 2 else None
    bitrate_val = sys.argv[3] if len(sys.argv) > 3 else "192"

    if not bitrate_val.endswith("k"):
        bitrate_val += "k"

    print("=== Converter 2: midi_to_mp3 ===")
    convert(midi_in, mp3_out, bitrate=bitrate_val)
