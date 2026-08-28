import React from 'react';

export default function SiriVisualizer({ isSpeaking, isListening, isProcessing, statusText }) {
  const getOrbStateClass = () => {
    if (isListening) return 'state-listening';
    if (isSpeaking) return 'state-speaking';
    if (isProcessing) return 'state-processing';
    return 'state-idle';
  };

  return (
    <div className="siri-visualizer-container">
      <div className={`orb-wrapper ${getOrbStateClass()}`}>
        {/* Animated Radial Pulse Rings */}
        <div className="pulse-aura aura-outer"></div>
        <div className="pulse-aura aura-mid"></div>
        <div className="pulse-aura aura-inner"></div>

        {/* Central Siri Visualizer Image */}
        <div className="siri-gif-frame">
          <img
            src="/Sirifinal.gif"
            alt="NOVA Core Visualizer"
            className="siri-gif-img"
            onError={(e) => {
              // Fallback to animated SVG orb if GIF fails
              e.target.style.display = 'none';
            }}
          />
          {/* Cybernetic fallback orb graphic */}
          <div className="cyber-core-orb"></div>
        </div>
      </div>

      <div className="visualizer-status-badge">
        <span className={`status-indicator-dot ${getOrbStateClass()}`}></span>
        <span className="status-text">{statusText || 'NOVA is ready and listening.'}</span>
      </div>
    </div>
  );
}
