import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import numpy as np

# Import all our custom service modules
from session_manager import session_manager
from transcription_service import transcriber
from question_engine import question_engine
from sentiment_analyzer import sentiment_analyzer

# --- FastAPI App Setup ---
app = FastAPI()

# Mount the 'frontend' directory to serve static files (like index.html and patient.html)
# This allows the browser to access our user interface files.
app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")

@app.on_event("startup")
async def startup_event():
    """Code to run when the server starts."""
    # This is where we could pre-load any other models or resources.
    # The individual services already load their own models upon initialization.
    print("Server has started and all AI models are loaded.")

@app.on_event("shutdown")
async def shutdown_event():
    """Code to run when the server shuts down."""
    print("Server is shutting down.")

# --- HTML Page Routes ---
@app.get("/", response_class=HTMLResponse)
async def get_doctor_page(request: Request):
    """Serves the main doctor's interface."""
    with open("../frontend/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/patient", response_class=HTMLResponse)
async def get_patient_page(request: Request):
    """Serves the simple patient interface."""
    with open("../frontend/patient.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# --- WebSocket Endpoints ---
@app.websocket("/ws/signal")
async def ws_signal(ws: WebSocket, room: str, speaker: str):
    """
    WebSocket for WebRTC signaling. This helps the doctor and patient
    browsers establish a direct peer-to-peer video call connection.
    """
    await ws.accept()
    session_manager.add_signal_socket(room, speaker, ws)
    try:
        while True:
            data = await ws.receive_text()
            # Relay the signaling message to the other participant in the room.
            await session_manager.relay_signal(room, speaker, data)
    except WebSocketDisconnect:
        session_manager.remove_signal_socket(room, speaker)
        print(f"Signal socket for {speaker} in room {room} disconnected.")

@app.websocket("/ws/transcribe")
async def ws_transcribe(ws: WebSocket):
    """
    The main WebSocket for AI processing. It receives audio, transcribes it,
    analyzes sentiment, and generates reflexive questions.
    """
    await ws.accept()
    room_id = None
    speaker_id = None
    
    try:
        # The first message must be a "join" message.
        join_msg = json.loads(await ws.receive_text())
        if join_msg.get("type") == "join":
            room_id = join_msg["room"]
            speaker_id = join_msg["speaker"]
            session_manager.add_transcribe_socket(room_id, speaker_id, ws)
            print(f"Transcription socket for {speaker_id} in room {room_id} connected.")
        else:
            await ws.close()
            return

        while True:
            raw_data = await ws.receive_text()
            msg = json.loads(raw_data)
            
            # --- Main AI Pipeline ---
            if msg.get("type") == "audio":
                # 1. Process and buffer the audio chunk
                chunk_to_process = transcriber.process_audio_chunk(room_id, speaker_id, msg["data"])

                if chunk_to_process is not None:
                    # 2. Transcribe the audio chunk if the buffer is full
                    full_text = transcriber.transcribe_chunk(chunk_to_process)

                    if full_text:
                        # 3. Analyze sentiment for patient's speech
                        sentiment = None
                        if speaker_id == "Patient":
                            sentiment = sentiment_analyzer.analyze(full_text)

                        # 4. Store the new transcript line in the session history
                        session_manager.add_to_history(room_id, speaker_id, full_text, sentiment)

                        # 5. Broadcast the transcript and sentiment to the doctor's UI
                        transcript_event = {
                            "type": "transcript",
                            "speaker": speaker_id,
                            "text": full_text,
                            "sentiment": sentiment
                        }
                        await session_manager.broadcast_transcribe(room_id, json.dumps(transcript_event))

                        # 6. Generate reflexive questions based on patient's speech
                        if speaker_id == "Patient":
                            current_history = session_manager.get_history(room_id)
                            current_step = session_manager.get_checklist_step(room_id)
                            questions = await question_engine.generate_question(current_history, current_step)
                            
                            if questions:
                                question_event = {
                                    "type": "question",
                                    "questions": questions
                                }
                                await session_manager.broadcast_transcribe(room_id, json.dumps(question_event))

            # --- Handle checklist updates from the doctor's UI ---
            elif msg.get("type") == "update_checklist":
                new_step = msg.get("step")
                session_manager.update_checklist_step(room_id, new_step)
                print(f"Room {room_id} advanced to checklist step: {new_step}")

    except WebSocketDisconnect:
        if room_id and speaker_id:
            session_manager.remove_transcribe_socket(room_id, speaker_id)
            print(f"Transcription socket for {speaker_id} in room {room_id} disconnected.")
    except Exception as e:
        print(f"An error occurred in the transcription websocket: {e}")
        if room_id and speaker_id:
            session_manager.remove_transcribe_socket(room_id, speaker_id)

