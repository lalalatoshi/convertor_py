"""
tests/test_rules_to_midi.py
============================
Unit tests for Converter 1: rules_to_midi
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from converters.rules_to_midi.rules_to_midi import convert
from converters.rules_to_midi.scale_definitions import build_scale_notes, SCALES
from converters.rules_to_midi.instrument_map import pick_instrument


class TestScaleDefinitions(unittest.TestCase):

    def test_major_scale_length(self):
        notes = build_scale_notes(0, "major", 4, num_octaves=1)
        self.assertEqual(len(notes), 7)

    def test_pentatonic_scale_length(self):
        notes = build_scale_notes(0, "pentatonic", 4, num_octaves=1)
        self.assertEqual(len(notes), 5)

    def test_notes_within_midi_range(self):
        notes = build_scale_notes(0, "major", 4, num_octaves=2)
        for n in notes:
            self.assertGreaterEqual(n, 0)
            self.assertLessEqual(n, 127)

    def test_unknown_scale_fallback(self):
        # SCALES does not have "unknown" — should not raise
        notes = build_scale_notes(0, "unknown", 4)
        self.assertIsInstance(notes, list)


class TestInstrumentMap(unittest.TestCase):

    def test_auto_happy_energetic(self):
        prog = pick_instrument(0.5, 0.5)
        self.assertEqual(prog, 0)  # Acoustic Grand Piano

    def test_auto_sad_calm(self):
        prog = pick_instrument(-0.5, -0.5)
        self.assertEqual(prog, 70)

    def test_int_override(self):
        prog = pick_instrument(0.0, 0.0, override=40)
        self.assertEqual(prog, 40)

    def test_str_override(self):
        prog = pick_instrument(0.0, 0.0, override="violin")
        self.assertEqual(prog, 40)

    def test_clamp_override(self):
        prog = pick_instrument(0.0, 0.0, override=200)
        self.assertEqual(prog, 127)


class TestRulesToMidi(unittest.TestCase):

    OUTPUT = "output/midi/test_output.mid"

    def _props(self, **kwargs):
        base = {"valence": 0.5, "arousal": 0.3, "tempo": 100,
                "pitch_root": 0, "scale": "major", "octave": 4,
                "duration": 3, "instrument": 0}
        base.update(kwargs)
        return base

    def test_file_created(self):
        path = convert(self._props(), self.OUTPUT)
        self.assertTrue(os.path.exists(path))

    def test_file_nonzero(self):
        convert(self._props(), self.OUTPUT)
        self.assertGreater(os.path.getsize(self.OUTPUT), 100)

    def test_minor_scale(self):
        path = convert(self._props(scale="minor"), self.OUTPUT)
        self.assertTrue(os.path.exists(path))

    def test_extreme_valence_positive(self):
        path = convert(self._props(valence=1.0), self.OUTPUT)
        self.assertTrue(os.path.exists(path))

    def test_extreme_valence_negative(self):
        path = convert(self._props(valence=-1.0), self.OUTPUT)
        self.assertTrue(os.path.exists(path))

    def test_returns_path_string(self):
        result = convert(self._props(), self.OUTPUT)
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main(verbosity=2)
