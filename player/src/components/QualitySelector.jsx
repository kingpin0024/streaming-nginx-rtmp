import React, { useState } from 'react';
import '../styles/QualitySelector.css';

const QualitySelector = ({ qualities, currentQuality, autoQuality, onQualityChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const getCurrentQualityLabel = () => {
    if (autoQuality) return 'Auto';
    const quality = qualities.find(q => q.id === currentQuality);
    return quality ? quality.label : 'Unknown';
  };

  return (
    <div className="quality-selector">
      <button 
        className="quality-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="quality-icon">HD</span>
        <span className="current-quality">{getCurrentQualityLabel()}</span>
      </button>
      
      {isOpen && (
        <div className="quality-menu">
          <div 
            className={`quality-option ${autoQuality ? 'active' : ''}`}
            onClick={() => {
              onQualityChange('auto');
              setIsOpen(false);
            }}
          >
            Auto
          </div>
          {qualities.map((quality) => (
            <div
              key={quality.id}
              className={`quality-option ${!autoQuality && currentQuality === quality.id ? 'active' : ''}`}
              onClick={() => {
                onQualityChange(quality.id);
                setIsOpen(false);
              }}
            >
              {quality.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default QualitySelector;
