import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import HeaderCommandBar from './components/HeaderCommandBar';
import SiriVisualizer from './components/SiriVisualizer';
import WeatherClockWidget from './components/WeatherClockWidget';
import ResponseDisplay from './components/ResponseDisplay';
import ChatHistoryPanel from './components/ChatHistoryPanel';
import VisionAnalyzer from './components/VisionAnalyzer';
import { fetchHealth, fetchWeather, fetchChatHistory, sendChatMessage, speakText, getClientCoordinates } from './services/api';

// Function to automatically launch native apps or navigate to direct official URLs
function autoRedirectOrLaunch(action) {
  if (!action) return;
  const { protocol, url, app } = action;
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent || '');

  console.log(`[NOVA Client] Launching ${app || 'action'} (protocol: ${protocol}, url: ${url}, isMobile: ${isMobile})`);

  setTimeout(() => {
    if (isMobile) {
      // On mobile devices, target the native protocol first (opens native app) or direct URL
      const mobileTarget = protocol || url;
      if (mobileTarget) {
        window.location.href = mobileTarget;
      }
    } else {
      // On desktop devices
      if (protocol) {
        // Trigger OS protocol handler via invisible iframe so desktop software opens
        try {
          const iframe = document.createElement('iframe');
          iframe.style.position = 'fixed';
          iframe.style.top = '-9999px';
          iframe.style.left = '-9999px';
          iframe.style.width = '1px';
          iframe.style.height = '1px';
          iframe.style.border = 'none';
          iframe.src = protocol;
          document.body.appendChild(iframe);
          setTimeout(() => {
            try { document.body.removeChild(iframe); } catch (_) {}
          }, 3000);
        } catch (_) {}
      }

      // Automatically navigate to official web URL if no desktop protocol or alongside web services
      if (url) {
        window.location.href = url;
      }
    }
  }, 400);
}

