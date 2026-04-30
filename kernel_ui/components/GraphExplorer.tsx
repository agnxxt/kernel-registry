import React, { useMemo } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  Node, 
  Edge,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { TelemetryEvent } from '../hooks/useTelemetry';

interface Props {
  events: TelemetryEvent[];
}

export const GraphExplorer: React.FC<Props> = ({ events }) => {
  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = [];
    const edges: Edge[] = [];
    const agentNodes = new Set<string>();

    events.forEach((event, idx) => {
      if (!agentNodes.has(event.agent)) {
        agentNodes.add(event.agent);
        nodes.push({
          id: event.agent,
          data: { label: event.agent },
          position: { x: Math.random() * 400, y: Math.random() * 400 },
          style: { 
            background: '#1e293b', 
            color: '#fff', 
            border: '1px solid #3b82f6',
            borderRadius: '8px',
            fontSize: '12px',
            width: 120
          },
        });
      }

      const actionId = `action-${event.action_id.slice(0, 8)}`;
      nodes.push({
        id: actionId,
        data: { label: event.pathway },
        position: { x: Math.random() * 400, y: Math.random() * 400 },
        style: { 
          background: event.pathway?.includes('Slow') ? '#4c1d95' : '#1e3a8a', 
          color: '#fff', 
          borderRadius: '4px',
          fontSize: '10px',
          width: 100
        },
      });

      edges.push({
        id: `e-${event.agent}-${actionId}`,
        source: event.agent,
        target: actionId,
        label: 'executes',
        style: { stroke: '#475569' },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#475569' },
      });
    });

    return { nodes, edges };
  }, [events]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl h-full relative overflow-hidden">
      <div className="absolute top-4 left-6 z-10">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          Knowledge Graph Explorer
        </h2>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        colorMode="dark"
        fitView
      >
        <Background color="#334155" gap={20} />
        <Controls />
      </ReactFlow>
    </div>
  );
};
