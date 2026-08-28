import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import HeaderCommandBar from './components/HeaderCommandBar';
import SiriVisualizer from './components/SiriVisualizer';
import WeatherClockWidget from './components/WeatherClockWidget';
import ResponseDisplay from './components/ResponseDisplay';
import ChatHistoryPanel from './components/ChatHistoryPanel';
import VisionAnalyzer from './components/VisionAnalyzer';
import { fetchHealth, fetchWeather, fetchChatHistory, sendChatMessage, speakText } from './services/api';

function App() {
  const [serverOnline, setServerOnline] = useState(false);
  const [weatherData, setWeatherData] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const [latestQuery, setLatestQuery] = useState('');
  const [latestResponse, setLatestResponse] = useState('');
  const [commandType, setCommandType] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speechEnabled, setSpeechEnabled] = useState(true);
  const [statusText, setStatusText] = useState('NOVA is ready.');

  // Load telemetry & history
  const loadTelemetry = useCallback(async () => {
    const health = await fetchHealth();
    setServerOnline(health.status === 'healthy');

    const weather = await fetchWeather();
    setWeatherData(weather);

    const history = await fetchChatHistory();
    setChatHistory(history);
  }, []);

  useEffect(() => {
    loadTelemetry();
    const interval = setInterval(loadTelemetry, 30000); // 30s telemetry polling
    return () => clearInterval(interval);
  }, [loadTelemetry]);

  // Handle user commands
  const handleSendMessage = async (queryText) => {
    if (!queryText.trim()) return;

    setLatestQuery(queryText);
    setIsProcessing(true);
    setStatusText(`Processing: "${queryText}"`);

    const result = await sendChatMessage(queryText, speechEnabled);
    setIsProcessing(false);

    if (result.response) {
      setLatestResponse(result.response);
      setCommandType(result.command_type || 'general_chat');
      setStatusText(result.status === 'success' ? 'Command completed.' : 'Response received.');

      // Browser TTS fallback if server-side TTS is disabled or desktop pyttsx3 is not heard
      if (speechEnabled && 'speechSynthesis' in window && !result.response.includes('Error')) {
        setIsSpeaking(true);
        const utterance = new SpeechSynthesisUtterance(result.response);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);
        // Clean speech synthesis
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
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
            <span>{serverOnline ? 'CORE ONLINE' : 'STANDBY (CHECK SERVER.PY)'}</span>
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
              const w = await fetchWeather();
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
