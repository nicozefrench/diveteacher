import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Info, XCircle, Search, Filter, RefreshCw } from 'lucide-react';
import { cn } from '../../lib/utils';
import { getUploadLogs } from '../../lib/api';

/**
 * LogViewer Component
 * 
 * Displays structured logs for document processing with:
 * - Real-time log streaming
 * - Level filtering (INFO, WARNING, ERROR)
 * - Search/filter capabilities
 * - Auto-refresh toggle
 * 
 * @param {Object} props
 * @param {string} props.uploadId - Upload identifier
 * @param {Object} props.status - Current upload status
 */
const LogViewer = ({ uploadId, status }) => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilter, setLevelFilter] = useState('all'); // all, info, warning, error
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch logs
  const fetchLogs = async () => {
    if (!uploadId) return;

    try {
      setLoading(true);
      const data = await getUploadLogs(uploadId);
      setLogs(data.logs || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
      setError('Failed to load logs');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchLogs();
  }, [uploadId]);

  // Auto-refresh (every 3 seconds while processing)
  useEffect(() => {
    if (!autoRefresh || status?.status !== 'processing') {
      return;
    }

    const interval = setInterval(fetchLogs, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh, status?.status, uploadId]);

  // Apply filters
  useEffect(() => {
    let filtered = logs;

    // Level filter
    if (levelFilter !== 'all') {
      filtered = filtered.filter((log) => log.level?.toLowerCase() === levelFilter);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (log) =>
          log.message?.toLowerCase().includes(query) ||
          log.stage?.toLowerCase().includes(query) ||
          log.sub_stage?.toLowerCase().includes(query)
      );
    }

    setFilteredLogs(filtered);
  }, [logs, levelFilter, searchQuery]);

  // Log level icon and color
  const getLogLevelConfig = (level) => {
    const levelLower = level?.toLowerCase() || 'info';
    
    switch (levelLower) {
      case 'error':
        return {
          icon: XCircle,
          color: 'text-red-600',
          bg: 'bg-red-50',
          border: 'border-red-200',
        };
      case 'warning':
        return {
          icon: AlertCircle,
          color: 'text-yellow-600',
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
        };
      case 'success':
        return {
          icon: CheckCircle,
          color: 'text-green-600',
          bg: 'bg-green-50',
          border: 'border-green-200',
        };
      default:
        return {
          icon: Info,
          color: 'text-blue-600',
          bg: 'bg-blue-50',
          border: 'border-blue-200',
        };
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    });
  };

  if (loading && logs.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center gap-3 text-gray-500">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <span>Loading logs...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <XCircle className="h-12 w-12 text-red-500 mx-auto mb-3" />
          <p className="text-sm text-gray-600">{error}</p>
          <button
            onClick={fetchLogs}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Level Filter */}
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-500" />
          <select
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Levels</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="success">Success</option>
          </select>
        </div>

        {/* Auto-refresh Toggle */}
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          className={cn(
            "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
            autoRefresh
              ? "bg-primary-100 text-primary-700 hover:bg-primary-200"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          )}
        >
          <RefreshCw className={cn("h-4 w-4", autoRefresh && "animate-spin")} />
          {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
        </button>

        {/* Manual Refresh */}
        <button
          onClick={fetchLogs}
          disabled={loading}
          className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
        </button>
      </div>

      {/* Stats */}
      <div className="flex items-center gap-4 text-sm text-gray-600">
        <span>Total: {logs.length} logs</span>
        <span>•</span>
        <span>Showing: {filteredLogs.length}</span>
        {searchQuery && (
          <>
            <span>•</span>
            <span>Search: "{searchQuery}"</span>
          </>
        )}
      </div>

      {/* Log Entries */}
      <div className="space-y-2 max-h-[500px] overflow-y-auto">
        {filteredLogs.length === 0 ? (
          <div className="text-center py-12">
            <Info className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-sm text-gray-600">
              {searchQuery || levelFilter !== 'all' ? 'No logs match your filters' : 'No logs available yet'}
            </p>
          </div>
        ) : (
          filteredLogs.map((log, index) => {
            const config = getLogLevelConfig(log.level);
            const Icon = config.icon;

            return (
              <div
                key={index}
                className={cn(
                  "flex items-start gap-3 p-3 rounded-lg border",
                  config.bg,
                  config.border
                )}
              >
                {/* Icon & Timestamp */}
                <div className="flex flex-col items-center gap-1 flex-shrink-0">
                  <Icon className={cn("h-5 w-5", config.color)} />
                  <span className="text-xs text-gray-500 font-mono">
                    {formatTimestamp(log.timestamp)}
                  </span>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* Message */}
                  <p className="text-sm text-gray-900 break-words">
                    {log.message}
                  </p>

                  {/* Metadata */}
                  {(log.stage || log.sub_stage || log.progress !== undefined) && (
                    <div className="flex flex-wrap items-center gap-2 mt-2">
                      {log.stage && (
                        <span className="px-2 py-0.5 bg-white border border-gray-300 rounded text-xs text-gray-700">
                          {log.stage}
                        </span>
                      )}
                      {log.sub_stage && (
                        <span className="px-2 py-0.5 bg-white border border-gray-300 rounded text-xs text-gray-700">
                          {log.sub_stage}
                        </span>
                      )}
                      {log.progress !== undefined && (
                        <span className="px-2 py-0.5 bg-white border border-gray-300 rounded text-xs text-gray-700">
                          {log.progress}%
                        </span>
                      )}
                    </div>
                  )}

                  {/* Additional Data */}
                  {log.data && Object.keys(log.data).length > 0 && (
                    <details className="mt-2">
                      <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                        View details
                      </summary>
                      <pre className="mt-2 p-2 bg-white border border-gray-300 rounded text-xs overflow-x-auto">
                        {JSON.stringify(log.data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default LogViewer;

