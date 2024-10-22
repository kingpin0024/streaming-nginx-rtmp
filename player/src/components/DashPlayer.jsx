import React, { useEffect, useRef } from 'react';
import ReactPlayer from 'react-player';
import dashjs from 'dashjs';

const DashPlayer = ({ url }) => {
  const playerRef = useRef(null);

  useEffect(() => {
    if (playerRef.current) {
      const player = dashjs.MediaPlayer().create();
      
      player.initialize(
        playerRef.current.getInternalPlayer(),
        url,
        true
      );

      // Configure automatic quality switching and low latency
      player.updateSettings({
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
      player.on('qualityChangeRendered', (e) => {
        console.log('Quality changed:', {
          mediaType: e.mediaType,
          oldQuality: e.oldQuality,
          newQuality: e.newQuality
        });
      });

      return () => {
        player.destroy();
      };
    }
  }, [url]);

  return (
    <div style={{ 
      width: '100%', 
      height: '100%',
      display: 'flex',
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
          maxWidth: '100%',
          maxHeight: '100%'
        }}
      />
    </div>
  );
};

export default DashPlayer;