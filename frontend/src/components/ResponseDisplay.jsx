import React from 'react';
import FormattedMarkdown from './FormattedMarkdown';

export default function ResponseDisplay({
  latestQuery,
  latestResponse,
  commandType,
  latestAction,
  isProcessing
}) {
  const handleActionClick = (e) => {
    e?.preventDefault();
    if (!latestAction) return;

    if (latestAction.protocol) {
      try {
        const iframe = document.createElement('iframe');
        iframe.style.position = 'fixed';
        iframe.style.top = '-9999px';
        iframe.style.left = '-9999px';
        iframe.style.width = '1px';
        iframe.style.height = '1px';
        iframe.src = latestAction.protocol;
        document.body.appendChild(iframe);
        setTimeout(() => {
          try { document.body.removeChild(iframe); } catch (_) {}
        }, 3000);
      } catch (_) {
        window.location.href = latestAction.protocol;
      }
    } else if (latestAction.url) {
      window.open(latestAction.url, '_blank', 'noopener,noreferrer');
    }
  };

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
                <>
                  <FormattedMarkdown content={latestResponse} />

                  {/* Interactive Action Chip for direct 1-click execution */}
                  {latestAction && (latestAction.url || latestAction.protocol) && (
                    <div className="action-button-container">
                      <button
                        type="button"
                        className="action-launch-chip"
                        onClick={handleActionClick}
                      >
                        <span className="action-icon">
                          {latestAction.url?.includes('youtube')
                            ? '▶️'
                            : latestAction.url?.includes('google')
                            ? '🔍'
                            : latestAction.url?.includes('amazon')
                            ? '🛒'
                            : '⚡'}
                        </span>
                        <span>
                          {latestAction.label ||
                            (latestAction.protocol
                              ? `Open ${latestAction.app || 'App'}`
                              : `Open Link`)}
                        </span>
                        <span className="action-arrow">↗</span>
                      </button>
                    </div>
                  )}
                </>
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
