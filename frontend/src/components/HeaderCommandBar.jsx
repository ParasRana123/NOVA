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

  // Initialize Web Speech API for voice listening with robust event handling
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      try {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
          isListeningRef.current = true;
          setIsListening(true);
          onListeningStateChange?.(true);
        };

        recognition.onresult = (event) => {
          const transcript = event.results?.[0]?.[0]?.transcript;
          if (transcript) {
            setInputVal(transcript);
            onSendMessage(transcript);
          }
        };

        recognition.onerror = (event) => {
          if (event.error !== 'no-speech' && event.error !== 'aborted') {
            console.warn('Speech recognition notice:', event.error);
          }
          isListeningRef.current = false;
          setIsListening(false);
          onListeningStateChange?.(false);
        };

        recognition.onend = () => {
          isListeningRef.current = false;
          setIsListening(false);
          onListeningStateChange?.(false);
        };

        recognitionRef.current = recognition;
      } catch (e) {
        console.warn('Speech recognition init notice:', e);
      }
    }

    return () => {
      if (recognitionRef.current && isListeningRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (_) {}
      }
    };
  }, [onSendMessage, onListeningStateChange]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!inputVal.trim() || isProcessing) return;
    const query = inputVal.trim();
    setInputVal('');
    onSendMessage(query);
  };

  const handleVoiceToggle = () => {
    if (!recognitionRef.current) {
      alert('Speech Recognition is not supported on this browser. Try Chrome/Edge or use the text input.');
      return;
    }

    if (isListening) {
      try {
        recognitionRef.current.stop();
      } catch (_) {}
    } else {
      try {
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
          <span className="input-prefix">&gt;</span>
          <input
            type="text"
            className="cyber-input"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Type a command (e.g. 'open whatsapp', 'play interstellar on youtube', 'remind me at 5pm', 'weather in Mumbai')..."
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
            className={`btn-voice ${isListening ? 'listening' : ''}`}
            onClick={handleVoiceToggle}
            title={isListening ? 'Listening... click to stop' : 'Click to speak via microphone'}
          >
            <span className="mic-icon">🎤</span>
            {isListening && <span className="pulse-ring"></span>}
          </button>

          <button
            type="button"
            className={`btn-copy ${copied ? 'copied' : ''}`}
            onClick={handleCopy}
            title="Copy latest NOVA response to clipboard"
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
