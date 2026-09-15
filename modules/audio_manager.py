"""Audiomanager"""
from pathlib import Path
import pygame
from mutagen import File, MutagenError


class AudioManager:
    """class of audiomanager"""
    def __init__(self) -> None:
        """Initialization class"""
        pygame.mixer.init()

    def get_duration(self, path: Path) -> float:
        """return duration of composition"""
        try:
            audio = File(str(path))

            if audio is not None and audio.info is not None:
                return audio.info.length

        except (MutagenError, OSError):
            pass

        return 0.0

    def is_supported(self, path: Path) -> bool:
        """check support file"""
        try:
            audio = File(str(path))

        except (MutagenError, OSError):
            return False

        return audio is not None and audio.info is not None
