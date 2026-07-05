/**
 * ChatInput Component — Prompt entry box with textareas.
 * Triggers submit on Enter, allows line breaks with Shift+Enter,
 * and handles loader states.
 */

"use client";

import React, { useRef, useState, useEffect } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Send, CornerDownLeft } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize the textarea based on text length
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    onSendMessage(input.trim());
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="relative rounded-2xl border border-border/80 bg-zinc-900 shadow-lg px-4 py-3 focus-within:border-purple-500/50 transition-all max-w-3xl mx-auto"
    >
      <Textarea
        ref={textareaRef}
        rows={1}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about this repository..."
        disabled={isLoading}
        className="w-full resize-none bg-transparent border-0 p-0 text-foreground placeholder-muted-foreground/60 focus-visible:ring-0 focus-visible:ring-offset-0 min-h-[24px] max-h-[200px]"
      />

      <div className="flex items-center justify-between pt-2 border-t border-border/10 mt-2 text-muted-foreground">
        <span className="text-[10px] hidden sm:flex items-center space-x-1">
          <span>Use</span>
          <kbd className="px-1 py-0.5 rounded bg-zinc-800 border border-zinc-700 font-mono text-[9px]">
            Enter
            </kbd>
          <span>to send,</span>
          <kbd className="px-1 py-0.5 rounded bg-zinc-800 border border-zinc-700 font-mono text-[9px]">
            Shift + Enter
            </kbd>
          <span>for newline</span>
        </span>

        <div className="flex items-center space-x-2 ml-auto">
          <Button
            type="submit"
            disabled={isLoading || !input.trim()}
            size="sm"
            className="h-8 w-8 rounded-lg bg-purple-600 hover:bg-purple-500 text-white p-0 shrink-0 transition"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </form>
  );
}
