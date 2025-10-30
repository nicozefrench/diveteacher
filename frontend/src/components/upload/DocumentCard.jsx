import React, { useState } from 'react';
import DocumentHeader from './DocumentHeader';
import { ChevronDown, ChevronRight } from 'lucide-react';

export default function DocumentCard({ document, onRetry }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('metrics');

  // 🔍 DEBUG: Phase 1 Investigation - Track props received
  console.log(`[DocumentCard] Rendering for ${document.id}:`, {
    timestamp: new Date().toISOString(),
    status: document.status,
    metrics: JSON.parse(JSON.stringify(document.metrics || {})),
    metadata: JSON.parse(JSON.stringify(document.metadata || {})),
    metrics_entities: document.metrics?.entities,
    metrics_relations: document.metrics?.relations,
    metadata_entities: document.metadata?.entities,
    metadata_relations: document.metadata?.relations
  });

  // Import tabs dynamically to avoid circular dependencies
  const MetricsPanel = React.lazy(() => import('./MetricsPanel'));
  const LogViewer = React.lazy(() => import('./LogViewer'));
  const Neo4jSnapshot = React.lazy(() => import('./Neo4jSnapshot'));

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-all bg-white">
      {/* Compact Header - Always Visible */}
      <div 
        className="flex items-center justify-between p-4 hover:bg-gray-50 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <DocumentHeader document={document} />
        
        <button 
          className="text-gray-400 hover:text-gray-600 flex-shrink-0 ml-4"
          aria-label={isExpanded ? "Collapse" : "Expand"}
        >
          {isExpanded ? (
            <ChevronDown className="w-5 h-5" />
          ) : (
            <ChevronRight className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Collapsible Monitoring Panel */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50">
          <div className="px-4 py-3">
            {/* Tab Navigation */}
            <div className="flex gap-2 mb-4 border-b border-gray-200">
              <button
                onClick={(e) => { e.stopPropagation(); setActiveTab('metrics'); }}
                className={`px-4 py-2 font-medium text-sm transition-colors ${
                  activeTab === 'metrics'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Metrics
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); setActiveTab('logs'); }}
                className={`px-4 py-2 font-medium text-sm transition-colors ${
                  activeTab === 'logs'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Logs
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); setActiveTab('neo4j'); }}
                className={`px-4 py-2 font-medium text-sm transition-colors ${
                  activeTab === 'neo4j'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Neo4j
              </button>
            </div>

            {/* Tab Content */}
            <React.Suspense fallback={<div className="text-center py-4 text-gray-500">Loading...</div>}>
              {activeTab === 'metrics' && (
                <MetricsPanel 
                  document={document}
                  status={document.status}
                  metrics={document.metrics}
                  metadata={document.metadata}
                />
              )}
              {activeTab === 'logs' && (
                <LogViewer uploadId={document.id} />
              )}
              {activeTab === 'neo4j' && (
                <Neo4jSnapshot uploadId={document.id} />
              )}
            </React.Suspense>
          </div>
        </div>
      )}
    </div>
  );
}

