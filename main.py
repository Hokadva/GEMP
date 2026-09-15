"""Main programm module, startapp"""
import sys

from PyQt6.QtWidgets import QApplication

from modules.audio_manager import AudioManager
from modules.styles import STYLES
from modules.ui import MainWindow


class Main:
    """Main programm class"""
    def __init__(self, app, main_window):
        """initialization class"""
        self.app = app
        self.main_window = main_window

    def start(self):
        """show UI and start programm"""
        self.main_window.show()
        sys.exit(self.app.exec())

    def stop(self):
        """Stop application"""
        self.app.quit()



if __name__ == "__main__":
    aplication = QApplication(sys.argv)
    audio_manager = AudioManager()
    window = MainWindow(STYLES, audio_manager)

    main = Main(aplication, window)
    main.start()
