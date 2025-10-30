import { useMemo } from 'react';

/**
 * RelationshipBreakdown Component
 * 
 * Displays relationship type distribution from Neo4j graph.
 * Extracted as separate component to avoid React Hooks violations (Fix #18).
 * 
 * Previously defined inside Neo4jSnapshot, which caused hook count violations
 * when conditional rendering was applied. Now as a separate component,
 * the hook count is stable within Neo4jSnapshot.
 * 
 * @param {Object} relationships - Relationship counts by type from Neo4j stats
 */
export default function RelationshipBreakdown({ relationships }) {
  // ✅ Hook ALWAYS called at top level (React Hooks Rule #1)
  const { sortedRelationships, total } = useMemo(() => {
    // Conditional logic INSIDE hook (correct pattern)
    if (!relationships || Object.keys(relationships).length === 0) {
      return { sortedRelationships: [], total: 0 };
    }
    
    const sorted = Object.entries(relationships)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10); // Top 10 relationship types
    const totalCount = Object.values(relationships).reduce((sum, count) => sum + count, 0);
    
    return { sortedRelationships: sorted, total: totalCount };
  }, [relationships]);

  // ✅ Early return AFTER all hooks (React Hooks Rule #2)
  if (sortedRelationships.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      <h5 className="text-sm font-medium text-gray-700 mb-3">Relationship Types</h5>
      {sortedRelationships.map(([type, count]) => {
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
                className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

