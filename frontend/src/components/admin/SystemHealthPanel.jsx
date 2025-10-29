import { useState, useEffect } from 'react';
import { Activity, Database, Cpu, HardDrive, CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { cn } from '../../lib/utils';
import { checkHealth } from '../../lib/api';

/**
 * SystemHealthPanel Component
 * 
 * Displays system health status for all services:
 * - Backend API status
 * - Neo4j database connectivity
 * - Ollama LLM service status
 * - Overall system health indicator
 * 
 * @returns {JSX.Element} System health panel
 */
const SystemHealthPanel = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);

  // Fetch health status
  const fetchHealth = async () => {
    try {
      setLoading(true);
      const data = await checkHealth();
      setHealth(data);
      setError(null);
      setLastChecked(new Date());
    } catch (err) {
      console.error('Failed to fetch health status:', err);
      setError('Failed to check system health');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchHealth();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Service status component
  const ServiceStatus = ({ name, status, icon: Icon, details }) => {
    const isHealthy = status === 'healthy' || status === 'operational';
    const isWarning = status === 'degraded' || status === 'slow';
    const isError = status === 'unhealthy' || status === 'error' || status === 'down';

    return (
      <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
        <div className={cn(
          "p-2 rounded-lg",
          isHealthy && "bg-green-100",
          isWarning && "bg-yellow-100",
          isError && "bg-red-100"
        )}>
          <Icon className={cn(
            "h-5 w-5",
            isHealthy && "text-green-600",
            isWarning && "text-yellow-600",
            isError && "text-red-600"
          )} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h5 className="text-sm font-medium text-gray-900">{name}</h5>
            {isHealthy && <CheckCircle className="h-4 w-4 text-green-600" />}
            {isWarning && <AlertCircle className="h-4 w-4 text-yellow-600" />}
            {isError && <XCircle className="h-4 w-4 text-red-600" />}
          </div>
          <p className={cn(
            "text-xs mt-0.5",
            isHealthy && "text-green-700",
            isWarning && "text-yellow-700",
            isError && "text-red-700"
          )}>
            {isHealthy && "Operational"}
            {isWarning && "Degraded Performance"}
            {isError && "Service Unavailable"}
          </p>
          {details && (
            <p className="text-xs text-gray-600 mt-1">{details}</p>
          )}
        </div>
      </div>
    );
  };

  if (loading && !health) {
    return (
      <div className="flex items-center justify-center py-12">
        <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <XCircle className="h-12 w-12 text-red-500 mx-auto mb-3" />
        <p className="text-sm text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchHealth}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  // Determine overall health
  const services = health?.services || {};
  const allHealthy = Object.values(services).every(s => s?.status === 'healthy' || s?.status === 'operational');
  const someUnhealthy = Object.values(services).some(s => s?.status === 'unhealthy' || s?.status === 'error');

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <div className={cn(
        "p-4 rounded-lg border-2",
        allHealthy && "bg-green-50 border-green-500",
        !allHealthy && !someUnhealthy && "bg-yellow-50 border-yellow-500",
        someUnhealthy && "bg-red-50 border-red-500"
      )}>
        <div className="flex items-center gap-3">
          {allHealthy && <CheckCircle className="h-6 w-6 text-green-600" />}
          {!allHealthy && !someUnhealthy && <AlertCircle className="h-6 w-6 text-yellow-600" />}
          {someUnhealthy && <XCircle className="h-6 w-6 text-red-600" />}
          <div className="flex-1">
            <h4 className={cn(
              "text-lg font-semibold",
              allHealthy && "text-green-900",
              !allHealthy && !someUnhealthy && "text-yellow-900",
              someUnhealthy && "text-red-900"
            )}>
              {allHealthy && "All Systems Operational"}
              {!allHealthy && !someUnhealthy && "Some Services Degraded"}
              {someUnhealthy && "System Issues Detected"}
            </h4>
            {lastChecked && (
              <p className="text-xs text-gray-600 mt-1">
                Last checked: {lastChecked.toLocaleTimeString()}
              </p>
            )}
          </div>
          <button
            onClick={fetchHealth}
            disabled={loading}
            className="p-2 rounded-lg hover:bg-white/50 transition-colors disabled:opacity-50"
            title="Refresh status"
          >
            <RefreshCw className={cn("h-5 w-5 text-gray-600", loading && "animate-spin")} />
          </button>
        </div>
      </div>

      {/* Service Status List */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold text-gray-700">Service Status</h4>
        
        {/* Backend API */}
        <ServiceStatus
          name="Backend API"
          status={services.backend?.status || 'healthy'}
          icon={Activity}
          details={services.backend?.version ? `v${services.backend.version}` : null}
        />

        {/* Neo4j Database */}
        <ServiceStatus
          name="Neo4j Database"
          status={services.neo4j?.status || 'unknown'}
          icon={Database}
          details={services.neo4j?.latency ? `Latency: ${services.neo4j.latency}ms` : null}
        />

        {/* Ollama LLM */}
        <ServiceStatus
          name="Ollama LLM"
          status={services.ollama?.status || 'unknown'}
          icon={Cpu}
          details={services.ollama?.model ? `Model: ${services.ollama.model}` : null}
        />

        {/* Storage */}
        {services.storage && (
          <ServiceStatus
            name="Storage"
            status={services.storage.status || 'healthy'}
            icon={HardDrive}
            details={services.storage.available ? `Available: ${services.storage.available}` : null}
          />
        )}
      </div>

      {/* System Info */}
      {health?.system && (
        <div className="pt-4 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">System Information</h4>
          <div className="space-y-1 text-xs text-gray-600">
            {health.system.version && (
              <div className="flex justify-between">
                <span>Version:</span>
                <span className="font-medium text-gray-900">{health.system.version}</span>
              </div>
            )}
            {health.system.uptime && (
              <div className="flex justify-between">
                <span>Uptime:</span>
                <span className="font-medium text-gray-900">{health.system.uptime}</span>
              </div>
            )}
            {health.system.environment && (
              <div className="flex justify-between">
                <span>Environment:</span>
                <span className="font-medium text-gray-900">{health.system.environment}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemHealthPanel;

