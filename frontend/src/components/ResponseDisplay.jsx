import React from 'react';

export default function ResponseDisplay({ latestQuery, latestResponse, commandType, isProcessing }) {
  return (
    <div className="response-display-panel">
      <div className="panel-header">
        <div className="panel-title-wrap">
          <span className="terminal-dot"></span>
          <span className="panel-title">TERMINAL OUTPUT</span>
        </div>
        {commandType && (
          <span className="command-type-pill">{commandType.toUpperCase()}</span>
        )}
      </div>

      <div className="terminal-content">
        {latestQuery && (
          <div className="query-row">
            <span className="prompt-label">USER &gt;</span>
            <span className="query-text">{latestQuery}</span>
          </div>
        )}

        <div className="response-body">
          <span className="prompt-label assistant">NOVA &gt;</span>
          {isProcessing ? (
            <div className="processing-state">
              <span className="typing-cursor"></span>
              <span className="processing-text">Synthesizing intelligence...</span>
            </div>
          ) : (
            <div className="response-text-content">
              {latestResponse ? (
                latestResponse.split('\n').map((line, idx) => (
                  <p key={idx} className="response-line">
                    {line}
                  </p>
                ))
              ) : (
                <p className="placeholder-text">
                  Welcome to NOVA. Type a command or press the microphone to interact.
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
