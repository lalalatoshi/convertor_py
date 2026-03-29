"""
rules_to_midi.py
================
Converter 1: Emotional/Musical Properties → MIDI File

Reads a properties dict (from the rules engine) and generates a
2-track MIDI file: melody (Track 0) + chord backing (Track 1).

Property keys (all optional, defaults shown):
    valence     float [-1.0,  1.0]   -1=sad,      +1=happy       default: 0.0
    arousal     float [-1.0,  1.0]   -1=calm,     +1=energetic   default: 0.0
    tempo       int   [40,   200]    BPM                          default: 90
    pitch_root  int   [0,    11]     0=C 2=D 4=E … 11=B          default: 0
    scale       str                  major/minor/pentatonic/blues  default: major
    octave      int   [2,    6]      base octave                  default: 4
    duration    float (seconds)      approx length                default: 10.0
    instrument  int|str|None         GM program or name           default: auto

Usage (CLI):
    python rules_to_midi.py                        # demo run → output/midi/output.mid
    python rules_to_midi.py output/midi/my.mid     # custom path

Usage (import):
    from converters.rules_to_midi.rules_to_midi import convert
    convert(properties, "output/midi/result.mid")
"""

import sys
import os
import random
from midiutil import MIDIFile

# Use relative imports when run as part of the package
try:
    from .scale_definitions import SCALES, build_scale_notes
    from .instrument_map import pick_instrument
except ImportError:
    from scale_definitions import SCALES, build_scale_notes
    from instrument_map import pick_instrument

# ── Helpers ───────────────────────────────────────────────────────────────────

def _clamp(val, lo, hi):
    return max(lo, min(hi, val))

def _velocity_from_arousal(arousal: float) -> int:
    """arousal [-1, 1] → velocity [40, 110]"""
    return int(_clamp(75 + arousal * 35, 40, 110))

def _note_duration_from_valence(valence: float, base_dur: float = 0.5) -> float:
    """
    Positive valence → shorter, lively notes.
    Negative valence → longer, sustained notes.
    Returns duration in beats.
    """
    return round(base_dur * (1.0 - valence * 0.4), 3)

def _add_chord(midi, track, channel, scale_notes, time, duration, velocity):
    """Place a triad (root, 3rd, 5th of scale) at the given beat."""
    chord_indices = [0, 2, 4] if len(scale_notes) > 4 else [0, 1, 2]
    chord_velocity = max(30, velocity - 20)
    for idx in chord_indices:
        if idx < len(scale_notes):
            midi.addNote(track, channel, scale_notes[idx], time, duration, chord_velocity)

# ── Main converter ────────────────────────────────────────────────────────────

def convert(properties: dict, output_path: str = "output/midi/output.mid") -> str:
    """
    Convert a rules-engine properties dict into a MIDI file.

    Parameters
    ----------
    properties  : dict  (see module docstring for keys)
    output_path : str   destination .mid file path

    Returns
    -------
    str : path to the generated MIDI file
    """

    # ── Extract & validate ────────────────────────────────────────────────────
    valence    = _clamp(float(properties.get("valence",    0.0)), -1.0, 1.0)
    arousal    = _clamp(float(properties.get("arousal",    0.0)), -1.0, 1.0)
    tempo      = _clamp(int(properties.get("tempo",        90)),   40,  200)
    pitch_root = _clamp(int(properties.get("pitch_root",   0)),    0,   11)
    scale_name = properties.get("scale", "major")
    octave     = _clamp(int(properties.get("octave",       4)),    2,   6)
    duration_s = float(properties.get("duration",         10.0))
    instrument = properties.get("instrument", None)

    if scale_name not in SCALES:
        print(f"[WARN] Unknown scale '{scale_name}', falling back to 'major'")
        scale_name = "major"

    # ── Derived parameters ────────────────────────────────────────────────────
    beats_per_second = tempo / 60.0
    total_beats      = duration_s * beats_per_second
    note_dur_beats   = _note_duration_from_valence(valence)
    velocity         = _velocity_from_arousal(arousal)
    program          = pick_instrument(valence, arousal, instrument)
    scale_notes      = build_scale_notes(pitch_root, scale_name, octave, num_octaves=2)

    # Higher arousal → notes placed closer together (faster feel)
    gap = max(0.05, 0.25 - arousal * 0.15)

    # ── Build MIDI ────────────────────────────────────────────────────────────
    midi = MIDIFile(2)   # Track 0: melody | Track 1: chords

    midi.addTempo(0, 0, tempo)
    midi.addProgramChange(0, 0, 0, program)

    midi.addTempo(1, 0, tempo)
    bass_program = _clamp(program + 32, 0, 127)
    midi.addProgramChange(1, 1, 0, bass_program)

    # ── Melody (Track 0) ──────────────────────────────────────────────────────
    random.seed(int(valence * 100 + arousal * 100))   # deterministic per emotion
    current_beat = 0.0
    prev_idx = len(scale_notes) // 2

    while current_beat < total_beats:
        max_step = 2 if abs(arousal) < 0.3 else 4
        step = random.randint(-max_step, max_step)
        idx  = _clamp(prev_idx + step, 0, len(scale_notes) - 1)
        note = scale_notes[idx]
        prev_idx = idx

        vel_var     = random.randint(-8, 8)
        actual_vel  = _clamp(velocity + vel_var, 20, 120)
        midi.addNote(0, 0, note, current_beat, note_dur_beats, actual_vel)
        current_beat += note_dur_beats + gap

    # ── Chord backing (Track 1) ───────────────────────────────────────────────
    chord_beat = 0.0
    while chord_beat < total_beats:
        _add_chord(midi, 1, 1, scale_notes, chord_beat, 1.8, velocity)
        chord_beat += 2.0

    # ── Write file ────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "wb") as f:
        midi.writeFile(f)

    notes_count = int(total_beats / (note_dur_beats + gap))
    print(f"[✓] MIDI saved       → {output_path}")
    print(f"    Tempo            = {tempo} BPM")
    print(f"    Scale            = {scale_name} (root={pitch_root})")
    print(f"    Valence/Arousal  = {valence} / {arousal}")
    print(f"    Instrument (GM)  = {program}")
    print(f"    Notes generated  = {notes_count}")
    return output_path


# ── CLI / Demo ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "output/midi/output.mid"

    demo_properties = {
        "valence":    0.7,
        "arousal":    0.6,
        "tempo":      128,
        "pitch_root": 0,
        "scale":      "major",
        "octave":     4,
        "duration":   10,
        "instrument": 0,
    }

    print("=== Converter 1: rules_to_midi ===")
    print(f"Properties : {demo_properties}\n")
    convert(demo_properties, out)
