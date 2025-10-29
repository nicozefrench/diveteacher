import { useState, useEffect } from 'react';
import { Database, Download, Trash2, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import { cn } from '../../lib/utils';
import { getNeo4jStats, exportNeo4jData, clearNeo4jDatabase } from '../../lib/api';
import ConfirmationModal from '../ui/ConfirmationModal';

/**
 * Neo4jManagementPanel Component
 * 
 * Provides Neo4j database management tools:
 * - Real-time statistics (nodes, relationships, density)
 * - Export database (JSON format)
 * - Clear database (with confirmation)
 * - Connection health check
 * 
 * @returns {JSX.Element} Neo4j management panel
 */
const Neo4jManagementPanel = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isExporting, setIsExporting] = useState(false);
  const [showClearModal, setShowClearModal] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  // Fetch stats
  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await getNeo4jStats();
      setStats(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch Neo4j stats:', err);
      setError('Failed to load database statistics');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchStats();
  }, []);

  // Handle export
  const handleExport = async () => {
    try {
      setIsExporting(true);
      const data = await exportNeo4jData();
      
      // Create download link
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `neo4j-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export database:', err);
      alert('Failed to export database: ' + err.message);
    } finally {
      setIsExporting(false);
    }
  };

  // Handle clear (with confirmation)
  const handleClear = async (confirmationCode) => {
    try {
      setIsClearing(true);
      await clearNeo4jDatabase(confirmationCode);
      setShowClearModal(false);
      // Refresh stats after clearing
      await fetchStats();
      alert('Database cleared successfully');
    } catch (err) {
      console.error('Failed to clear database:', err);
      alert('Failed to clear database: ' + err.message);
    } finally {
      setIsClearing(false);
    }
  };

  // Stat card
  const StatCard = ({ label, value, icon: Icon, color = 'blue' }) => (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <div className={cn("p-2 rounded-lg", `bg-${color}-100`)}>
        <Icon className={cn("h-5 w-5", `text-${color}-600`)} />
      </div>
      <div>
        <p className="text-xs text-gray-600">{label}</p>
        <p className="text-xl font-bold text-gray-900">
          {value !== undefined && value !== null ? value.toLocaleString() : '–'}
        </p>
      </div>
    </div>
  );

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-3" />
        <p className="text-sm text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchStats}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  const totalNodes = stats?.nodes?.total || 0;
  const totalRelationships = stats?.relationships?.total || 0;
  const graphDensity = totalNodes > 0 ? (totalRelationships / totalNodes).toFixed(2) : 0;

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold text-gray-700">Database Statistics</h4>
          <button
            onClick={fetchStats}
            disabled={loading}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
            title="Refresh statistics"
          >
            <RefreshCw className={cn("h-4 w-4 text-gray-600", loading && "animate-spin")} />
          </button>
        </div>

        <div className="grid grid-cols-1 gap-3">
          <StatCard
            icon={Database}
            label="Total Nodes"
            value={totalNodes}
            color="green"
          />
          <StatCard
            icon={Database}
            label="Total Relationships"
            value={totalRelationships}
            color="purple"
          />
          <StatCard
            icon={Database}
            label="Graph Density"
            value={graphDensity}
            color="blue"
          />
        </div>
      </div>

      {/* Connection Status */}
      <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
        <CheckCircle className="h-5 w-5 text-green-600" />
        <div className="flex-1 text-sm">
          <span className="font-medium text-green-900">Connected</span>
          {stats?.database?.version && (
            <span className="text-green-700 ml-2">Neo4j v{stats.database.version}</span>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-2">
        <h4 className="text-sm font-semibold text-gray-700">Management Actions</h4>
        
        {/* Export Button */}
        <button
          onClick={handleExport}
          disabled={isExporting || totalNodes === 0}
          className={cn(
            "w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors",
            "bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          <Download className="h-4 w-4" />
          {isExporting ? 'Exporting...' : 'Export Database (JSON)'}
        </button>

        {/* Clear Button (Dangerous) */}
        <button
          onClick={() => setShowClearModal(true)}
          disabled={isClearing || totalNodes === 0}
          className={cn(
            "w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors",
            "bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          <Trash2 className="h-4 w-4" />
          Clear Database
        </button>

        {totalNodes === 0 && (
          <p className="text-xs text-gray-500 text-center mt-2">
            Database is empty
          </p>
        )}
      </div>

      {/* Confirmation Modal */}
      {showClearModal && (
        <ConfirmationModal
          title="Clear Database"
          message={`This will permanently delete ALL ${totalNodes.toLocaleString()} nodes and ${totalRelationships.toLocaleString()} relationships. This action CANNOT be undone.`}
          confirmationCode="DELETE_ALL_DATA"
          onConfirm={handleClear}
          onCancel={() => setShowClearModal(false)}
          isProcessing={isClearing}
          variant="danger"
        />
      )}
    </div>
  );
};

export default Neo4jManagementPanel;

