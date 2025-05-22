from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import time
import asyncio

from vad import apply_vad
from transcriber import Transcriber

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

transcriber = Transcriber()
clients = []


@app.get("/")
async def get():
    with open("static/index.html") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    complete_audio_buffer = bytearray()
    session_active = True

    last_speech_time = time.time()
    silence_threshold = 2.0
    is_speaking = False
    speech_started = False

    vad_buffer = bytearray()
    vad_check_size = 16000
    last_sent_transcript = ""

    try:
        while True:
            try:
                message = await websocket.receive()

                if message.get('type') == 'websocket.receive' and 'text' in message:
                    control_msg = message['text']
                    if control_msg == "start_session":
                        complete_audio_buffer = bytearray()
                        vad_buffer = bytearray()
                        session_active = True
                        last_speech_time = time.time()
                        is_speaking = False
                        speech_started = False
                        last_sent_transcript = ""
                        print("New transcription session started")
                    elif control_msg == "end_session":
                        session_active = False
                        print("Transcription session ended")
                    continue

                if message.get('type') == 'websocket.receive' and 'bytes' in message:
                    data = message['bytes']
                else:
                    continue

            except Exception as e:
                data = await websocket.receive_bytes()

            if not session_active:
                continue

            print(f"Received {len(data)} bytes of audio data")

            complete_audio_buffer.extend(data)
            vad_buffer.extend(data)

            if len(vad_buffer) > 32000:
                vad_buffer = vad_buffer[-32000:]

            if len(vad_buffer) >= vad_check_size:
                vad_chunk = bytes(vad_buffer[-vad_check_size:])
                has_speech = apply_vad(vad_chunk)
                current_time = time.time()

                if has_speech:
                    print("Speech detected - continuing to collect audio")
                    last_speech_time = current_time
                    is_speaking = True
                    speech_started = True

                    if len(complete_audio_buffer) % 48000 == 0 and len(complete_audio_buffer) >= 48000:
                        try:
                            preview_transcript = transcriber.transcribe(bytes(complete_audio_buffer))
                            if preview_transcript.strip() and preview_transcript.strip() != last_sent_transcript:
                                print(f"Preview transcript: '{preview_transcript.strip()}'")
                                last_sent_transcript = preview_transcript.strip()

                                for client in clients:
                                    try:
                                        await client.send_text(preview_transcript.strip())
                                    except:
                                        if client in clients:
                                            clients.remove(client)
                        except Exception as e:
                            print(f"Preview transcription error: {e}")

                else:
                    print("No speech detected")

                    if speech_started and is_speaking and (current_time - last_speech_time) >= silence_threshold:
                        print(f"Silence detected for {silence_threshold} seconds, processing complete statement...")

                        if len(complete_audio_buffer) > 8000:
                            try:
                                print(
                                    f"Processing complete audio buffer of {len(complete_audio_buffer)} bytes ({len(complete_audio_buffer) / 16000:.1f} seconds)")

                                final_transcript = transcriber.transcribe(bytes(complete_audio_buffer))

                                print(f"FINAL COMPLETE TRANSCRIPT: '{final_transcript}'")

                                if final_transcript.strip():
                                    for client in clients:
                                        try:
                                            await client.send_text(final_transcript.strip())
                                        except:
                                            if client in clients:
                                                clients.remove(client)

                                    print(f"Sent final transcript to clients: '{final_transcript.strip()}'")

                            except Exception as e:
                                print(f"Final transcription error: {e}")

                        print("Resetting for next statement...")
                        is_speaking = False
                        speech_started = False
                        complete_audio_buffer = bytearray()
                        vad_buffer = bytearray()
                        last_sent_transcript = ""

    except WebSocketDisconnect:
        print("Client disconnected")
        if websocket in clients:
            clients.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in clients:
            clients.remove(websocket)