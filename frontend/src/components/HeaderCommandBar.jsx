import React, { useState, useEffect, useRef } from 'react';

export default function HeaderCommandBar({
  onSendMessage,
  latestResponse,
  isProcessing,
  isSpeaking,
  onToggleSpeech,
  speechEnabled,
  onListeningStateChange
}) {
  const [inputVal, setInputVal] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [copied, setCopied] = useState(false);
  const recognitionRef = useRef(null);
  const isListeningRef = useRef(false);
  const onSendMessageRef = useRef(onSendMessage);
  const silenceTimerRef = useRef(null);
  const accumulatedTranscriptRef = useRef('');

  useEffect(() => {
    onSendMessageRef.current = onSendMessage;
  }, [onSendMessage]);

  // Initialize Web Speech API with mobile + desktop compatibility
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent || '');
        const recognition = new SpeechRecognition();
        
        // Mobile browsers (Chrome on Android / iOS Safari) require non-continuous mode
        recognition.continuous = !isMobile;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
          isListeningRef.current = true;
          setIsListening(true);
          onListeningStateChange?.(true);
          accumulatedTranscriptRef.current = '';
        };

        recognition.onresult = (event) => {
          let interimText = '';
          let finalText = '';

          for (let i = 0; i < event.results.length; ++i) {
            const transcript = event.results[i][0]?.transcript || '';
            if (event.results[i].isFinal) {
              finalText += transcript + ' ';
            } else {
              interimText += transcript;
            }
          }

          const combined = (finalText + interimText).trim();
          if (combined) {
            setInputVal(combined);
            accumulatedTranscriptRef.current = combined;
          }

          // Auto-submit after 1.4s of silence
          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
          }

          silenceTimerRef.current = setTimeout(() => {
            const queryToSend = accumulatedTranscriptRef.current.trim();
            if (queryToSend) {
              try {
                recognition.stop();
              } catch (_) {}
              isListeningRef.current = false;
              setIsListening(false);
              onListeningStateChange?.(false);
              setInputVal('');
              accumulatedTranscriptRef.current = '';
              onSendMessageRef.current(queryToSend);
            }
          }, 1400);
        };

        recognition.onerror = (event) => {
          if (event.error !== 'no-speech' && event.error !== 'aborted') {
            console.warn('Speech recognition notice:', event.error);
          }
          if (event.error === 'not-allowed') {
            alert('Microphone access was denied. Please allow microphone permissions in your browser bar.');
          }
          isListeningRef.current = false;
          setIsListening(false);
          onListeningStateChange?.(false);
        };

        recognition.onend = () => {
          isListeningRef.current = false;
          setIsListening(false);
          onListeningStateChange?.(false);

          // On mobile, submit when speech ends if transcript exists
          const queryToSend = accumulatedTranscriptRef.current.trim();
          if (queryToSend) {
            setInputVal('');
            accumulatedTranscriptRef.current = '';
            onSendMessageRef.current(queryToSend);
          }
        };

        recognitionRef.current = recognition;
      } catch (e) {
        console.warn('Speech recognition initialization notice:', e);
      }
    }

    return () => {
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      if (recognitionRef.current && isListeningRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (_) {}
      }
    };
  }, [onListeningStateChange]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    if (recognitionRef.current && isListeningRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (_) {}
    }
    const query = inputVal.trim() || accumulatedTranscriptRef.current.trim();
    if (!query || isProcessing) return;
    setInputVal('');
    accumulatedTranscriptRef.current = '';
    onSendMessageRef.current(query);
  };

  const handleVoiceToggle = () => {
    if (!recognitionRef.current) {
      alert('Speech Recognition is not supported on this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isListening) {
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      try {
        recognitionRef.current.stop();
      } catch (_) {}
      const query = inputVal.trim() || accumulatedTranscriptRef.current.trim();
      if (query) {
        setInputVal('');
        accumulatedTranscriptRef.current = '';
        onSendMessageRef.current(query);
      }
    } else {
      try {
        accumulatedTranscriptRef.current = '';
        setInputVal('');
        recognitionRef.current.start();
      } catch (err) {
        if (err.name !== 'InvalidStateError') {
          console.warn('Speech recognition start notice:', err);
        }
      }
    }
  };

  const handleCopy = () => {
    if (!latestResponse) return;
    try {
      navigator.clipboard.writeText(latestResponse);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (_) {}
  };

  return (
    <div className="header-command-bar">
      <form className="command-input-container" onSubmit={handleSubmit}>
        <div className="input-glow-wrapper">
          <span className={`input-prefix ${isListening ? 'listening-pulse' : ''}`}>
            {isListening ? '🎙️' : '>'}
          </span>
          <input
            type="text"
            className={`cyber-input ${isListening ? 'input-recording' : ''}`}
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder={
              isListening
                ? 'Listening... Speak your command'
                : "Type or click 🎤 (e.g. 'play hall of fame on youtube', 'open whatsapp')..."
            }
            disabled={isProcessing}
            autoFocus
          />
        </div>

        <div className="command-actions">
          <button
            type="submit"
            className={`btn-primary ${isProcessing ? 'processing' : ''}`}
            disabled={isProcessing || !inputVal.trim()}
          >
            {isProcessing ? (
              <span className="spinner-wrap">
                <span className="cyber-spinner"></span>
                Processing...
              </span>
            ) : (
              'Speak to NOVA'
            )}
          </button>

          <button
            type="button"
            className={`btn-voice ${isListening ? 'listening active-recording' : ''}`}
            onClick={handleVoiceToggle}
            title={isListening ? 'Listening... click to send' : 'Click to speak via microphone'}
          >
            <span className="mic-icon">🎤</span>
            {isListening && <span className="pulse-ring"></span>}
          </button>

          <button
            type="button"
            className={`btn-copy ${copied ? 'copied' : ''}`}
            onClick={handleCopy}
            title="Copy latest response"
          >
            {copied ? '✓ Copied' : 'Copy'}
          </button>

          <button
            type="button"
            className={`btn-speech-toggle ${speechEnabled ? 'enabled' : 'disabled'}`}
            onClick={onToggleSpeech}
            title={speechEnabled ? 'TTS Voice Enabled' : 'TTS Voice Muted'}
          >
            {speechEnabled ? '🔊' : '🔇'}
          </button>
        </div>
      </form>
    </div>
  );
}
