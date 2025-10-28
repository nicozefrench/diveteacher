/**
 * Footer Component
 * System info and status
 */

import { useState, useEffect } from 'react';
import { checkHealth } from '@/lib/api';
import { Activity, AlertCircle } from 'lucide-react';

export function Footer() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const status = await checkHealth();
        setHealth(status);
      } catch (error) {
        console.error('Health check failed:', error);
        setHealth({ status: 'unhealthy' });
      } finally {
        setLoading(false);
      }
    };
    
    fetchHealth();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <footer className="dive-footer">
      <div className="dive-container flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span>© 2025 DiveTeacher</span>
          <span className="text-gray-400">·</span>
          <span>AI-Powered Diving Education</span>
        </div>
        
        <div className="flex items-center gap-2">
          {loading ? (
            <span className="text-gray-400 text-sm">Checking status...</span>
          ) : health?.status === 'healthy' ? (
            <>
              <Activity className="text-green-500" size={16} />
              <span className="text-sm text-green-600 font-medium">
                System Operational
              </span>
            </>
          ) : (
            <>
              <AlertCircle className="text-red-500" size={16} />
              <span className="text-sm text-red-600 font-medium">
                System Unavailable
              </span>
            </>
          )}
        </div>
      </div>
    </footer>
  );
}