function App() {
  const [serverOnline, setServerOnline] = useState(false);
  const [weatherData, setWeatherData] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const [latestQuery, setLatestQuery] = useState('');
  const [latestResponse, setLatestResponse] = useState('');
  const [commandType, setCommandType] = useState('');
  const [latestAction, setLatestAction] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speechEnabled, setSpeechEnabled] = useState(true);
  const [statusText, setStatusText] = useState('NOVA is ready.');

  // Load telemetry & history
  const loadTelemetry = useCallback(async () => {
    const health = await fetchHealth();
    setServerOnline(health.status === 'healthy');

    // Get user's actual browser/GPS coordinates
    const coords = await getClientCoordinates();
    const weather = await fetchWeather(coords?.lat, coords?.lon);
    setWeatherData(weather);

    const history = await fetchChatHistory();
    setChatHistory(history);
  }, []);

  useEffect(() => {
    loadTelemetry();
    const interval = setInterval(loadTelemetry, 30000);
    return () => clearInterval(interval);
  }, [loadTelemetry]);

  // Handle user commands
  const handleSendMessage = async (queryText) => {
    if (!queryText.trim()) return;

    setLatestQuery(queryText);
    setIsProcessing(true);
    setStatusText(`Processing: "${queryText}"`);
    setLatestAction(null);

    const result = await sendChatMessage(queryText, speechEnabled);
    setIsProcessing(false);

    if (result.response) {
      setLatestResponse(result.response);
      setCommandType(result.command_type || 'general_chat');
      setLatestAction(result.action || null);
      setStatusText(result.status === 'success' ? 'Command completed.' : 'Response received.');

      // Browser Speech Synthesis with guarded lifecycle
      if (speechEnabled && 'speechSynthesis' in window && !result.response.includes('Error')) {
        try {
          window.speechSynthesis.cancel();
          const cleanSpeechText = result.response.replace(/[#*`_~>[\]]/g, '').trim();
          const utterance = new SpeechSynthesisUtterance(cleanSpeechText);
          utterance.rate = 1.0;
          utterance.pitch = 1.0;

          utterance.onstart = () => setIsSpeaking(true);
          utterance.onend = () => setIsSpeaking(false);
          utterance.onerror = (e) => {
            if (e.error !== 'interrupted' && e.error !== 'canceled') {
              console.warn('Speech synthesis notice:', e.error);
            }
            setIsSpeaking(false);
          };

          window.speechSynthesis.speak(utterance);
        } catch (speechErr) {
          console.warn('Speech synthesis invocation notice:', speechErr);
          setIsSpeaking(false);
        }
      }

      // Automatically launch native app or direct official web destination
      if (result.action) {
        autoRedirectOrLaunch(result.action);
      }

      // Refresh chat log
      const updatedHistory = await fetchChatHistory();
      setChatHistory(updatedHistory);
    } else {
      setLatestResponse(result.error || 'No response received from NOVA backend.');
      setStatusText('Error processing request.');
    }
  };

  const handleToggleSpeech = () => {
    setSpeechEnabled((prev) => !prev);
    if (speechEnabled && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (_) {}
    }
  };

  return (
    <div className="nova-app-container">
      {/* Top Cyber Navigation Bar */}
      <header className="nova-top-nav">
        <div className="nav-brand">
          <div className="brand-logo-gem"></div>
          <div className="brand-text">
            <span className="brand-title">NOVA</span>
            <span className="brand-subtitle">OPERATIONAL VIRTUAL ASSISTANT</span>
          </div>
        </div>

        <div className="nav-controls">
          <div className={`server-status-pill ${serverOnline ? 'online' : 'offline'}`}>
            <span className="status-dot"></span>
            <span>{serverOnline ? 'CORE ONLINE' : 'CONNECTING TO CORE'}</span>
          </div>

          <button
            className="btn-history-toggle"
            onClick={() => setIsHistoryOpen(true)}
            title="Open Chat History Drawer"
          >
            <span className="history-icon">💬</span>
            <span>Previous Chat</span>
          </button>
        </div>
      </header>

      {/* Main Command Bar Area */}
      <section className="command-bar-section">
        <HeaderCommandBar
          onSendMessage={handleSendMessage}
          latestResponse={latestResponse}
          isProcessing={isProcessing}
          isSpeaking={isSpeaking}
          onToggleSpeech={handleToggleSpeech}
          speechEnabled={speechEnabled}
          onListeningStateChange={setIsListening}
        />
      </section>

      {/* Primary Dashboard Grid Layout */}
      <main className="nova-dashboard-grid">
        {/* Left / Center Zone: Animated Siri Visualizer Hero */}
        <section className="grid-hero-zone">
          <SiriVisualizer
            isSpeaking={isSpeaking}
            isListening={isListening}
            isProcessing={isProcessing}
            statusText={statusText}
          />
        </section>

        {/* Right Zone: Digital Clock & Weather Telemetry */}
        <section className="grid-telemetry-zone">
          <WeatherClockWidget
            weatherData={weatherData}
            onRefreshWeather={async () => {
              const coords = await getClientCoordinates();
              const w = await fetchWeather(coords?.lat, coords?.lon);
              setWeatherData(w);
            }}
          />
        </section>

        {/* Lower Left: Terminal Response Viewport */}
        <section className="grid-terminal-zone">
          <ResponseDisplay
            latestQuery={latestQuery}
            latestResponse={latestResponse}
            commandType={commandType}
            latestAction={latestAction}
            isProcessing={isProcessing}
          />
        </section>

        {/* Lower Right: Gemini Vision Studio */}
        <section className="grid-vision-zone">
          <VisionAnalyzer
            onSpeakingTrigger={(msg) => {
              if (speechEnabled) speakText(msg);
            }}
          />
        </section>
      </main>

      {/* Chat History Slide-out Modal / Drawer */}
      <ChatHistoryPanel
        chatHistory={chatHistory}
        onRefreshHistory={async () => {
          const h = await fetchChatHistory();
          setChatHistory(h);
        }}
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
      />
    </div>
  );
}

export default App;
