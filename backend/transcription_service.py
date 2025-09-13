import os
import io
import base64
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from typing import Optional

# --- Configuration ---
# We use a general-purpose model like "base" which supports multiple languages,
# including English and Hindi, as required by the problem statement.
MODEL_SIZE = "base" 
COMPUTE_TYPE = "int8"
SAMPLE_RATE = 16000
BUFFER_SECONDS = 2

class TranscriptionService:
   
    def __init__(self):
        """Initializes the TranscriptionService by loading the AI model."""
        print("Loading Faster-Whisper model...")
        
        # This initializes the Whisper model from faster-whisper.
        # It's configured to run on the CPU for maximum compatibility.
        self.model = WhisperModel(
            MODEL_SIZE,
            device="cpu", # Forcing CPU usage as requested
            compute_type=COMPUTE_TYPE,
        )
        print(f"Model '{MODEL_SIZE}' loaded and running on CPU.")
        
        # This dictionary will hold the audio buffers for each participant in each room.
        # The key will be a tuple: (room_id, speaker_id)
        self.buffers = {}

    def process_audio_chunk(self, room_id: str, speaker_id: str, base64_data: str) -> Optional[np.ndarray]:
        """
        Decodes incoming audio data, adds it to a buffer, and returns a chunk when ready for transcription.
        
        Args:
            room_id: The unique identifier for the consultation room.
            speaker_id: The identifier for the speaker ('Doctor' or 'Patient').
            base64_data: The raw audio data, base64-encoded.
            
        Returns:
            A NumPy array of audio samples ready for transcription, or None if the buffer is not yet full.
        """
        # Decode the base64 string into raw bytes, then convert to a NumPy array of 16-bit integers.
        audio_bytes = base64.b64decode(base64_data)
        samples = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Convert the audio to float32 format, which is required by the Whisper model.
        samples = samples.astype(np.float32) / 32768.0
        
        key = (room_id, speaker_id)
        if key not in self.buffers:
            self.buffers[key] = np.zeros(0, dtype=np.float32)
        
        # Append the new audio samples to the existing buffer for this speaker.
        self.buffers[key] = np.concatenate([self.buffers[key], samples])

        # Check if the buffer has enough audio to meet our threshold (e.g., 2 seconds).
        if len(self.buffers[key]) >= SAMPLE_RATE * BUFFER_SECONDS:
            # If the buffer is full, slice off a chunk to be transcribed.
            chunk_to_transcribe = self.buffers[key][:SAMPLE_RATE * BUFFER_SECONDS]
            # Keep the rest of the audio in the buffer for the next cycle.
            self.buffers[key] = self.buffers[key][SAMPLE_RATE * BUFFER_SECONDS:]
            return chunk_to_transcribe
            
        return None

    def transcribe_chunk(self, audio_chunk: np.ndarray) -> str:
        """
        Transcribes a chunk of audio using the loaded Whisper model.
        
        Args:
            audio_chunk: A NumPy array of audio samples.
            
        Returns:
            The transcribed text as a string.
        """
        if audio_chunk is None or audio_chunk.size == 0:
            return ""
            
        # The model expects audio in WAV format. We create this in-memory.
        with io.BytesIO() as wav_buffer:
            sf.write(wav_buffer, audio_chunk, SAMPLE_RATE, format="WAV")
            wav_buffer.seek(0)
            
            # This is the core transcription call.
            # language=None enables automatic language detection (for English/Hindi).
            # vad_filter=True helps remove silence and improves accuracy.
            segments, _ = self.model.transcribe(wav_buffer, beam_size=5, vad_filter=True, language=None)
            
            # Join all transcribed segments into a single coherent sentence.
            full_text = " ".join(segment.text.strip() for segment in segments)
            return full_text

# Create a single, global instance of the service that the main app will use.
# This ensures the heavy AI model is only loaded into memory once.
transcriber = TranscriptionService()

