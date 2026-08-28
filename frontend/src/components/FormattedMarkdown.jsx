import React from 'react';

/**
 * Format inline markdown tokens (bold, italics, code) into React elements.
 */
function formatInlineText(text) {
  if (!text) return '';

  const parts = [];
  // Regex to match ***bold italic***, **bold**, *italic*, and `code`
  const regex = /(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;

  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }

    const token = match[0];
    if (token.startsWith('***') && token.endsWith('***')) {
      parts.push(
        <strong key={match.index} className="md-bold">
          <em>{token.slice(3, -3)}</em>
        </strong>
      );
    } else if (token.startsWith('**') && token.endsWith('**')) {
      parts.push(
        <strong key={match.index} className="md-bold">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('*') && token.endsWith('*')) {
      parts.push(
        <em key={match.index} className="md-italic">
          {token.slice(1, -1)}
        </em>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(
        <code key={match.index} className="md-inline-code">
          {token.slice(1, -1)}
        </code>
      );
    }

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}

/**
 * Render multi-line markdown text with natural, human-styled modern typography.
 */
export default function FormattedMarkdown({ content, className = '' }) {
  if (!content) return null;

  const lines = content.split('\n');

  return (
    <div className={`formatted-markdown-block ${className}`}>
      {lines.map((rawLine, index) => {
        const line = rawLine.trim();

        if (!line) {
          return <div key={index} className="md-empty-gap" />;
        }

        // Horizontal dividers
        if (line === '---' || line === '***' || line === '___') {
          return <hr key={index} className="md-divider" />;
        }

        // Section Title: e.g. "### 1. Description of Key Elements" or "1. Description of Key Elements"
        const sectionMatch = line.match(/^(?:#{1,4}\s*)?(\d+)\.\s+([A-Z][a-zA-Z0-9\s&/\-_,]+):?$/);
        if (sectionMatch) {
          const num = sectionMatch[1];
          const title = sectionMatch[2];
          return (
            <div key={index} className="md-section-header">
              <span className="md-section-number">{num}.</span>
              <span className="md-section-text">{title}</span>
            </div>
          );
        }

        // Heading 1 (#)
        if (line.startsWith('# ')) {
          const headingText = line.replace(/^#\s+/, '');
          return (
            <h2 key={index} className="md-heading md-h1">
              {formatInlineText(headingText)}
            </h2>
          );
        }

        // Heading 2 (##)
        if (line.startsWith('## ')) {
          const headingText = line.replace(/^##\s+/, '');
          return (
            <h3 key={index} className="md-heading md-h2">
              {formatInlineText(headingText)}
            </h3>
          );
        }

        // Heading 3 (###)
        if (line.startsWith('### ')) {
          const headingText = line.replace(/^###\s+/, '');
          return (
            <h4 key={index} className="md-heading md-h3">
              {formatInlineText(headingText)}
            </h4>
          );
        }

        // Bullet list item (*, -, +, •)
        const bulletMatch = line.match(/^(\*|\-|\+|\•)\s+(.*)$/);
        if (bulletMatch) {
          return (
            <div key={index} className="md-list-item">
              <span className="md-bullet-symbol">•</span>
              <span className="md-list-text">{formatInlineText(bulletMatch[2])}</span>
            </div>
          );
        }

        // Numbered list item (e.g. "1. Item")
        const numberedMatch = line.match(/^(\d+)\.\s+(.*)$/);
        if (numberedMatch) {
          return (
            <div key={index} className="md-list-item numbered">
              <span className="md-number-bullet">{numberedMatch[1]}.</span>
              <span className="md-list-text">{formatInlineText(numberedMatch[2])}</span>
            </div>
          );
        }

        // Standard Paragraph
        return (
          <p key={index} className="md-paragraph">
            {formatInlineText(rawLine)}
          </p>
        );
      })}
    </div>
  );
}
