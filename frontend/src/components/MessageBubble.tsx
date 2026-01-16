import { useState } from "react";
import type { Source } from "../api";

interface MessageBubbleProps {
  message: string;
  isUser: boolean;
  sources?: Source[];
  timestamp?: Date;
}

export function MessageBubble({
  message,
  isUser,
  sources,
  timestamp,
}: MessageBubbleProps) {
  const [sourcesExpanded, setSourcesExpanded] = useState(false);

  return (
    <div
      className={`flex w-full mb-4 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`max-w-[80%] md:max-w-[70%] rounded-lg p-4 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gray-800 text-gray-100 border border-gray-700"
        }`}
      >
        <div className="whitespace-pre-wrap break-words">{message}</div>

        {timestamp && (
          <div
            className={`text-xs mt-2 ${
              isUser ? "text-blue-200" : "text-gray-400"
            }`}
          >
            {timestamp.toLocaleTimeString()}
          </div>
        )}

        {sources && sources.length > 0 && !isUser && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <button
              onClick={() => setSourcesExpanded(!sourcesExpanded)}
              className="text-sm text-blue-400 hover:text-blue-300 flex items-center space-x-1"
            >
              <span>{sources.length} source{sources.length !== 1 ? "s" : ""}</span>
              <svg
                className={`w-4 h-4 transition-transform ${
                  sourcesExpanded ? "rotate-180" : ""
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {sourcesExpanded && (
              <div className="mt-2 space-y-2">
                {sources.map((source, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-gray-900/50 rounded border border-gray-700 text-sm"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-gray-400 text-xs">
                        Source {idx + 1}
                        {source.chunk_index !== null && ` • Chunk ${source.chunk_index}`}
                        {source.score !== null &&
                          ` • Score: ${source.score.toFixed(3)}`}
                      </span>
                    </div>
                    <p className="text-gray-300 text-xs line-clamp-3">
                      {source.text}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
