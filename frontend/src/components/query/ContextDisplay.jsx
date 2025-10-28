/**
 * ContextDisplay Component
 * Shows retrieved facts from knowledge graph
 */

import { Database } from 'lucide-react';
import { Card } from '@/components/ui/Card';

export function ContextDisplay({ facts }) {
  if (!facts || facts.length === 0) {
    return null;
  }
  
  return (
    <Card className="mb-4">
      <div className="flex items-start gap-3">
        <Database className="text-dive-primary flex-shrink-0 mt-1" size={20} />
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 mb-2">
            Knowledge Graph Context
          </h4>
          <div className="space-y-2">
            {facts.map((fact, idx) => (
              <div 
                key={idx} 
                className="text-sm text-gray-700 pl-4 border-l-2 border-dive-secondary"
              >
                {fact}
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}

