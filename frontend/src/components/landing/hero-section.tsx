/**
 * HeroSection Component — Premium landing page title and description.
 * Utilizes sleek glassmorphism gradients and modern sans-serif typography.
 */

"use client";

import React from "react";
import { Terminal, Github, Bot } from "lucide-react";

export function HeroSection() {
  return (
    <div className="flex flex-col items-center text-center space-y-6 max-w-3xl mx-auto px-4 py-8">
      {/* Badge container with micro-animation */}
      <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full border border-border bg-card/40 backdrop-blur-md animate-fade-in hover:border-primary/50 transition-colors duration-300">
        <Bot className="h-4 w-4 text-purple-400" />
        <span className="text-xs font-semibold tracking-wide uppercase text-muted-foreground">
          RAG-Powered Code Intelligence
        </span>
      </div>

      {/* Hero title with sleek gradient */}
      <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-white via-neutral-200 to-neutral-500 bg-clip-text text-transparent">
        Talk to Your <br />
        <span className="bg-gradient-to-r from-purple-400 via-violet-400 to-indigo-500 bg-clip-text text-transparent">
          GitHub Codebase
        </span>
      </h1>

      {/* Subheading */}
      <p className="text-lg text-muted-foreground leading-relaxed max-w-xl">
        Enter a public GitHub repository URL to download, chunk, and index the entire codebase. 
        Then, ask questions and get instant, grounded explanations with source references.
      </p>

      {/* Features showcase */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full pt-6 max-w-lg">
        <div className="flex items-center space-x-3 p-4 rounded-xl border border-border/50 bg-card/25 backdrop-blur-sm text-left">
          <Terminal className="h-5 w-5 text-indigo-400 shrink-0" />
          <div>
            <h4 className="text-sm font-semibold text-foreground">Language-Aware</h4>
            <p className="text-xs text-muted-foreground">Intelligent syntax chunking preserving logical structures.</p>
          </div>
        </div>
        <div className="flex items-center space-x-3 p-4 rounded-xl border border-border/50 bg-card/25 backdrop-blur-sm text-left">
          <Github className="h-5 w-5 text-purple-400 shrink-0" />
          <div>
            <h4 className="text-sm font-semibold text-foreground">Instant Parsing</h4>
            <p className="text-xs text-muted-foreground">Auto-indexes public files via GitHub REST trees.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
