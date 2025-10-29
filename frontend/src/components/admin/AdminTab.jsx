import { useState } from 'react';
import { Card, CardHeader, CardBody, CardTitle, CardDescription } from '../ui/Card';
import Neo4jManagementPanel from './Neo4jManagementPanel';
import SystemHealthPanel from './SystemHealthPanel';
import QueryConsole from './QueryConsole';

/**
 * AdminTab Component
 * 
 * Administrative dashboard for system management:
 * - Neo4j database management (stats, export, clear, query)
 * - System health monitoring (services status, logs)
 * - Cypher query console for database queries
 * 
 * @returns {JSX.Element} Admin dashboard
 */
const AdminTab = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">System Administration</h2>
        <p className="mt-1 text-sm text-gray-600">
          Manage the knowledge graph database and monitor system health
        </p>
      </div>

      {/* Top Row: Neo4j Management + System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Neo4j Management Card */}
        <Card>
          <CardHeader>
            <CardTitle>Neo4j Management</CardTitle>
            <CardDescription>
              Database statistics and management actions
            </CardDescription>
          </CardHeader>
          <CardBody>
            <Neo4jManagementPanel />
          </CardBody>
        </Card>

        {/* System Health Card */}
        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
            <CardDescription>
              Monitor service status and system resources
            </CardDescription>
          </CardHeader>
          <CardBody>
            <SystemHealthPanel />
          </CardBody>
        </Card>
      </div>

      {/* Bottom Row: Cypher Query Console (Full Width) */}
      <Card>
        <CardHeader>
          <CardTitle>Cypher Query Console</CardTitle>
          <CardDescription>
            Execute custom Cypher queries against the Neo4j database
          </CardDescription>
        </CardHeader>
        <CardBody>
          <QueryConsole />
        </CardBody>
      </Card>
    </div>
  );
};

export default AdminTab;

