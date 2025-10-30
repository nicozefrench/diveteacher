import { useMemo } from 'react';

/**
 * EntityBreakdown Component
 * 
 * Displays entity type distribution from Neo4j graph.
 * Extracted as separate component to avoid React Hooks violations (Fix #18).
 * 
 * Previously defined inside Neo4jSnapshot, which caused hook count violations
 * when conditional rendering was applied. Now as a separate component,
 * the hook count is stable within Neo4jSnapshot.
 * 
 * @param {Object} entities - Entity counts by type from Neo4j stats
 */
export default function EntityBreakdown({ entities }) {
  // ✅ Hook ALWAYS called at top level (React Hooks Rule #1)
  const { sortedEntities, total } = useMemo(() => {
    // Conditional logic INSIDE hook (correct pattern)
    if (!entities || Object.keys(entities).length === 0) {
      return { sortedEntities: [], total: 0 };
    }
    
    const sorted = Object.entries(entities)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10); // Top 10 entity types
    const totalCount = Object.values(entities).reduce((sum, count) => sum + count, 0);
    
    return { sortedEntities: sorted, total: totalCount };
  }, [entities]);

  // ✅ Early return AFTER all hooks (React Hooks Rule #2)
  if (sortedEntities.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      <h5 className="text-sm font-medium text-gray-700 mb-3">Entity Types</h5>
      {sortedEntities.map(([type, count]) => {
        const percentage = total > 0 ? (count / total) * 100 : 0;
        
        return (
          <div key={type} className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="text-gray-700 truncate">{type}</span>
              <span className="font-medium text-gray-900">
                {count} ({percentage.toFixed(1)}%)
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

