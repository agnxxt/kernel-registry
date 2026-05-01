import { useState, useEffect } from 'react';

export function useTelemetry(url: string) {
  const [events, setEvents] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Resolve dynamic WebSocket URL if none provided or if it is localhost:8000 but we are on a different host
    let wsUrl = url;
    if (typeof window !== 'undefined') {
        if (wsUrl.includes('localhost:8000') && window.location.hostname !== 'localhost') {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            wsUrl = protocol + "//" + host + "/ws/telemetry";
        }
    }

    const socket = new WebSocket(wsUrl);

    socket.onopen = () => setIsConnected(true);
    socket.onclose = () => setIsConnected(false);
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents((prev) => [data, ...prev].slice(0, 50));
    };

    return () => socket.close();
  }, [url]);

  return { events, isConnected };
}
