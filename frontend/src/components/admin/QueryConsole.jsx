import { useState } from 'react';
import { Play, Download, Trash2, BookOpen, Clock } from 'lucide-react';
import { cn } from '../../lib/utils';
import { executeNeo4jQuery } from '../../lib/api';

/**
 * QueryConsole Component
 * 
 * Cypher query console for Neo4j database:
 * - Execute custom Cypher queries
 * - View results in table format
 * - Example queries for quick testing
 * - Query history
 * - Export results to JSON
 * 
 * @returns {JSX.Element} Query console
 */
const QueryConsole = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  // Example queries
  const exampleQueries = [
    {
      name: 'Count all nodes',
      query: 'MATCH (n) RETURN count(n) as total_nodes',
    },
    {
      name: 'Count all relationships',
      query: 'MATCH ()-[r]->() RETURN count(r) as total_relationships',
    },
    {
      name: 'List node labels',
      query: 'MATCH (n) RETURN DISTINCT labels(n) as labels, count(n) as count ORDER BY count DESC LIMIT 10',
    },
    {
      name: 'List relationship types',
      query: 'MATCH ()-[r]->() RETURN DISTINCT type(r) as type, count(r) as count ORDER BY count DESC LIMIT 10',
    },
    {
      name: 'Show recent entities',
      query: 'MATCH (n) RETURN n LIMIT 25',
    },
  ];

  // Execute query
  const handleExecute = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const data = await executeNeo4jQuery(query);
      setResults(data);
      
      // Add to history (keep last 10)
      setHistory(prev => [
        { query, timestamp: new Date(), success: true },
        ...prev.slice(0, 9)
      ]);
    } catch (err) {
      console.error('Query failed:', err);
      setError(err.message || 'Query execution failed');
      setResults(null);
      
      // Add failed query to history
      setHistory(prev => [
        { query, timestamp: new Date(), success: false, error: err.message },
        ...prev.slice(0, 9)
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Load example query
  const loadExample = (exampleQuery) => {
    setQuery(exampleQuery);
    setError(null);
  };

  // Clear results
  const clearResults = () => {
    setResults(null);
    setError(null);
  };

  // Export results
  const exportResults = () => {
    if (!results) return;

    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `neo4j-query-results-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      {/* Query Input */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium text-gray-700">Cypher Query</label>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setQuery('')}
              className="text-xs text-gray-600 hover:text-gray-900"
            >
              Clear
            </button>
          </div>
        </div>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="MATCH (n) RETURN n LIMIT 25"
          rows={6}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleExecute}
          disabled={loading || !query.trim()}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
            "bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        >
          <Play className="h-4 w-4" />
          {loading ? 'Executing...' : 'Execute Query'}
        </button>

        {results && (
          <>
            <button
              onClick={exportResults}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
            <button
              onClick={clearResults}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
            >
              <Trash2 className="h-4 w-4" />
              Clear
            </button>
          </>
        )}
      </div>

      {/* Example Queries */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <BookOpen className="h-4 w-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Example Queries</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              onClick={() => loadExample(example.query)}
              className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-xs font-medium text-gray-700 transition-colors"
            >
              {example.name}
            </button>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700 font-medium">Query Error:</p>
          <p className="text-sm text-red-600 mt-1 font-mono">{error}</p>
        </div>
      )}

      {/* Results Display */}
      {results && (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
            <h4 className="text-sm font-semibold text-gray-900">
              Query Results
              {results.records && (
                <span className="ml-2 text-gray-600 font-normal">
                  ({results.records.length} records)
                </span>
              )}
            </h4>
            {results.summary && (
              <p className="text-xs text-gray-600 mt-1">
                Execution time: {results.summary.executionTime || 'N/A'}
              </p>
            )}
          </div>
          <div className="max-h-96 overflow-auto">
            {results.records && results.records.length > 0 ? (
              <table className="w-full text-sm">
                <thead className="bg-gray-100 sticky top-0">
                  <tr>
                    {Object.keys(results.records[0]).map((key) => (
                      <th key={key} className="px-4 py-2 text-left font-medium text-gray-700 border-b border-gray-200">
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.records.map((record, idx) => (
                    <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                      {Object.values(record).map((value, vIdx) => (
                        <td key={vIdx} className="px-4 py-2 text-gray-900 font-mono text-xs">
                          {typeof value === 'object' 
                            ? JSON.stringify(value, null, 2)
                            : String(value)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-gray-500">
                No results returned
              </div>
            )}
          </div>
        </div>
      )}

      {/* Query History */}
      {history.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Recent Queries</span>
          </div>
          <div className="space-y-2">
            {history.slice(0, 5).map((item, index) => (
              <div
                key={index}
                className={cn(
                  "p-3 rounded-lg border cursor-pointer hover:bg-gray-50 transition-colors",
                  item.success ? "border-gray-200" : "border-red-200 bg-red-50"
                )}
                onClick={() => loadExample(item.query)}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-xs font-mono text-gray-700 flex-1 line-clamp-2">
                    {item.query}
                  </p>
                  <span className="text-xs text-gray-500 whitespace-nowrap">
                    {item.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                {!item.success && item.error && (
                  <p className="text-xs text-red-600 mt-1">Error: {item.error}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryConsole;

