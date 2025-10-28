/**
 * App Component
 * Main application with tab navigation
 */

import { useState } from 'react';
import { Header } from './components/layout/Header';
import { TabNavigation } from './components/layout/TabNavigation';
import { Footer } from './components/layout/Footer';
import { UploadTab } from './components/upload/UploadTab';
import { ChatInterface } from './components/query/ChatInterface';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      
      <TabNavigation 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
      />
      
      <main className="flex-1 overflow-hidden">
        {activeTab === 'upload' && <UploadTab />}
        {activeTab === 'query' && <ChatInterface />}
      </main>
      
      <Footer />
    </div>
  );
}

export default App;
