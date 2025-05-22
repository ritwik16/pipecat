import torch
import numpy as np

class SileroVAD:
    def __init__(self):
        try:
            self.model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            self.model.eval()

            if hasattr(torch, 'jit') and hasattr(torch.jit, 'optimize_for_inference'):
                self.model = torch.jit.optimize_for_inference(self.model)

            self.initialized = True
            print("Silero VAD initialized successfully with optimizations")
        except Exception as e:
            print(f"Failed to initialize Silero VAD: {e}")
            self.initialized = False

    def apply_vad(self, audio_bytes: bytes, threshold: float = 0.3) -> bool:
        if not self.initialized:
            return True

        try:
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16)

            audio_float = audio_np.astype(np.float32) / 32768.0

            chunk_size = 512
            speech_detected = False

            for i in range(0, len(audio_float), chunk_size):
                chunk = audio_float[i:i + chunk_size]

                if len(chunk) < chunk_size:
                    continue

                audio_tensor = torch.from_numpy(chunk)

                with torch.no_grad():
                    speech_prob = self.model(audio_tensor, 16000).item()

                print(f"VAD chunk {i // chunk_size + 1}: speech probability: {speech_prob:.3f}")

                if speech_prob > threshold:
                    speech_detected = True
                    break

            return speech_detected

        except Exception as e:
            print(f"Silero VAD Error: {e}")
            return True


vad_model = None


def initialize_vad():
    global vad_model
    if vad_model is None:
        vad_model = SileroVAD()


def apply_vad(audio_bytes: bytes, threshold: float = 0.3) -> bool:
    global vad_model

    if vad_model is None:
        initialize_vad()

    return vad_model.apply_vad(audio_bytes, threshold)