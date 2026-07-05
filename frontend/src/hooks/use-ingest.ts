/**
 * useIngest — manages the repository ingestion lifecycle.
 * Handles loading states, progress, statistics, and errors.
 */

"use client";

import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import type { IngestResponse, IngestionStatistics } from "@/types";

interface UseIngestReturn {
  isLoading: boolean;
  error: string | null;
  statistics: IngestionStatistics | null;
  repositoryId: string | null;
  ingest: (githubUrl: string) => Promise<void>;
  reset: () => void;
}

export function useIngest(): UseIngestReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statistics, setStatistics] = useState<IngestionStatistics | null>(null);
  const [repositoryId, setRepositoryId] = useState<string | null>(null);

  const ingest = useCallback(async (githubUrl: string) => {
    setIsLoading(true);
    setError(null);
    setStatistics(null);
    setRepositoryId(null);

    try {
      const response: IngestResponse =
        await apiClient.ingestRepository(githubUrl);
      setStatistics(response.statistics);
      setRepositoryId(response.repository_id);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setStatistics(null);
    setRepositoryId(null);
  }, []);

  return { isLoading, error, statistics, repositoryId, ingest, reset };
}
