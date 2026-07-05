/**
 * CodeBlock Component — Render code blocks inside markdown answers.
 * Features: syntax display header, language label, copy to clipboard button,
 * and elegant scrolling layouts.
 */

"use client";

import React, { useState } from "react";
import { Check, Copy } from "lucide-react";

interface CodeBlockProps {
  value: string;
  language?: string;
}

export function CodeBlock({ value, language = "plaintext" }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.warn("Failed to copy code to clipboard", err);
    }
  };

  return (
    <div className="relative group my-4 rounded-xl border border-border/80 bg-zinc-900 overflow-hidden font-mono text-sm shadow-md">
      {/* Codeblock Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border/20 bg-zinc-950 text-zinc-400 text-xs">
        <span className="font-semibold uppercase tracking-wider">{language}</span>
        <button
          onClick={handleCopy}
          className="flex items-center space-x-1 hover:text-white px-2 py-1 rounded-md hover:bg-zinc-800 transition"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-green-400" />
              <span className="text-green-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code Content */}
      <div className="p-4 overflow-x-auto max-h-[350px] scrollbar-thin scrollbar-thumb-zinc-700">
        <pre className="text-left text-zinc-100 font-mono leading-relaxed whitespace-pre">
          <code>{value.trim()}</code>
        </pre>
      </div>
    </div>
  );
}
