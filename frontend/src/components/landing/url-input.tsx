/**
 * URLInput Component — Accepts a public GitHub URL with interactive validation,
 * smooth input focus states, loading animations, and quick-start repository presets.
 */

"use client";

import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Github, ArrowRight, AlertCircle } from "lucide-react";
import { parseGitHubUrl } from "@/lib/utils";

interface URLInputProps {
  onIngest: (url: string) => void;
  isLoading: boolean;
}

const EXAMPLE_REPOS = [
  "https://github.com/pallets/flask",
  "https://github.com/postmanlabs/httpbin",
  "https://github.com/expressjs/express",
];

export function URLInput({ onIngest, isLoading }: URLInputProps) {
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const parsed = parseGitHubUrl(url);
    if (!parsed) {
      setError("Please enter a valid GitHub repository URL (e.g. https://github.com/owner/repo)");
      return;
    }

    onIngest(url.trim());
  };

  const handlePresetClick = (presetUrl: string) => {
    setUrl(presetUrl);
    setError(null);
    onIngest(presetUrl);
  };

  return (
    <div className="w-full max-w-lg mx-auto space-y-6 px-4">
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-muted-foreground">
              <Github className="h-5 w-5" />
            </div>
            <Input
              type="text"
              placeholder="https://github.com/owner/repo"
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                if (error) setError(null);
              }}
              disabled={isLoading}
              className="pl-11 h-12 bg-card/45 border-border/70 text-foreground placeholder-muted-foreground/60 rounded-xl focus-visible:ring-purple-500/50 focus-visible:border-purple-500/80 transition-all"
            />
          </div>
          <Button
            type="submit"
            disabled={isLoading || !url}
            className="h-12 px-6 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-medium shadow-md shadow-purple-900/25 hover:shadow-purple-900/35 transition-all duration-300"
          >
            {isLoading ? (
              <span className="flex items-center space-x-2">
                <span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Ingesting...</span>
              </span>
            ) : (
              <span className="flex items-center space-x-2">
                <span>Ingest</span>
                <ArrowRight className="h-4 w-4" />
              </span>
            )}
          </Button>
        </div>

        {error && (
          <div className="flex items-center space-x-2 text-red-400 text-sm p-3 rounded-lg border border-red-900/30 bg-red-950/20 animate-slide-in">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </form>

      {/* Preset Suggestions */}
      {!isLoading && (
        <div className="space-y-2.5">
          <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider text-center">
            Or quick-start with a sample repository
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {EXAMPLE_REPOS.map((repoUrl) => {
              const parts = parseGitHubUrl(repoUrl);
              const displayName = parts ? `${parts.owner}/${parts.repo}` : repoUrl;
              return (
                <button
                  key={repoUrl}
                  onClick={() => handlePresetClick(repoUrl)}
                  className="px-3 py-1.5 text-xs font-medium rounded-lg border border-border/60 bg-card/30 text-muted-foreground hover:text-foreground hover:bg-card/70 hover:border-purple-500/40 transition-all duration-200"
                >
                  {displayName}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
