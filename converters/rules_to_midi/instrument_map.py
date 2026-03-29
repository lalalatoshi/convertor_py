"""
instrument_map.py
=================
General MIDI (GM) program number mappings.
Used to auto-select instrument based on emotional quadrant (valence/arousal).
"""

# Emotion quadrant → GM program number
EMOTION_INSTRUMENT_MAP = {
    "bright_happy":  0,    # Acoustic Grand Piano
    "calm_happy":    40,   # Violin
    "sad_calm":      70,   # Bassoon
    "energetic":     30,   # Distortion Guitar
}

# Common named instruments for manual override
NAMED_INSTRUMENTS = {
    "piano":        0,
    "bright_piano": 1,
    "harpsichord":  6,
    "guitar":       25,
    "electric_guitar": 27,
    "bass":         32,
    "violin":       40,
    "viola":        41,
    "cello":        42,
    "trumpet":      56,
    "saxophone":    65,
    "flute":        73,
    "clarinet":     71,
    "synth_lead":   80,
    "synth_pad":    88,
    "choir":        52,
}

def pick_instrument(valence: float, arousal: float, override=None) -> int:
    """
    Select a GM instrument program number.

    Parameters
    ----------
    valence  : float [-1.0, 1.0]
    arousal  : float [-1.0, 1.0]
    override : int or str or None
        If int  → used directly as GM program number
        If str  → looked up in NAMED_INSTRUMENTS
        If None → auto-selected from emotion quadrant

    Returns
    -------
    int : GM program number (0–127)
    """
    if override is not None:
        if isinstance(override, str):
            return NAMED_INSTRUMENTS.get(override.lower(), 0)
        return max(0, min(127, int(override)))

    if valence >= 0 and arousal >= 0:
        return EMOTION_INSTRUMENT_MAP["bright_happy"]
    elif valence >= 0 and arousal < 0:
        return EMOTION_INSTRUMENT_MAP["calm_happy"]
    elif valence < 0 and arousal < 0:
        return EMOTION_INSTRUMENT_MAP["sad_calm"]
    else:
        return EMOTION_INSTRUMENT_MAP["energetic"]
