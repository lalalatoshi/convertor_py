"""
tests/test_midi_to_mp3.py
==========================
Unit tests for Converter 2: midi_to_mp3
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from converters.rules_to_midi.rules_to_midi import convert as make_midi
from converters.midi_to_mp3.midi_to_mp3 import convert, midi_to_wav, wav_to_mp3
from converters.midi_to_mp3.soundfont_finder import find_soundfont


MIDI_FIXTURE = "output/midi/test_fixture.mid"
WAV_OUT      = "output/mp3/test_out.wav"
MP3_OUT      = "output/mp3/test_out.mp3"


def setUpModule():
    """Create a test MIDI file once before all tests."""
    make_midi({"valence": 0.0, "arousal": 0.0, "tempo": 90,
               "scale": "major", "duration": 3}, MIDI_FIXTURE)


class TestSoundFontFinder(unittest.TestCase):

    def test_finds_sf2(self):
        path = find_soundfont()
        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith(".sf2"))

    def test_override_nonexistent_falls_through(self):
        # Should still find system SF2 even if override doesn't exist
        path = find_soundfont(override="/nonexistent/path.sf2")
        self.assertTrue(os.path.exists(path))


class TestMidiToWav(unittest.TestCase):

    def test_wav_created(self):
        midi_to_wav(MIDI_FIXTURE, WAV_OUT)
        self.assertTrue(os.path.exists(WAV_OUT))

    def test_wav_nonzero(self):
        midi_to_wav(MIDI_FIXTURE, WAV_OUT)
        self.assertGreater(os.path.getsize(WAV_OUT), 1000)

    def tearDown(self):
        if os.path.exists(WAV_OUT):
            os.remove(WAV_OUT)


class TestMidiToMp3(unittest.TestCase):

    def test_mp3_created(self):
        path = convert(MIDI_FIXTURE, MP3_OUT)
        self.assertTrue(os.path.exists(path))

    def test_mp3_nonzero(self):
        convert(MIDI_FIXTURE, MP3_OUT)
        self.assertGreater(os.path.getsize(MP3_OUT), 1000)

    def test_returns_path_string(self):
        result = convert(MIDI_FIXTURE, MP3_OUT)
        self.assertIsInstance(result, str)

    def test_missing_midi_raises(self):
        with self.assertRaises(FileNotFoundError):
            convert("nonexistent.mid", MP3_OUT)

    def tearDown(self):
        if os.path.exists(MP3_OUT):
            os.remove(MP3_OUT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
