import React from 'react';
import DashPlayer from './components/DashPlayer';

const STREAM_URL = 'https://streaming.convay.com/dash/stream.mpd';

const App = () => {
  return (
    <div style={{ 
      width: '100vw', 
      height: '100vh', 
      margin: 0, 
      padding: 0, 
      overflow: 'hidden',
      backgroundColor: '#000'
    }}>
      <DashPlayer url={STREAM_URL} />
    </div>
  );
};

export default App;

