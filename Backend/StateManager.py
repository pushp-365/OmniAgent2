"""
Centralized State Manager for OmniAgent Web Application
Manages microphone, speaker, and assistant status across threads
"""
import threading
from queue import Queue
import os

current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"


class StateManager:
    """Thread-safe state management for OmniAgent"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.mic_enabled = False
        self.speaker_enabled = True
        self.current_status = "Available"
        self.message_queue = Queue()  # For passing messages between threads
        self.response_queue = Queue()  # For receiving responses
        
    def toggle_mic(self):
        """Toggle microphone state"""
        with self._lock:
            self.mic_enabled = not self.mic_enabled
            self._update_mic_file()
            return self.mic_enabled
    
    def set_mic(self, enabled):
        """Set microphone state explicitly"""
        with self._lock:
            self.mic_enabled = enabled
            self._update_mic_file()
            return self.mic_enabled
    
    def get_mic_status(self):
        """Get current microphone status"""
        with self._lock:
            return self.mic_enabled
    
    def toggle_speaker(self):
        """Toggle speaker state"""
        with self._lock:
            self.speaker_enabled = not self.speaker_enabled
            self._update_speaker_file()
            return self.speaker_enabled
    
    def set_speaker(self, enabled):
        """Set speaker state explicitly"""
        with self._lock:
            self.speaker_enabled = enabled
            self._update_speaker_file()
            return self.speaker_enabled
    
    def get_speaker_status(self):
        """Get current speaker status"""
        with self._lock:
            return self.speaker_enabled
    
    def set_status(self, status):
        """Set assistant status"""
        with self._lock:
            self.current_status = status
            self._update_status_file()
    
    def get_status(self):
        """Get current assistant status"""
        with self._lock:
            return self.current_status
    
    def _update_mic_file(self):
        """Update microphone status file"""
        try:
            with open(rf'{TempDirPath}\Mic.data', 'w', encoding='utf-8') as file:
                file.write("True" if self.mic_enabled else "False")
        except Exception as e:
            print(f"Error updating mic file: {e}")
    
    def _update_speaker_file(self):
        """Update speaker status file"""
        try:
            with open(rf'{TempDirPath}\Speaker.data', 'w', encoding='utf-8') as file:
                file.write("True" if self.speaker_enabled else "False")
        except Exception as e:
            print(f"Error updating speaker file: {e}")
    
    def _update_status_file(self):
        """Update status file"""
        try:
            with open(rf'{TempDirPath}\Status.data', 'w', encoding='utf-8') as file:
                file.write(self.current_status)
        except Exception as e:
            print(f"Error updating status file: {e}")
    
    def add_message(self, message_type, content):
        """Add a message to the processing queue"""
        self.message_queue.put({
            'type': message_type,  # 'text' or 'voice'
            'content': content
        })
    
    def get_message(self, block=True, timeout=None):
        """Get a message from the queue"""
        try:
            return self.message_queue.get(block=block, timeout=timeout)
        except:
            return None
    
    def add_response(self, response):
        """Add a response to the response queue"""
        self.response_queue.put(response)
    
    def get_response(self, block=True, timeout=None):
        """Get a response from the queue"""
        try:
            return self.response_queue.get(block=block, timeout=timeout)
        except:
            return None


# Global state manager instance
state_manager = StateManager()


# Helper functions for backward compatibility
def GetSpeakerStatus():
    """Get speaker status (for backward compatibility)"""
    return "True" if state_manager.get_speaker_status() else "False"


def SetSpeakerStatus(status):
    """Set speaker status (for backward compatibility)"""
    enabled = status.lower() == "true"
    state_manager.set_speaker(enabled)
