import { useState, useEffect, useCallback } from 'react';

export interface TelemetryEvent {
  event: string;
  agent: string;
  action_id: string;
  pathway: string;
  theories: string[];
  trust_score: number;
  historical_reliability?: number;
  timestamp: string;
}

export const useTelemetry = (url: string) => {
  const [events, setEvents] = useState<TelemetryEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const socket = new WebSocket(url);

    socket.onopen = () => setIsConnected(true);
    socket.onclose = () => setIsConnected(false);
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents((prev) => [
        { ...data, timestamp: new Date().toLocaleTimeString() },
        ...prev.slice(0, 49) // Keep last 50 events
      ]);
    };

    return () => socket.close();
  }, [url]);

  return { events, isConnected };
};
