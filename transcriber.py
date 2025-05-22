import tempfile
import wave
import os
import whisper


class Transcriber:
    def __init__(self):
        self.model = whisper.load_model('base', download_root='./models')

        self.model.eval()

        self._warm_up_model()

    def _warm_up_model(self):
        try:
            dummy_audio = b'\x00' * 16000
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                self._write_wav(f.name, dummy_audio)
                try:
                    self.model.transcribe(f.name, language="en",
                                          fp16=False,
                                          no_speech_threshold=0.1,
                                          logprob_threshold=-1.0)
                except:
                    pass
                finally:
                    os.remove(f.name)
        except Exception as e:
            print(f"Model warm-up error: {e}")

    def transcribe(self, pcm_bytes):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            self._write_wav(f.name, pcm_bytes)
            try:
                result = self.model.transcribe(f.name,
                                               language="en",
                                               fp16=False,
                                               no_speech_threshold=0.1,
                                               logprob_threshold=-1.0,
                                               compression_ratio_threshold=2.4,
                                               temperature=0.0,
                                               best_of=1,
                                               beam_size=1,
                                               patience=1.0,
                                               length_penalty=1.0,
                                               suppress_tokens=[-1],
                                               initial_prompt=None,
                                               condition_on_previous_text=False,
                                               verbose=False)
                return result['text'].strip()
            except Exception as e:
                print(f"Transcription error: {e}")
                return ""
            finally:
                os.remove(f.name)

    def _write_wav(self, path, pcm):
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm)