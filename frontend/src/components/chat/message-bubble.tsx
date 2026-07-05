/**
 * MessageBubble Component — Renders individual user and assistant messages.
 * Uses react-markdown for rich text parsing and formats citations / source snippets
 * in collapsible cards with relevance scores.
 */

"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { User, Bot, BookOpen, ChevronDown, ChevronUp, Terminal } from "lucide-react";
import { CodeBlock } from "@/components/chat/code-block";
import type { Message, SourceChunk } from "@/types";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const [showSources, setShowSources] = useState(false);

  return (
    <div className={`flex w-full space-x-4 p-6 ${isUser ? "bg-zinc-950/20" : "bg-zinc-900/10 border-y border-border/10"}`}>
      {/* Avatar Container */}
      <Avatar className={`h-9 w-9 border ${isUser ? "bg-zinc-800 border-zinc-700 text-purple-400" : "bg-purple-600/10 border-purple-500/20 text-purple-400"}`}>
        <AvatarFallback className="bg-transparent font-semibold">
          {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
        </AvatarFallback>
      </Avatar>

      {/* Message Content Area */}
      <div className="flex-1 space-y-4 overflow-hidden">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-semibold text-foreground">
            {isUser ? "You" : "Assistant"}
          </span>
          <span className="text-[10px] text-muted-foreground pt-0.5">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        {/* Markdown Text Body */}
        <div className="text-zinc-200 text-sm leading-relaxed prose prose-invert max-w-none break-words">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Inject custom CodeBlock component for code blocks
              code({ node, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || "");
                const isInline = !className;
                return !isInline ? (
                  <CodeBlock
                    value={String(children).replace(/\n$/, "")}
                    language={match ? match[1] : "plaintext"}
                  />
                ) : (
                  <code className="px-1.5 py-0.5 bg-zinc-800 border border-zinc-700/60 rounded text-purple-300 font-mono text-xs break-all" {...props}>
                    {children}
                  </code>
                );
              },
              p({ children }) {
                return <p className="mb-3 last:mb-0">{children}</p>;
              },
              ul({ children }) {
                return <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>;
              },
              ol({ children }) {
                return <ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>;
              },
              li({ children }) {
                return <li className="mb-0.5">{children}</li>;
              },
              h1: ({ children }) => <h1 className="text-xl font-bold mt-4 mb-2 text-foreground">{children}</h1>,
              h2: ({ children }) => <h2 className="text-lg font-bold mt-4 mb-2 text-foreground">{children}</h2>,
              h3: ({ children }) => <h3 className="text-md font-bold mt-3 mb-1 text-foreground">{children}</h3>,
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-purple-500/50 pl-4 my-2 italic text-muted-foreground bg-purple-950/5 py-1 rounded-r">
                  {children}
                </blockquote>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Citations & Sources list (Assistant Only) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="pt-2">
            <button
              onClick={() => setShowSources(!showSources)}
              className="inline-flex items-center space-x-2 text-xs font-semibold text-zinc-400 hover:text-white px-3 py-1.5 rounded-lg border border-border/10 bg-card/25 transition-all duration-200"
            >
              <BookOpen className="h-3.5 w-3.5" />
              <span>
                {showSources ? "Hide Sources" : `View Sources (${message.sources.length})`}
              </span>
              {showSources ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </button>

            {/* Collapsible Sources Cards list */}
            {showSources && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 animate-slide-in">
                {message.sources.map((source, index) => (
                  <Card key={index} className="border border-border/60 bg-zinc-950/40 rounded-xl overflow-hidden shadow-sm hover:border-purple-500/20 transition duration-200">
                    <CardContent className="p-3.5 space-y-2">
                      <div className="flex items-center justify-between">
                        {/* File link display format */}
                        <span className="text-xs font-semibold text-foreground truncate max-w-[70%]">
                          {source.file_path.split("/").pop()}
                        </span>
                        <Badge variant="outline" className="text-[10px] py-0.5 px-2 bg-green-500/5 text-green-400 border-green-500/20">
                          {Math.round(source.relevance_score * 100)}% match
                        </Badge>
                      </div>

                      <span className="text-[10px] font-mono text-zinc-500 block truncate">
                        {source.file_path} {source.start_line ? `#L${source.start_line}-${source.end_line}` : ""}
                      </span>

                      {/* Snippet Preview Box */}
                      <div className="p-2 rounded bg-zinc-900 border border-zinc-800 font-mono text-[10px] text-zinc-400 overflow-x-auto whitespace-pre max-h-[100px]">
                        {source.snippet.trim()}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
