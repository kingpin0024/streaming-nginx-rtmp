import { useCallback } from 'react';

export const useStreamQuality = () => {
  const onQualityChange = useCallback((e) => {
    console.log('Quality changed:', e);
    // You can add your own logic here to handle quality changes
  }, []);

  return { onQualityChange };
};