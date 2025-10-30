import { useState, useEffect, useMemo } from 'react';
import { Database, GitFork, Layers, TrendingUp, RefreshCw, AlertCircle } from 'lucide-react';
import { cn } from '../../lib/utils';
import { getNeo4jStats } from '../../lib/api';
import EntityBreakdown from './EntityBreakdown';
import RelationshipBreakdown from './RelationshipBreakdown';

/**
 * Neo4jSnapshot Component
 * 
 * Displays knowledge graph statistics from Neo4j:
 * - Total nodes and relationships
 * - Entity breakdown by type
 * - Relationship breakdown by type
 * - Graph density metrics
 * - Real-time updates during processing
 * 
 * Optimized with useMemo for computed values
 * 
 * @param {Object} props
 * @param {string} props.uploadId - Upload identifier
 * @param {Object} props.status - Current upload status
 * @param {Object} props.metadata - Document metadata
 */
const Neo4jSnapshot = ({ uploadId, status, metadata = {} }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch Neo4j stats
  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await getNeo4jStats();
      setStats(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch Neo4j stats:', err);
      setError('Failed to load Neo4j statistics');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchStats();
  }, []);

  // Auto-refresh (every 5 seconds while processing)
  useEffect(() => {
    if (!autoRefresh || status?.status !== 'processing') {
      return;
    }

    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh, status?.status]);

  // FIX #20: Memoize calculated stats BEFORE early returns
  // This ensures hooks are called in the same order on every render
  // Previously, useMemo was after early returns, causing hook order to change
  const { totalNodes, totalRelationships, graphDensity } = useMemo(() => {
    // Robust null checks to prevent crashes with empty/undefined stats
    if (!stats) {
      return { totalNodes: 0, totalRelationships: 0, graphDensity: '0.00' };
    }
    
    const nodes = stats?.nodes?.total || 0;
    const relationships = stats?.relationships?.total || 0;
    
    // Prevent division by zero and ensure string return for display
    const density = nodes > 0 ? (relationships / nodes).toFixed(2) : '0.00';
    
    return { totalNodes: nodes, totalRelationships: relationships, graphDensity: density };
  }, [stats]);

  // Stat card component
  const StatCard = ({ icon: Icon, label, value, color = 'blue', subtext }) => (
    <div className={cn(
      "flex items-start gap-3 p-4 rounded-lg border",
      `bg-${color}-50 border-${color}-200`
    )}>
      <div className={cn("p-2 rounded-lg", `bg-${color}-100`)}>
        <Icon className={cn("h-6 w-6", `text-${color}-600`)} />
      </div>
      <div className="flex-1">
        <p className="text-sm text-gray-600">{label}</p>
        <p className="text-3xl font-bold text-gray-900 mt-1">
          {value !== undefined && value !== null ? value.toLocaleString() : '–'}
        </p>
        {subtext && (
          <p className="text-xs text-gray-500 mt-1">{subtext}</p>
        )}
      </div>
    </div>
  );

  // Early returns are now AFTER all hooks (useState, useEffect, useMemo)
  // This ensures consistent hook order on every render
  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center gap-3 text-gray-500">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <span>Loading Neo4j statistics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-3" />
          <p className="text-sm text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchStats}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold text-gray-900">Knowledge Graph Statistics</h4>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={cn(
              "flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
              autoRefresh
                ? "bg-primary-100 text-primary-700 hover:bg-primary-200"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            )}
          >
            <RefreshCw className={cn("h-3 w-3", autoRefresh && "animate-spin")} />
            {autoRefresh ? 'Auto' : 'Manual'}
          </button>
          <button
            onClick={fetchStats}
            disabled={loading}
            className="p-1.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
          </button>
        </div>
      </div>

      {/* 🔧 FIX: Empty state when no data available yet */}
      {stats && totalNodes === 0 && totalRelationships === 0 && (
        <div className="flex items-center justify-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
          <div className="text-center">
            <Database className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-900 mb-1">No Graph Data Yet</p>
            <p className="text-xs text-gray-500 max-w-sm mx-auto">
              {status?.status === 'processing' 
                ? 'Knowledge graph will be populated once processing completes...'
                : 'Upload a document to build the knowledge graph'}
            </p>
          </div>
        </div>
      )}

      {/* Overview Stats - Only show if we have data */}
      {stats && (totalNodes > 0 || totalRelationships > 0) && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard
              icon={Layers}
              label="Total Nodes"
              value={totalNodes}
              color="green"
              subtext="Entities in graph"
            />
            <StatCard
              icon={GitFork}
              label="Total Relations"
              value={totalRelationships}
              color="purple"
              subtext="Connections between entities"
            />
            <StatCard
              icon={TrendingUp}
              label="Graph Density"
              value={graphDensity}
              color="blue"
              subtext="Avg relations per node"
            />
          </div>

          {/* Current Document Stats (if processing or recently completed) */}
          {(metadata.entities || metadata.relations) && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start gap-3">
                <Database className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h5 className="text-sm font-semibold text-blue-900 mb-2">
                    Current Document Contribution
                  </h5>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-blue-700">Entities Added:</p>
                      <p className="text-2xl font-bold text-blue-900 mt-1">
                        {metadata.entities || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-blue-700">Relations Added:</p>
                      <p className="text-2xl font-bold text-blue-900 mt-1">
                        {metadata.relations || 0}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Entity Breakdown - FIX #18: Always rendered (returns null if no data) */}
          <EntityBreakdown entities={stats?.nodes?.by_label} />

          {/* Relationship Breakdown - FIX #18: Always rendered (returns null if no data) */}
          <RelationshipBreakdown relationships={stats?.relationships?.by_type} />

          {/* Connection Status */}
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <div className="flex items-center gap-1.5">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
              <span>Connected to Neo4j</span>
            </div>
            {stats?.database?.version && (
              <>
                <span>•</span>
                <span>Neo4j v{stats.database.version}</span>
              </>
            )}
            {stats?.last_updated && (
              <>
                <span>•</span>
                <span>Updated {new Date(stats.last_updated).toLocaleTimeString()}</span>
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Neo4jSnapshot;

