/**
 * API Client — handles all HTTP communication with the FastAPI backend.
 * Centralized error handling and type-safe request/response.
 */

import type {
  IngestRequest,
  IngestResponse,
  ChatRequest,
  ChatResponse,
  APIError,
} from "@/types";

const API_BASE_URL =
  (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData: APIError = await response.json().catch(() => ({
        error: "unknown_error",
        message: `Request failed with status ${response.status}`,
      }));
      throw new Error(errorData.message || `API error: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Ingest a GitHub repository.
   */
  async ingestRepository(githubUrl: string): Promise<IngestResponse> {
    const body: IngestRequest = { github_url: githubUrl };
    return this.request<IngestResponse>("/api/v1/ingest", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  /**
   * Ask a question about an ingested repository.
   */
  async chat(
    repositoryId: string,
    question: string
  ): Promise<ChatResponse> {
    const body: ChatRequest = {
      repository_id: repositoryId,
      question,
    };
    return this.request<ChatResponse>("/api/v1/chat", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  /**
   * Health check.
   */
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request("/health");
  }
}

export const apiClient = new APIClient(API_BASE_URL);
