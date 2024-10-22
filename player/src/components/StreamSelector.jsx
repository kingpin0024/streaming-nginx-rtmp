

// src/components/StreamSelector.jsx
import React, { useState } from 'react';

const StreamSelector = ({ onStreamSelect }) => {
  const [customUrl, setCustomUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (customUrl) {
      onStreamSelect(customUrl);
    }
  };

  return (
    <div style={{ marginBottom: '20px' }}>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={customUrl}
          onChange={(e) => setCustomUrl(e.target.value)}
          placeholder="Enter DASH stream URL"
          style={{ width: '300px', padding: '8px', marginRight: '10px' }}
        />
        <button type="submit">Load Stream</button>
      </form>
    </div>
  );
};

export default StreamSelector;