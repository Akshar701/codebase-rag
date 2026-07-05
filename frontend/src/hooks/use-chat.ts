/**
 * useChat — manages the chat conversation state.
 * Handles message history, loading, streaming feel, and errors.
 */

"use client";

import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api";
import { generateId } from "@/lib/utils";
import type { Message, SourceChunk } from "@/types";

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (question: string) => Promise<void>;
  clearMessages: () => void;
}

export function useChat(repositoryId: string): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (question: string) => {
      // Add user message immediately
      const userMessage: Message = {
        id: generateId(),
        role: "user",
        content: question,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await apiClient.chat(repositoryId, question);

        // Add assistant response
        const assistantMessage: Message = {
          id: generateId(),
          role: "assistant",
          content: response.answer,
          sources: response.sources,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to get response";
        setError(message);

        // Add error message as assistant response
        const errorMessage: Message = {
          id: generateId(),
          role: "assistant",
          content: `⚠️ Error: ${message}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [repositoryId]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, isLoading, error, sendMessage, clearMessages };
}
