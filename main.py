import sys
import json
import os
from pathlib import Path

from converters.rules_to_midi.rules_to_midi import convert as to_midi
from converters.midi_to_mp3.midi_to_mp3 import convert as to_mp3


def run_pipeline(properties: dict, midi_out: str = None, mp3_out: str = None) -> str:

    # ✅ Ensure folders exist
    os.makedirs("output/midi", exist_ok=True)
    os.makedirs("output/mp3", exist_ok=True)

    # Auto filename
    tag = f"v{properties.get('valence', 0)}_a{properties.get('arousal', 0)}"

    # MIDI path
    if midi_out is None:
        midi_out = f"output/midi/{tag}.mid"

    # MP3 path (clean + safe)
    if mp3_out is None:
        name = Path(midi_out).stem
        mp3_out = f"output/mp3/{name}.mp3"

    print("=" * 45)
    print("  EmoSynth Pipeline")
    print("=" * 45)
    print(f"  Properties : {properties}")
    print()

    # Step 1: properties → MIDI
    midi_path = to_midi(properties, midi_out)
    print()

    # Step 2: MIDI → MP3
    mp3_path = to_mp3(midi_path, mp3_out)
    print()

    print("=" * 45)
    print(f"  Final output : {mp3_path}")
    print("=" * 45)

    return mp3_path


# CLI / Demo
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
        with open(sys.argv[1]) as f:
            props = json.load(f)
        print(f"Loaded properties from {sys.argv[1]}")
    else:
        props = {
            "valence":    0.7,
            "arousal":    0.6,
            "tempo":      128,
            "pitch_root": 0,
            "scale":      "major",
            "octave":     4,
            "duration":   10,
            "instrument": 0,
        }

    run_pipeline(props)