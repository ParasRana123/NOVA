import React, { useState, useRef } from 'react';
import { analyzeImage } from '../services/api';

export default function VisionAnalyzer({ onSpeakingTrigger }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [analysisResult, setAnalysisResult] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setAnalysisResult('');
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile || isAnalyzing) return;

    setIsAnalyzing(true);
    setAnalysisResult('Analyzing image using Google Gemini Vision...');

    const res = await analyzeImage(selectedFile);
    setIsAnalyzing(false);

    if (res.analysis) {
      setAnalysisResult(res.analysis);
      onSpeakingTrigger?.('Image analysis complete.');
    } else {
      setAnalysisResult('No analysis generated.');
    }
  };

  const triggerUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="vision-analyzer-card">
      <div className="vision-header">
        <div className="vision-title-group">
          <span className="vision-icon">👁️</span>
          <span className="vision-title">IMAGE INTELLIGENCE (GEMINI)</span>
        </div>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/png, image/jpeg, image/jpg"
        style={{ display: 'none' }}
      />

      <div className="vision-workbench">
        {/* Upload Thumbnail Box */}
        <div className="upload-preview-box" onClick={triggerUpload} title="Click to upload image">
          {previewUrl ? (
            <img src={previewUrl} alt="Upload Preview" className="uploaded-thumbnail" />
          ) : (
            <div className="upload-placeholder">
              <span className="upload-icon-symbol">📁</span>
              <span className="upload-hint">Upload Image</span>
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div className="vision-actions">
          <button className="btn-vision upload" onClick={triggerUpload}>
            Choose Image
          </button>
          <button
            className={`btn-vision analyze ${isAnalyzing ? 'loading' : ''}`}
            onClick={handleAnalyze}
            disabled={!selectedFile || isAnalyzing}
          >
            {isAnalyzing ? 'Analyzing...' : 'Analyze Image'}
          </button>
        </div>
      </div>

      {/* Analysis Output Pane */}
      {analysisResult && (
        <div className="vision-result-container">
          <div className="result-header">Vision Analysis:</div>
          <div className="result-body">
            {analysisResult.split('\n').map((line, idx) => (
              <p key={idx} className="result-line">{line}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
