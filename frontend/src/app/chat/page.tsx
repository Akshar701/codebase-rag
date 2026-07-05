/**
 * Chat Workspace Router — wraps query parsing and page rendering.
 * Wraps the Client component in a Suspense boundary (required in Next.js 15 for useSearchParams).
 */

"use client";

import React, { Suspense, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useChat } from "@/hooks/use-chat";
import { ChatSidebar } from "@/components/chat/chat-sidebar";
import { ChatContainer } from "@/components/chat/chat-container";
import { ChatInput } from "@/components/chat/chat-input";
import { formatRepoName } from "@/lib/utils";
import { Terminal } from "lucide-react";

function ChatWorkspace() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const repoId = searchParams.get("repo");

  // Unconditional hook calls at the top level
  const { messages, sendMessage, clearMessages, isLoading } = useChat(repoId || "");

  // Safe redirect in useEffect to avoid redirection during rendering phase
  useEffect(() => {
    if (!repoId) {
      router.push("/");
    }
  }, [repoId, router]);

  // Defer null-render check until all hooks are declared
  if (!repoId) {
    return null;
  }

  const repoDisplayName = formatRepoName(repoId);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-zinc-950 text-white font-sans">
      {/* Workspace Sidebar */}
      <ChatSidebar
        repositoryId={repoId}
        onClearChat={clearMessages}
        messageCount={messages.length}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col justify-between h-full bg-zinc-900/20 relative">
        {/* Glow backlight details */}
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-500/5 blur-[120px] pointer-events-none select-none -z-10" />

        {/* Scrollable Conversation Stream */}
        <ChatContainer
          messages={messages}
          isLoading={isLoading}
          repoName={repoDisplayName}
        />

        {/* Fixed Prompt Input Box */}
        <div className="p-6 bg-gradient-to-t from-zinc-950 via-zinc-950/80 to-transparent border-t border-border/5">
          <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}

// Fallback skeleton loader inside the suspense boundary
function ChatSkeleton() {
  return (
    <div className="flex h-screen w-screen items-center justify-center bg-zinc-950 text-zinc-400 space-x-3 select-none">
      <div className="h-5 w-5 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
      <span className="text-sm font-medium">Opening workspace...</span>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<ChatSkeleton />}>
      <ChatWorkspace />
    </Suspense>
  );
}
