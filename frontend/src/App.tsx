import { useState } from "react";
import { UploadArea } from "./components/UploadArea";
import { Chat } from "./components/Chat";

function App() {
  const [docId, setDocId] = useState<string | null>(null);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-700 bg-gray-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-white">Document Q&A Engine</h1>
          <p className="text-sm text-gray-400 mt-1">
            Upload a PDF and ask questions about its content
          </p>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 container mx-auto px-4 py-8">
        {!docId ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <UploadArea onUploadComplete={setDocId} />
          </div>
        ) : (
          <div className="h-[calc(100vh-200px)]">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-gray-400">
                Document ready • ID: <code className="bg-gray-800 px-2 py-1 rounded text-xs">{docId}</code>
              </p>
              <button
                onClick={() => {
                  setDocId(null);
                }}
                className="text-sm text-gray-400 hover:text-gray-300 underline"
              >
                Upload new document
              </button>
            </div>
            <Chat docId={docId} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-700 bg-gray-900/50 backdrop-blur-sm py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-500">
          Powered by OpenAI & RAG
        </div>
      </footer>
    </div>
  );
}

export default App;
