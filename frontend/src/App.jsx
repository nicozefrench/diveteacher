import { useState } from 'react'
import FileUpload from './components/FileUpload'
import Chat from './components/Chat'

function App() {
  const [uploadedDocuments, setUploadedDocuments] = useState([])

  const handleUploadComplete = (uploadId, filename) => {
    setUploadedDocuments(prev => [...prev, { uploadId, filename }])
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            📚 RAG Knowledge Graph
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Upload documents, build knowledge graphs, ask questions
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: File Upload */}
          <div>
            <FileUpload onUploadComplete={handleUploadComplete} />
            
            {/* Uploaded Documents List */}
            {uploadedDocuments.length > 0 && (
              <div className="mt-6">
                <h2 className="text-lg font-semibold mb-3">
                  Uploaded Documents ({uploadedDocuments.length})
                </h2>
                <ul className="space-y-2">
                  {uploadedDocuments.map((doc, idx) => (
                    <li 
                      key={idx} 
                      className="bg-white p-3 rounded-lg border text-sm"
                    >
                      <span className="font-medium">{doc.filename}</span>
                      <span className="text-gray-500 ml-2">✓ Processed</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Right: Chat Interface */}
          <div>
            <Chat />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-sm text-gray-600">
          <p>
            Powered by <strong>Ollama</strong> + <strong>Neo4j</strong> + <strong>Graphiti</strong>
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App

