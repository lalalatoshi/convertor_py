"""
scale_definitions.py
====================
Scale interval definitions and note-building utilities.
"""

# Intervals from root note (semitones)
SCALES = {
    "major":      [0, 2, 4, 5, 7, 9, 11],
    "minor":      [0, 2, 3, 5, 7, 8, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "blues":      [0, 3, 5, 6, 7, 10],
    "dorian":     [0, 2, 3, 5, 7, 9, 10],
    "phrygian":   [0, 1, 3, 5, 7, 8, 10],
}

def build_scale_notes(root: int, scale_name: str, octave: int, num_octaves: int = 2) -> list:
    """
    Build a list of MIDI note numbers for a given scale.

    Parameters
    ----------
    root       : int  root note 0=C, 1=C#, 2=D, ... 11=B
    scale_name : str  key from SCALES dict
    octave     : int  base octave (4 = middle C octave)
    num_octaves: int  how many octaves to span

    Returns
    -------
    list of int MIDI note numbers (0–127)
    """
    intervals = SCALES.get(scale_name, SCALES["major"])
    notes = []
    for oct_offset in range(num_octaves):
        for interval in intervals:
            midi_note = (octave + oct_offset) * 12 + root + interval
            if 0 <= midi_note <= 127:
                notes.append(midi_note)
    return notes
