import winsound
import threading
import os

class SoundManager:
    def __init__(self):
        self.sound_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'assets', 'Windows Balloon.wav'
        )

    def play_complete(self):
        """Play completion sound from local WAV file"""
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=self._play_sound, daemon=True).start()

    def _play_sound(self):
        """Play the actual sound"""
        try:
            if os.path.exists(self.sound_path):
                winsound.PlaySound(self.sound_path, winsound.SND_FILENAME)
        except Exception as e:
            # Silently fail if sound cannot be played
            pass
