/**
 * ChatSidebar Component — Sidebar panel for the chat workspace.
 * Displays repository info, active model configuration parameters,
 * and clears message logs.
 */

"use client";

import React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  ArrowLeft,
  Terminal,
  Cpu,
  Database,
  Sparkles,
  Trash2,
  Github,
} from "lucide-react";
import { formatRepoName } from "@/lib/utils";

interface ChatSidebarProps {
  repositoryId: string;
  onClearChat: () => void;
  messageCount: number;
}

export function ChatSidebar({
  repositoryId,
  onClearChat,
  messageCount,
}: ChatSidebarProps) {
  const displayName = formatRepoName(repositoryId);

  return (
    <aside className="w-64 border-r border-border/10 bg-zinc-950 flex flex-col justify-between h-full shrink-0">
      {/* Top Section */}
      <div className="flex-1 flex flex-col min-h-0 overflow-y-auto">
        {/* Return link */}
        <div className="p-4">
          <Link href="/">
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-zinc-400 hover:text-white pl-2 h-9 rounded-lg hover:bg-zinc-900"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              <span>Exit Workspace</span>
            </Button>
          </Link>
        </div>

        <Separator className="bg-border/5" />

        {/* Repository details */}
        <div className="p-4 space-y-4">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
              Active Repository
            </span>
            <div className="flex items-center space-x-2 pt-1">
              <Github className="h-4 w-4 text-purple-400 shrink-0" />
              <span className="font-bold text-sm text-foreground truncate">
                {displayName}
              </span>
            </div>
          </div>
        </div>

        <Separator className="bg-border/5" />

        {/* Configuration list */}
        <div className="p-4 space-y-4">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
            Pipeline Configuration
          </span>
          <div className="space-y-3 pt-1 text-xs text-zinc-400">
            <div className="flex items-center space-x-2.5">
              <Cpu className="h-3.5 w-3.5 text-zinc-500" />
              <div>
                <span className="text-[10px] text-zinc-500 block">LLM Model</span>
                <span className="font-semibold text-foreground">gemini-3.5-flash</span>
              </div>
            </div>
            <div className="flex items-center space-x-2.5">
              <Sparkles className="h-3.5 w-3.5 text-zinc-500" />
              <div>
                <span className="text-[10px] text-zinc-500 block">Embeddings</span>
                <span className="font-semibold text-foreground">gemini-embedding-002</span>
              </div>
            </div>
            <div className="flex items-center space-x-2.5">
              <Database className="h-3.5 w-3.5 text-zinc-500" />
              <div>
                <span className="text-[10px] text-zinc-500 block">Vector Index</span>
                <span className="font-semibold text-foreground">Pinecone Serverless</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="p-4 border-t border-border/5 space-y-3 bg-zinc-950/80">
        <div className="flex justify-between items-center text-xs text-zinc-500 px-1">
          <span>Messages log</span>
          <span className="font-bold">{messageCount}</span>
        </div>

        <Button
          onClick={onClearChat}
          disabled={messageCount === 0}
          variant="outline"
          size="sm"
          className="w-full text-red-400 border-red-950/20 bg-red-950/5 hover:bg-red-950/20 hover:text-red-300 rounded-lg h-9 transition-colors flex items-center justify-center space-x-2"
        >
          <Trash2 className="h-3.5 w-3.5" />
          <span>Clear Chat</span>
        </Button>
      </div>
    </aside>
  );
}
