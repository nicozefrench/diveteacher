/**
 * TabNavigation Component
 * Tabs for switching between Upload and Query
 */

import { Upload, MessageSquare } from 'lucide-react';
import { cn } from '@/lib/utils';

const TABS = [
  { id: 'upload', label: 'Document Upload', icon: Upload },
  { id: 'query', label: 'RAG Query', icon: MessageSquare }
];

export function TabNavigation({ activeTab, setActiveTab }) {
  return (
    <div className="border-b border-gray-200 bg-white">
      <div className="dive-container">
        <nav className="dive-tabs">
          {TABS.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'dive-tab',
                  isActive && 'dive-tab-active'
                )}
              >
                <Icon size={20} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
}

