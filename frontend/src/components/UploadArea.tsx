import { useState, useRef } from "react";
import { uploadFile } from "../api";
import type { UploadResponse } from "../api";

interface UploadAreaProps {
  onUploadComplete: (docId: string) => void;
}

export function UploadArea({ onUploadComplete }: UploadAreaProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleFile = async (file: File) => {
    if (file.type !== "application/pdf") {
      setError("Please upload a PDF file");
      return;
    }

    setError(null);
    setFileName(file.name);
    setFileSize(file.size);
    setIsUploading(true);
    setUploadProgress(0);

    try {
      setIsIndexing(true);
      const result: UploadResponse = await uploadFile(file, (progress) => {
        setUploadProgress(progress);
      });

      setIsUploading(false);
      setIsIndexing(false);
      setUploadProgress(null);

      // Document is ready immediately after upload (indexing happens server-side)
      if (result.status === "ready") {
        onUploadComplete(result.doc_id);
      } else {
        setError("Upload failed. Please try again.");
      }
    } catch (err) {
      setIsUploading(false);
      setIsIndexing(false);
      setUploadProgress(null);
      setError(err instanceof Error ? err.message : "Upload failed");
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-all
          ${
            isDragging
              ? "border-blue-400 bg-blue-500/10"
              : "border-gray-600 bg-gray-800/50 hover:border-gray-500"
          }
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          className="hidden"
        />

        {!isUploading && !isIndexing && (
          <>
            <div className="mb-4">
              <svg
                className="w-16 h-16 mx-auto text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <p className="text-gray-300 mb-2">
              Drag and drop your PDF here, or{" "}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-blue-400 hover:text-blue-300 underline"
              >
                choose a file
              </button>
            </p>
            <p className="text-sm text-gray-500">
              Maximum file size: 50MB
            </p>
          </>
        )}

        {isUploading && (
          <div className="space-y-4">
            <p className="text-gray-300">Uploading {fileName}...</p>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="text-sm text-gray-400">
              {uploadProgress?.toFixed(0)}% • {fileSize ? formatFileSize(fileSize) : ""}
            </p>
          </div>
        )}

        {isIndexing && (
          <div className="space-y-4">
            <div className="flex items-center justify-center space-x-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400"></div>
              <p className="text-gray-300">Indexing document...</p>
            </div>
            <p className="text-sm text-gray-500">
              Extracting text, chunking, and creating embeddings. This may take a moment for large documents.
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-900/30 border border-red-700 rounded-lg">
          <p className="text-red-300">{error}</p>
          <button
            onClick={() => {
              setError(null);
              setFileName(null);
              setFileSize(null);
            }}
            className="mt-2 text-sm text-red-400 hover:text-red-300 underline"
          >
            Try again
          </button>
        </div>
      )}

      {fileName && !isUploading && !isIndexing && !error && (
        <div className="mt-4 p-4 bg-green-900/30 border border-green-700 rounded-lg">
          <p className="text-green-300">✓ {fileName} ready</p>
        </div>
      )}
    </div>
  );
}
