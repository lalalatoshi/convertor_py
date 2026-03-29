"""
soundfont_finder.py
===================
Locates an available .sf2 SoundFont file on the system.
Works on Windows, Linux, and macOS.
Used by midi_to_mp3.py for FluidSynth rendering.
"""

import os
import sys

def _sf2_search_paths() -> list:
    """Build SF2 search path list based on current OS."""
    paths = []

    # Windows paths
    if sys.platform == "win32":
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        local_app     = os.environ.get("LOCALAPPDATA", "")
        paths += [
            os.path.join(program_files, "FluidSynth", "soundfonts", "FluidR3_GM.sf2"),
            os.path.join(program_files, "VirtualMIDISynth", "soundfonts", "FluidR3_GM.sf2"),
            os.path.join(local_app, "FluidSynth", "FluidR3_GM.sf2"),
            "C:\\soundfonts\\FluidR3_GM.sf2",
            os.path.expanduser("~\\soundfonts\\FluidR3_GM.sf2"),
            os.path.expanduser("~\\Downloads\\FluidR3_GM.sf2"),
        ]

    # Linux paths
    paths += [
        "/usr/share/sounds/sf2/FluidR3_GM.sf2",
        "/usr/share/sounds/sf2/TimGM6mb.sf2",
        "/usr/share/sounds/sf2/default-GM.sf2",
        "/etc/alternatives/default-GM.sf2",
        "/usr/share/soundfonts/FluidR3_GM.sf2",
    ]

    # macOS (Homebrew) paths
    paths += [
        "/opt/homebrew/share/sounds/sf2/FluidR3_GM.sf2",
        "/usr/local/share/soundfonts/FluidR3_GM.sf2",
    ]

    # Project-local soundfonts/ folder (works on all OS) — HIGHEST PRIORITY for portability
    project_sf2 = os.path.join(
        os.path.dirname(__file__), "..", "..", "soundfonts", "FluidR3_GM.sf2"
    )
    paths.insert(0, project_sf2)  # check this first

    return paths


def find_soundfont(override: str = None) -> str:
    """
    Find an available .sf2 SoundFont file.

    Parameters
    ----------
    override : str or None
        If provided and the path exists, it is returned immediately.

    Returns
    -------
    str : absolute path to a valid .sf2 file

    Raises
    ------
    FileNotFoundError if no soundfont is found anywhere
    """
    if override and os.path.exists(override):
        return os.path.abspath(override)

    for path in _sf2_search_paths():
        resolved = os.path.abspath(path)
        if os.path.exists(resolved):
            return resolved

    raise FileNotFoundError(
        "No SoundFont (.sf2) file found on this system.\n\n"
        "Windows: Download FluidR3_GM.sf2 from:\n"
        "  https://member.keymusician.com/Member/FluidR3_GM/index.html\n"
        "Then place it in:\n"
        "  emosynth/soundfonts/FluidR3_GM.sf2   <- recommended\n"
        "  C:\\soundfonts\\FluidR3_GM.sf2\n\n"
        "Or pass the path directly:\n"
        "  convert(midi_path, soundfont='C:/path/to/FluidR3_GM.sf2')"
    )
