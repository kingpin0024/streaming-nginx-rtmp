import React, { useEffect, useRef, useState } from 'react';
import ReactPlayer from 'react-player';
import dashjs from 'dashjs';

const DashPlayer = ({ url }) => {
  const playerRef = useRef(null);
  const [player, setPlayer] = useState(null);
  const [qualities, setQualities] = useState([]);
  const [currentQuality, setCurrentQuality] = useState(null);

  useEffect(() => {
    if (playerRef.current) {
      const dashPlayer = dashjs.MediaPlayer().create();
      
      dashPlayer.initialize(
        playerRef.current.getInternalPlayer(),
        url,
        true
      );

      // Configure automatic quality switching and low latency
      dashPlayer.updateSettings({
        'streaming': {
          'lowLatencyEnabled': true,
          'liveDelay': 3,
          'liveCatchUpMinDrift': 0.05,
          'liveCatchUpPlaybackRate': 0.5,
          'abr': {
            'autoSwitchBitrate': {
              'video': true,
              'audio': true
            },
            'initialBitrate': {
              'video': 5000,
              'audio': 128
            },
            'maxBitrate': {
              'video': 12000,
              'audio': 128
            }
          }
        }
      });

      // Log quality changes
      dashPlayer.on('qualityChangeRendered', (e) => {
        console.log('Quality changed:', {
          mediaType: e.mediaType,
          oldQuality: e.oldQuality,
          newQuality: e.newQuality
        });
        if (e.mediaType === 'video') {
          setCurrentQuality(e.newQuality);
        }
      });

      // Get available qualities
      dashPlayer.on('streamInitialized', () => {
        const availableQualities = dashPlayer.getBitrateInfoListFor('video');
        setQualities(availableQualities);
        setCurrentQuality(dashPlayer.getQualityFor('video'));
      });

      setPlayer(dashPlayer);

      return () => {
        dashPlayer.destroy();
      };
    }
  }, [url]);

  const handleQualityChange = (event) => {
    const newQuality = parseInt(event.target.value, 10);
    if (player) {
      player.setQualityFor('video', newQuality);
      setCurrentQuality(newQuality);
    }
  };

  return (
    <div style={{ 
      width: '100%', 
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center'
    }}>
      <ReactPlayer
        ref={playerRef}
        url={url}
        controls
        width="100%"
        height="100%"
        playing
        config={{
          file: {
            forceVideo: true,
            attributes: {
              crossOrigin: 'anonymous'
            }
          }
        }}
        style={{
          maxWidth: '80%',
          maxHeight: '80%'
        }}
      />
      <div style={{ marginTop: '10px' }}>
        <label htmlFor="quality-select">Quality: </label>
        <select
          id="quality-select"
          value={currentQuality}
          onChange={handleQualityChange}
          style={{ marginLeft: '5px' }}
        >
          {qualities.map((q) => (
            <option key={q.qualityIndex} value={q.qualityIndex}>
              {q.height}p ({Math.round(q.bitrate / 1000)} kbps)
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default DashPlayer;
