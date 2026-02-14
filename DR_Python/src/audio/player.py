from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, QObject, pyqtSignal

class AudioPlayer(QObject):
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    state_changed = pyqtSignal(QMediaPlayer.PlaybackState)
    
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Connect signals
        # Connect signals
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.errorOccurred.connect(self._on_error)
        
        self.audio_output.setVolume(0.8)

    def _on_error(self, error, error_string):
        print(f"AUDIO ERROR: {error} - {error_string}")

    def _on_position_changed(self, pos):
        # print(f"Position: {pos}") # Too spammy
        self.position_changed.emit(pos)

    def _on_duration_changed(self, duration):
        print(f"Duration changed: {duration}")
        self.duration_changed.emit(duration)

    def _on_state_changed(self, state):
        print(f"State changed: {state}")
        self.state_changed.emit(state)

    def load(self, file_path):
        if file_path.startswith("http"):
            url = QUrl(file_path)
        else:
            url = QUrl.fromLocalFile(file_path)
        self.player.setSource(url)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()
        
    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def set_position(self, position_ms):
        self.player.setPosition(position_ms)

    def set_volume(self, volume_0_to_1):
        self.audio_output.setVolume(volume_0_to_1)
        
    def set_playback_rate(self, rate):
        self.player.setPlaybackRate(rate)
        
    def get_duration(self):
        return self.player.duration()
        
    def get_position(self):
        return self.player.position()
