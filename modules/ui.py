"""UI module"""
from __future__ import annotations
import time

import pygame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QAbstractItemView, QComboBox, QDialog,
                             QFileDialog, QFrame, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QMainWindow, QMessageBox,
                             QPushButton, QSlider, QVBoxLayout, QWidget)
from modules.composition import Composition
from modules.playlist import PlayList


class MainWindow(QMainWindow):
    """Mainwindow class"""
    def __init__(self, styles: dict, audio_manager: callable) -> None:
        super().__init__()

        self.audio_manager: callable = audio_manager

        pygame.mixer.init()
        self._current_composition: Composition | None = None
        self._is_playing: bool = False
        self._track_started_at: float = 0.0
        self._track_start_offset: float = 0.0

        self._track_timer: QTimer = QTimer()
        self._track_timer.setInterval(200)
        self._track_timer.timeout.connect(self._check_track_end)
        self._track_timer.start()

        self._styles: dict = styles
        self._create_ui()
        self._playlists = {}
        self.add_playlist()
        self.display_playlists()

        self.setWindowTitle("Player")

        self._create_playlist_dialog: QDialog = None
        self._create_playlist_dialog_lineedit: QLineEdit = None


    def _create_ui(self) -> None:
        """
        create main windows
        """
        centralwidget: QWidget = QWidget()
        self.setCentralWidget(centralwidget)

        self.resize(400, 600)
        main_layout = QVBoxLayout(centralwidget)

        play_list_layout: QHBoxLayout = QHBoxLayout()

        self._playlist_combobox: QComboBox = QComboBox()
        self._playlist_combobox.currentTextChanged.connect(self._fill_file_list)
        create_playlist_btn: QPushButton = QPushButton("+")
        remove_playlist_btn: QPushButton = QPushButton("-")
        play_list_text: QLabel = QLabel("Playlists:")

        compositions_text: QLabel = QLabel("Compositins:")
        self._compositions_list: QListWidget = QListWidget()
        self._compositions_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._compositions_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._compositions_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._compositions_list.model().rowsMoved.connect(self._on_rows_moved)
        self._compositions_list.itemSelectionChanged.connect(self._on_text_changed)

        play_btns_layout: QHBoxLayout = QHBoxLayout()
        play_btns_layout.setContentsMargins(40, 0, 40, 0)

        self._music_slider: QSlider = QSlider(Qt.Orientation.Horizontal)
        self._music_slider.setStyleSheet(self._styles.get("slider_style"))
        self._music_slider.setRange(0, 1000)
        self._music_slider.setValue(0)
        self._music_slider.setFixedHeight(20)
        self._music_slider.sliderPressed.connect(self._on_slider_moved)

        previous_composition_btn: QPushButton = QPushButton("<-")
        self.play_composition_btn: QPushButton = QPushButton("Play")
        next_composition_btn: QPushButton = QPushButton("->")

        manage_btns_layout: QHBoxLayout = QHBoxLayout()
        manage_btns_layout.setContentsMargins(60, 0, 60, 0)
        add_composition_btn: QPushButton = QPushButton("Add")
        remove_composition_btn: QPushButton = QPushButton("Remove")

        play_list_layout.addWidget(play_list_text)
        play_list_layout.addWidget(self._playlist_combobox, stretch=1)

        buttons = (
            (create_playlist_btn, self._create_playlist, play_list_layout, 0),
            (remove_playlist_btn, self.remove_playlist, play_list_layout, 0),
            (previous_composition_btn, self.previous_composition, play_btns_layout, 0),
            (self.play_composition_btn, self.play_composition, play_btns_layout, 1),
            (next_composition_btn, self.next_composition, play_btns_layout, 0),
            (add_composition_btn, self.add_composition, manage_btns_layout, 0),
            (remove_composition_btn, self.remove_composition, manage_btns_layout, 0)
        )

        for button, func, layout, stratch in buttons:
            layout.addWidget(button, stratch)
            button.clicked.connect(func)

        line1: QFrame = QFrame()
        line2: QFrame = QFrame()

        lines: list = [
            line1, line2
        ]

        for line in lines:
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)

        main_layout.addLayout(play_list_layout)
        main_layout.addWidget(line1)
        main_layout.addWidget(compositions_text)
        main_layout.addWidget(self._compositions_list)
        main_layout.addWidget(line2)
        main_layout.addWidget(self._music_slider)
        main_layout.addLayout(play_btns_layout)
        main_layout.addLayout(manage_btns_layout)

    def display_playlists(self) -> None:
        """
        display playlist when that changed
        """
        self._playlist_combobox.clear()
        self._playlist_combobox.addItems(tuple(self._playlists.keys()))

    def _on_slider_moved(self) -> None:
        """
        check when user move slider
        """
        new_poz = self._music_slider.value()
        comp = self._current_composition
        if comp is None:
            return

        sec = new_poz / self._music_slider.maximum() * comp.duration

        try:
            pygame.mixer.music.play(start=sec)
        except pygame.error as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self._track_start_offset = sec
        self._track_started_at = time.monotonic()
        self._is_playing = True
        self.play_composition_btn.setText("Stop")

    def stop_playing(self) -> None:
        """
        stop playing music
        """
        self._track_start_offset = self.current_position()
        pygame.mixer.music.pause()
        self._is_playing = False
        self.play_composition_btn.setText("Play")

    def _on_text_changed(self) -> None:
        """
        check when change composition on list
        """
        selected = self._compositions_list.selectedItems()
        if not selected:
            return

        new_name = selected[0].text()

        if self._current_composition is None:
            return

        if self._current_composition.name != new_name:
            self.stop_playing()

    def add_playlist(self, name: str ="Default") -> PlayList:
        """
        add playlist to list of playlists
        """
        self._playlists[name] = PlayList()

        return self._playlists[name]

    def _check_track_end(self) -> None:
        """
        check track end and swap composition
        """
        if not self._is_playing:
            return

        if not pygame.mixer.music.get_busy():
            self._is_playing = False
            self.next_composition()
            return

        self._update_slider()

    def _update_slider(self) -> None:
        """
        set music slider to current position
        """
        comp = self._current_composition
        if comp is None or comp.duration <= 0:
            return

        pos = self.current_position()
        pos = min(pos, comp.duration)
        value = int(pos / comp.duration * self._music_slider.maximum())

        self._music_slider.blockSignals(True)
        self._music_slider.setSliderPosition(value)
        self._music_slider.blockSignals(False)

    def current_position(self) -> float:
        """
        return current position of composition timeline
        """
        if not self._is_playing:
            return self._track_start_offset

        return self._track_start_offset + (time.monotonic() - self._track_started_at)

    def play_composition(self) -> None:
        """
        play composition by click appropriate buttons
        """
        if not self._is_playing:
            selected = self._compositions_list.selectedItems()
            if not selected:
                return

            playlist = self._get_current_playlist()
            new = playlist.find_composition_by_name(
                selected[0].text()
            )
            if new is None:
                return

            if new != self._current_composition:
                self._current_composition = new
                playlist.play_all(new)
                self._track_start_offset = 0.0
                try:
                    pygame.mixer.music.load(str(new.path))
                except pygame.error as e:
                    QMessageBox.critical(self, "Error", str(e))
                    return

            try:
                pygame.mixer.music.play(start=self._track_start_offset)
            except pygame.error as e:
                QMessageBox.critical(self, "Error", str(e))
                return

            self._track_started_at = time.monotonic()
            self._is_playing = True
            self.play_composition_btn.setText("Stop")

        else:
            self.stop_playing()

    def _on_rows_moved(self) -> None:
        """
        function that track rows change
        """
        update_playlist = PlayList()

        items = [
            self._compositions_list.item(i).text()
            for i in range(self._compositions_list.count())
        ]

        for item in items:
            update_playlist.append(
                self._get_current_playlist().find_composition_by_name(item)
            )

        self._playlists[self._get_current_playlist_name()] = update_playlist

    def _get_current_playlist_name(self) -> str:
        """
        return current playlist name
        """
        return self._playlist_combobox.currentText()

    def _get_current_playlist(self) -> PlayList:
        """
        return current playlist
        """
        return self._playlists.get(self._get_current_playlist_name())

    def _fill_file_list(self) -> bool:
        """
        fill compostion list
        """
        self._compositions_list.clear()

        current_playlist = self._get_current_playlist()
        if current_playlist is None or len(current_playlist) == 0:
            return False

        that_num = -1

        for num, node in enumerate(current_playlist):
            composition = node.data
            self._compositions_list.addItem(composition.name)

            if self._current_composition == composition:
                that_num = num

        if (self._current_composition is not None
                and self._current_composition not in current_playlist):
            self._clear_playing()

        elif that_num > -1:
            self._compositions_list.setCurrentRow(that_num)

        return True

    def _havent_playlists_error(self) -> None:
        """
        create warninig message when user do something with composition
        when playlist isn't exists
        """
        QMessageBox.warning(self, "Haven't playlist", "For first - create playlist")

    def add_composition(self) -> bool:
        """
        add composition to list
        """
        current_playlist = self._get_current_playlist()
        if current_playlist is None:
            self._havent_playlists_error()
            return False

        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select files",
            "",
            "Audio (*.mp3 *.wav *.ogg *.flac);;All files (*)",
        )

        if not paths:
            return False

        for file in paths:
            composition = Composition(
                file.split("/")[-1], file, self.audio_manager.get_duration(file)
            )

            if composition in current_playlist:
                continue

            current_playlist.append(composition)

        self._fill_file_list()
        return True

    def _clear_playing(self) -> None:
        """
        stop playing music and change btn
        """
        pygame.mixer.music.stop()
        self._is_playing = False
        self._current_composition = None
        self._track_start_offset = 0.0
        self.play_composition_btn.setText("Play")
        self._music_slider.blockSignals(True)
        self._music_slider.setSliderPosition(0)
        self._music_slider.blockSignals(False)

    def remove_composition(self) -> bool:
        """
        remove composition from list
        """
        current_playlist = self._get_current_playlist()
        if current_playlist is None:
            self._havent_playlists_error()
            return

        selected = self._compositions_list.selectedItems()

        if not selected:
            return

        name = selected[0].text()
        comp = current_playlist.find_composition_by_name(name)

        if comp is None:
            return

        if comp == self._current_composition:
            pygame.mixer.music.stop()

        current_playlist.remove(comp)
        self._fill_file_list()

    def _highlight_current(self) -> None:
        """
        set cursor in composition list to current composition
        """
        playlist = self._get_current_playlist()

        if playlist is None:
            return

        current = playlist.current

        if current is None:
            return

        for index in range(self._compositions_list.count()):
            item = self._compositions_list.item(index)
            if item.text() == current.name:
                self._compositions_list.setCurrentRow(index)
                self._compositions_list.scrollToItem(item)
                return

        return

    def _composition_manager(self, pointer) -> None:
        """
        auxiliary function that uses in next_composition and previous_composition
        """
        playlist = self._get_current_playlist()
        if playlist is None or len(playlist) == 0:
            return

        getattr(playlist, pointer)()
        composition = playlist.current
        if composition is None:
            return

        self._current_composition = composition
        self._track_start_offset = 0.0

        try:
            pygame.mixer.music.load(str(composition.path))
            pygame.mixer.music.play()

        except pygame.error as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self._track_started_at = time.monotonic()
        self._is_playing = True
        self.play_composition_btn.setText("Stop")
        self._highlight_current()

    def next_composition(self) -> None:
        """
        change current composition to next regarding current
        """
        self._composition_manager("next_track")

    def previous_composition(self) -> None:
        """
        change current composition to previous regarding current
        """
        self._composition_manager("previous_track")

    def _create_playlist(self) -> None:
        """
        open create playlist menu
        """
        self._create_playlist_dialog = QDialog(self)
        self._create_playlist_dialog.setWindowTitle("Create playlist")
        self._create_playlist_dialog.resize(250, 100)

        playlist_main_layout = QVBoxLayout(self._create_playlist_dialog)

        create_playlist_dialog_hlayout1 = QHBoxLayout()
        create_playlist_dialog_hlayout1.addWidget(QLabel("Name:"))
        self._create_playlist_dialog_lineedit = QLineEdit()
        create_playlist_dialog_hlayout1.addWidget(self._create_playlist_dialog_lineedit)
        playlist_main_layout.addLayout(create_playlist_dialog_hlayout1)

        create_playlist_dialog_hlayout2 = QHBoxLayout()
        accept_btn = QPushButton("Accept")
        cancel_btn = QPushButton("Cancel")
        create_playlist_dialog_hlayout2.addWidget(accept_btn)
        create_playlist_dialog_hlayout2.addWidget(cancel_btn)
        cancel_btn.clicked.connect(self._cancel_playlist)
        accept_btn.clicked.connect(self._accept_playlist)
        playlist_main_layout.addLayout(create_playlist_dialog_hlayout2)

        self._create_playlist_dialog.show()

    def _cancel_playlist(self) -> None:
        """
        exit from create playlist menu
        """
        self._create_playlist_dialog.close()

    def _accept_playlist(self) -> None:
        """
        calling when user clicked on accept btn when he create new playlist
        and validate that playlist
        """
        name = self._create_playlist_dialog_lineedit.text()
        if name == "":
            QMessageBox.critical(
                self._create_playlist_dialog, "Error",
                "Name of playlist should not be empty")
            return

        if name in self._playlists:
            QMessageBox.critical(
                self._create_playlist_dialog, "Error",
                "Playlist with this name already exists")
            return

        self.add_playlist(name)

        self.display_playlists()
        self._playlist_combobox.setCurrentText(name)
        self._clear_playing()
        self._fill_file_list()
        self._cancel_playlist()

    def remove_playlist(self) -> None:
        """
        Remove current playlist from list and combobox
        """
        name = self._playlist_combobox.currentText()

        if not name or name not in self._playlists:
            return

        del self._playlists[name]

        if len(self._playlists) == 0:
            self._clear_playing()

        self.display_playlists()
        self._fill_file_list()
