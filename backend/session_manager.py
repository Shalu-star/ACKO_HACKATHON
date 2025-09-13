from fastapi import WebSocket
from typing import Dict, List, Any
from docx import Document
import uuid
from pathlib import Path    
from fastapi.responses import FileResponse

class SessionManager:
  
    def __init__(self):
        """Initializes the SessionManager with a dictionary to hold active rooms."""
        self.rooms: Dict[str, Dict[str, Any]] = {}

    def _ensure_room_exists(self, room_id: str):
        """A helper function to create a room's data structure if it doesn't exist."""
        if room_id not in self.rooms:
            self.rooms[room_id] = {
                "signal_sockets": {},      # For WebRTC video call connections
                "transcribe_sockets": {},  # For AI processing connections
                "history": [],             # Stores the conversation transcript
                "checklist_step": "Introduction" # The starting step of the consultation
            }

    # --- Connection Management ---
    
    def add_signal_socket(self, room_id: str, speaker_id: str, ws: WebSocket):
        """Adds a signaling WebSocket for a user in a room."""
        self._ensure_room_exists(room_id)
        self.rooms[room_id]["signal_sockets"][speaker_id] = ws

    def remove_signal_socket(self, room_id: str, speaker_id: str):
        """Removes a signaling WebSocket and cleans up the room if empty."""
        if room_id in self.rooms:
            if speaker_id in self.rooms[room_id]["signal_sockets"]:
                del self.rooms[room_id]["signal_sockets"][speaker_id]
            self._cleanup_room_if_empty(room_id)

    def add_transcribe_socket(self, room_id: str, speaker_id: str, ws: WebSocket):
        """Adds a transcription WebSocket for a user in a room."""
        self._ensure_room_exists(room_id)
        self.rooms[room_id]["transcribe_sockets"][speaker_id] = ws

    def remove_transcribe_socket(self, room_id: str, speaker_id: str):
        """Removes a transcription WebSocket and cleans up the room if empty."""
        if room_id in self.rooms:
            if speaker_id in self.rooms[room_id]["transcribe_sockets"]:
                del self.rooms[room_id]["transcribe_sockets"][speaker_id]
            self._cleanup_room_if_empty(room_id)

    # --- Message Broadcasting ---

    async def relay_signal(self, room_id: str, sender_id: str, data: str):
        """Relays a WebRTC signaling message to the other user in the room."""
        if room_id in self.rooms:
            for speaker_id, ws in self.rooms[room_id]["signal_sockets"].items():
                if speaker_id != sender_id:
                    await ws.send_text(data)

    async def broadcast_transcribe(self, room_id: str, data: str):
        """Broadcasts AI-related data (transcript, questions) to all users in a room."""
        if room_id in self.rooms:
            for ws in self.rooms[room_id]["transcribe_sockets"].values():
                await ws.send_text(data)

    # --- State Management (History & Checklist) ---

    def add_to_history(self, room_id: str, speaker_id: str, text: str, sentiment: str = None):
        """Adds a new entry to the conversation history for a room."""
        if room_id in self.rooms:
            self.rooms[room_id]["history"].append({
                "speaker": speaker_id,
                "text": text,
                "sentiment": sentiment
            })

    def get_history(self, room_id: str) -> List[Dict]:
        """Retrieves the full conversation history for a room."""
        return self.rooms.get(room_id, {}).get("history", [])

    def update_checklist_step(self, room_id: str, step: str):
        """Updates the current step of the consultation checklist for a room."""
        if room_id in self.rooms:
            self.rooms[room_id]["checklist_step"] = step

    def get_checklist_step(self, room_id: str) -> str:
        """Retrieves the current step of the consultation checklist for a room."""
        return self.rooms.get(room_id, {}).get("checklist_step", "Introduction")

    # --- Cleanup ---

    def _cleanup_room_if_empty(self, room_id: str):
        """Checks if a room is empty and deletes its data if so."""
        if room_id in self.rooms:
            # A room is considered empty if both participants have disconnected.
            if not self.rooms[room_id]["signal_sockets"] and not self.rooms[room_id]["transcribe_sockets"]:
                print(f"Room {room_id} is empty. Cleaning up session data.")
                del self.rooms[room_id]


    def generate_summary_text(self, room_id: str) -> str:
        """Builds a clean text summary from the stored conversation history."""
        history = self.get_history(room_id)
        if not history:
            return "No conversation history found."

        lines = []
        lines.append("=== ACKO Tele-MER Consultation Summary ===\n")
        for entry in history:
            speaker = entry.get("speaker", "Unknown")
            text = entry.get("text", "")
            sentiment = entry.get("sentiment")
            if sentiment:
                lines.append(f"{speaker} ({sentiment}): {text}")
            else:
                lines.append(f"{speaker}: {text}")

        return "\n".join(lines)

    def export_summary_docx(self, room_id: str) -> Path:
        """Exports the summary as a .docx file and returns the path."""
        summary_text = self.generate_summary_text(room_id)
        filename = f"summary_{room_id}_{uuid.uuid4().hex[:6]}.docx"
        filepath = Path(filename)

        doc = Document()
        doc.add_heading('ACKO Tele-MER Consultation Summary', level=1)
        for line in summary_text.split("\n"):
            doc.add_paragraph(line)
        doc.save(filepath)

        return filepath


# Create a single, global instance of the manager that the main app will use.
# This ensures all parts of the application share the same state.
session_manager = SessionManager()

