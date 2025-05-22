# Speech-to-Text Live Transcription

A real-time speech transcription web application built with FastAPI and OpenAI Whisper, featuring live audio processing and accuracy testing capabilities.

## Features

- **Live Transcription**: Real-time speech-to-text conversion with voice activity detection
- **Accuracy Testing**: Built-in test suite with predefined statements to measure transcription accuracy
- **Modern Web Interface**: Clean, responsive UI with real-time status updates
- **WebSocket Integration**: Low-latency audio streaming and transcription delivery

## How It Works

The application uses:
- **OpenAI Whisper** for speech recognition
- **Silero VAD** for voice activity detection
- **FastAPI WebSockets** for real-time audio streaming
- **Browser MediaRecorder API** for audio capture

## Installation & Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd speech-to-text-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:8000`

## Usage

### Live Transcription
1. Click the microphone button to start recording
2. Speak clearly into your microphone
3. View real-time transcription results
4. Click again to stop recording

### Accuracy Testing
1. Switch to the "Accuracy Testing" tab
2. Click the speaker icon to hear test statements
3. Click "Test Now" and repeat the statement
4. View your accuracy score and detailed analysis

## Accuracy Calculation

The accuracy metric is currently calculated using a **simple word-matching algorithm**:
- Splits both original and transcribed text into individual words
- Counts matching words (case-insensitive)
- Calculates percentage: `(matching_words / total_original_words) * 100`

*Note: This is a basic implementation and doesn't account for word order, synonyms, or partial matches.*

## Potential Improvements

### Accuracy Metrics
- **Advanced similarity algorithms** (Levenshtein distance, BLEU score)
- **Semantic similarity** using embeddings
- **Word order consideration** and context matching
- **Phonetic similarity** for pronunciation variations

### Performance Enhancements
- **Model optimization** with quantization and GPU acceleration
- **Streaming improvements** with chunked processing
- **Caching mechanisms** for repeated phrases
- **Multi-language support** with automatic detection

### User Experience
- **Audio playback** of original vs transcribed text
- **Export functionality** for transcription results
- **Custom vocabulary** upload for domain-specific terms
- **Real-time confidence scoring** display

### Technical Improvements
- **Database integration** for persistent results
- **User authentication** and session management
- **API rate limiting** and error handling
- **Docker containerization** for easy deployment

## Requirements

- Python 3.12

## Note

Due to time constraints, I was not able to integrate Pipecat into this implementation. Pipecat integration could have provided enhanced real-time audio processing capabilities and improved streaming performance for production deployments.