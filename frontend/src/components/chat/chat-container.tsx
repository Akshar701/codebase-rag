/**
 * ChatContainer Component — Renders the message history scroll layout,
 * empty state headers, and typing loader indicators.
 * Implements auto-scrolling to show new messages.
 */

"use client";

import React, { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "@/components/chat/message-bubble";
import { Sparkles, Terminal } from "lucide-react";
import type { Message } from "@/types";

interface ChatContainerProps {
  messages: Message[];
  isLoading: boolean;
  repoName: string;
}

export function ChatContainer({
  messages,
  isLoading,
  repoName,
}: ChatContainerProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      const scrollContainer = scrollRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages, isLoading]);

  return (
    <ScrollArea ref={scrollRef} className="flex-1 h-full bg-zinc-950/20">
      {messages.length === 0 ? (
        /* Empty State */
        <div className="flex flex-col items-center justify-center h-[50vh] text-center space-y-4 px-6 select-none animate-fade-in">
          <div className="p-3.5 rounded-2xl bg-purple-600/10 border border-purple-500/25 text-purple-400">
            <Terminal className="h-8 w-8" />
          </div>
          <div className="space-y-1.5 max-w-sm">
            <h3 className="font-bold text-lg text-foreground">
              Connected to Workspace
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Ask questions about the classes, methods, endpoints, or configurations inside{" "}
              <span className="text-zinc-200 font-semibold">{repoName}</span>.
            </p>
          </div>
        </div>
      ) : (
        /* Message list */
        <div className="flex flex-col w-full pb-32">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {/* Typing Indicator */}
          {isLoading && (
            <div className="flex w-full space-x-4 p-6 bg-zinc-900/10 border-y border-border/10">
              <div className="h-9 w-9 border bg-purple-600/10 border-purple-500/20 text-purple-400 rounded-full flex items-center justify-center animate-pulse">
                <Sparkles className="h-5 w-5" />
              </div>
              <div className="flex-grow space-y-4 pt-1">
                <span className="text-sm font-semibold text-foreground">Assistant</span>
                <div className="flex items-center space-x-1 pt-1.5">
                  <div className="h-2.5 w-2.5 bg-purple-500/60 rounded-full animate-bounce delay-100" />
                  <div className="h-2.5 w-2.5 bg-purple-500/80 rounded-full animate-bounce delay-200" />
                  <div className="h-2.5 w-2.5 bg-purple-500 rounded-full animate-bounce delay-300" />
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </ScrollArea>
  );
}
