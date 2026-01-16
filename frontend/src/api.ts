const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:3001";

export interface UploadResponse {
  doc_id: string;
  chunk_count: number;
  status: "ready";
}

export interface ChatRequest {
  question: string;
  doc_id: string;
}

export interface ErrorResponse {
  error: string;
  provider?: string;
  status?: number;
  details?: string;
}

export interface Source {
  text: string;
  chunk_index: number | null;
  score: number | null;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
}

/**
 * Upload a PDF file to the backend
 */
export async function uploadFile(
  file: File,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable && onProgress) {
        const progress = (e.loaded / e.total) * 100;
        onProgress(progress);
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText) as UploadResponse;
          resolve(response);
        } catch (error) {
          reject(new Error("Failed to parse response"));
        }
      } else {
        // Try to parse structured error response from backend
        let errorMessage = `Upload failed: ${xhr.statusText}`;
        try {
          const errorResponse: ErrorResponse = JSON.parse(xhr.responseText);
          if (errorResponse.error) {
            errorMessage = errorResponse.error;
            if (errorResponse.details) {
              errorMessage += `: ${errorResponse.details}`;
            }
          } else if (errorResponse.detail) {
            errorMessage = errorResponse.detail;
          }
        } catch (e) {
          // If response isn't JSON, use status text
          errorMessage = xhr.responseText || `Upload failed: ${xhr.statusText}`;
        }
        reject(new Error(errorMessage));
      }
    });

    xhr.addEventListener("error", () => {
      reject(new Error("Upload failed"));
    });

    xhr.open("POST", `${API_BASE_URL}/api/upload`);
    xhr.send(formData);
  });
}


/**
 * Send a chat message
 */
export async function sendMessage(
  question: string,
  docId: string
): Promise<ChatResponse> {
  const body: ChatRequest = { question, doc_id: docId };

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error: ErrorResponse = await response.json().catch(() => ({ error: "Unknown error" }));
    const errorMessage = error.error || `Chat request failed: ${response.statusText}`;
    const details = error.details ? `: ${error.details}` : "";
    throw new Error(errorMessage + details);
  }

  return response.json();
}
