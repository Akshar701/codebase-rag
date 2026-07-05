/**
 * Shared TypeScript types for the Codebase RAG application.
 */

// --- Ingestion ---

export interface IngestRequest {
  github_url: string;
}

export interface IngestionStatistics {
  files_processed: number;
  files_skipped: number;
  chunks_generated: number;
  embedding_time_seconds: number;
  total_duration_seconds: number;
}

export interface IngestResponse {
  status: string;
  repository_id: string;
  statistics: IngestionStatistics;
}

// --- Chat ---

export interface ChatRequest {
  repository_id: string;
  question: string;
}

export interface SourceChunk {
  file_path: string;
  start_line: number | null;
  end_line: number | null;
  snippet: string;
  relevance_score: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceChunk[];
}

// --- UI State ---

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
  timestamp: Date;
}

export interface Conversation {
  id: string;
  repository_id: string;
  repository_name: string;
  messages: Message[];
  created_at: Date;
}

// --- Errors ---

export interface APIError {
  error: string;
  message: string;
  details?: string;
}
