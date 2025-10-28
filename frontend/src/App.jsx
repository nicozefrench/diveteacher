import { useState } from 'react';
import { Upload, MessageSquare, Activity } from 'lucide-react';
import UploadTab from './components/upload/UploadTab';
import ChatInterface from './components/query/ChatInterface';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [systemStatus, setSystemStatus] = useState('loading');

  // Check system health on mount
  useState(() => {
    fetch('http://localhost:8000/api/query/health')
      .then(() => setSystemStatus('operational'))
      .catch(() => setSystemStatus('error'));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white shadow-sm">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo & Brand */}
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-primary">
                <svg
                  className="h-6 w-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">DiveTeacher</h1>
                <p className="text-xs text-gray-500">AI-Powered RAG Knowledge System</p>
              </div>
            </div>

            {/* System Status */}
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                System
              </span>
              <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                systemStatus === 'operational' 
                  ? 'bg-success-50 text-success-700'
                  : systemStatus === 'error'
                  ? 'bg-error-50 text-error-700'
                  : 'bg-gray-50 text-gray-700'
              }`}>
                <span className={`h-1.5 w-1.5 rounded-full ${
                  systemStatus === 'operational' 
                    ? 'bg-success-500'
                    : systemStatus === 'error'
                    ? 'bg-error-500'
                    : 'bg-gray-400 animate-pulse'
                }`} />
                {systemStatus === 'operational' 
                  ? 'Operational'
                  : systemStatus === 'error'
                  ? 'Offline'
                  : 'Checking...'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Admin Dashboard</h2>
          <p className="mt-1 text-sm text-gray-500">
            Manage your documents and interact with the RAG knowledge graph
          </p>
        </div>

        {/* Tabs Navigation */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="-mb-px flex gap-6" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('upload')}
              className={`
                group inline-flex items-center gap-2 border-b-2 px-1 py-4 text-sm font-medium transition-all
                ${activeTab === 'upload'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }
              `}
            >
              <Upload className={`h-5 w-5 ${activeTab === 'upload' ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500'}`} />
              Document Upload
              {activeTab === 'upload' && (
                <span className="rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">
                  Active
                </span>
              )}
            </button>

            <button
              onClick={() => setActiveTab('query')}
              className={`
                group inline-flex items-center gap-2 border-b-2 px-1 py-4 text-sm font-medium transition-all
                ${activeTab === 'query'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }
              `}
            >
              <MessageSquare className={`h-5 w-5 ${activeTab === 'query' ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500'}`} />
              RAG Query
              {activeTab === 'query' && (
                <span className="rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">
                  Active
                </span>
              )}
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="animate-fade-in">
          {activeTab === 'upload' && <UploadTab />}
          {activeTab === 'query' && <ChatInterface />}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-gray-200 bg-white">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <p className="text-sm text-gray-500">
              © 2025 DiveTeacher. AI-Powered Diving Education Platform.
            </p>
            <div className="flex items-center gap-4">
              <a href="#" className="text-sm text-gray-500 hover:text-primary-600 transition-colors">
                Documentation
              </a>
              <a href="#" className="text-sm text-gray-500 hover:text-primary-600 transition-colors">
                Support
              </a>
              <span className="text-sm text-gray-400">v1.2.0</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
