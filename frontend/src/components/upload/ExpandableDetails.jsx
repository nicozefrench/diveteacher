import { useState } from 'react';
import { ChevronDown, ChevronUp, Activity, FileText, Database } from 'lucide-react';
import { cn } from '../../lib/utils';
import MetricsPanel from './MetricsPanel';
import LogViewer from './LogViewer';
import Neo4jSnapshot from './Neo4jSnapshot';

/**
 * ExpandableDetails Component
 * 
 * Provides detailed monitoring for document processing with tabbed views:
 * - Metrics: Real-time processing metrics and performance stats
 * - Logs: Structured logs with filtering capabilities
 * - Neo4j: Knowledge graph statistics and entity/relation counts
 * 
 * @param {Object} props
 * @param {string} props.uploadId - Upload identifier for fetching data
 * @param {Object} props.status - Current upload status object
 * @param {Object} props.metadata - Document metadata (optional)
 */
const ExpandableDetails = ({ uploadId, status, metadata = {} }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('metrics');

  // Don't show for pending or failed uploads without processing
  if (!uploadId || status?.status === 'pending') {
    return null;
  }

  const tabs = [
    { id: 'metrics', label: 'Metrics', icon: Activity },
    { id: 'logs', label: 'Logs', icon: FileText },
    { id: 'neo4j', label: 'Neo4j', icon: Database },
  ];

  return (
    <div className="mt-4 border border-gray-200 rounded-lg overflow-hidden">
      {/* Toggle Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={cn(
          "w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 transition-colors",
          "text-sm font-medium text-gray-700"
        )}
      >
        <div className="flex items-center gap-2">
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-gray-500" />
          ) : (
            <ChevronDown className="h-4 w-4 text-gray-500" />
          )}
          <span>Detailed Monitoring</span>
        </div>
        <span className="text-xs text-gray-500">
          {isExpanded ? 'Hide details' : 'Show logs, metrics & Neo4j stats'}
        </span>
      </button>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="bg-white">
          {/* Tab Navigation */}
          <div className="flex border-b border-gray-200">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors",
                    "border-b-2 -mb-px",
                    isActive
                      ? "border-primary-600 text-primary-700 bg-primary-50"
                      : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab Content */}
          <div className="p-4">
            {activeTab === 'metrics' && (
              <MetricsPanel uploadId={uploadId} status={status} metadata={metadata} />
            )}
            {activeTab === 'logs' && (
              <LogViewer uploadId={uploadId} status={status} />
            )}
            {activeTab === 'neo4j' && (
              <Neo4jSnapshot uploadId={uploadId} status={status} metadata={metadata} />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpandableDetails;

