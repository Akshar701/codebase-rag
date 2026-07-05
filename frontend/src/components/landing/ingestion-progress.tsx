/**
 * IngestionProgress Component — Renders a gorgeous, animated loader representing
 * the backend pipeline. Upon success, displays ingestion statistics in a sleek,
 * modular layout with a button to enter the chat workspace.
 */

"use client";

import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileText, Cpu, Server, Sparkles, MessageSquare, ArrowRight } from "lucide-react";
import { formatDuration } from "@/lib/utils";
import type { IngestionStatistics } from "@/types";

interface IngestionProgressProps {
  isLoading: boolean;
  statistics: IngestionStatistics | null;
  onProceed: () => void;
}

const PIPELINE_STEPS = [
  { text: "Fetching repository tree...", icon: FileText, delay: 0 },
  { text: "Downloading eligible files...", icon: Cpu, delay: 3000 },
  { text: "Parsing and chunking elements...", icon: Cpu, delay: 7000 },
  { text: "Generating vector embeddings...", icon: Sparkles, delay: 11000 },
  { text: "Upserting entries to Pinecone...", icon: Server, delay: 14000 },
];

export function IngestionProgress({
  isLoading,
  statistics,
  onProceed,
}: IngestionProgressProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [prevIsLoading, setPrevIsLoading] = useState(isLoading);

  // Adjust state during render when isLoading changes
  if (isLoading !== prevIsLoading) {
    setPrevIsLoading(isLoading);
    if (isLoading) {
      setCurrentStepIndex(0);
    }
  }

  useEffect(() => {
    if (!isLoading) {
      return;
    }

    const timers = PIPELINE_STEPS.map((step, idx) => {
      if (idx === 0) return null; // Already initialized to 0
      return setTimeout(() => {
        setCurrentStepIndex(idx);
      }, step.delay);
    }).filter((t): t is NodeJS.Timeout => t !== null);

    return () => {
      timers.forEach((t) => clearTimeout(t));
    };
  }, [isLoading]);

  if (!isLoading && !statistics) return null;

  return (
    <div className="w-full max-w-lg mx-auto px-4 py-4 animate-fade-in">
      <Card className="border border-border/80 bg-card/30 backdrop-blur-md overflow-hidden rounded-2xl">
        <CardContent className="p-6 space-y-6">
          {isLoading ? (
            /* Loading State Animation */
            <div className="flex flex-col items-center justify-center space-y-6 py-6">
              {/* Complex Glowing Spinner */}
              <div className="relative flex items-center justify-center h-20 w-20">
                <div className="absolute inset-0 border-4 border-purple-500/10 rounded-full" />
                <div className="absolute inset-0 border-4 border-transparent border-t-purple-500 border-r-indigo-500 rounded-full animate-spin duration-1000" />
                {React.createElement(PIPELINE_STEPS[currentStepIndex].icon, {
                  className: "h-8 w-8 text-purple-400 animate-pulse",
                })}
              </div>

              <div className="text-center space-y-2">
                <h3 className="text-lg font-bold text-foreground">
                  Ingesting Repository
                </h3>
                <p className="text-sm text-muted-foreground animate-pulse">
                  {PIPELINE_STEPS[currentStepIndex].text}
                </p>
              </div>

              {/* Progress dots bar */}
              <div className="flex space-x-1.5 pt-2">
                {PIPELINE_STEPS.map((_, idx) => (
                  <div
                    key={idx}
                    className={`h-1.5 w-1.5 rounded-full transition-all duration-300 ${
                      idx === currentStepIndex
                        ? "bg-purple-500 w-4"
                        : idx < currentStepIndex
                        ? "bg-purple-500/60"
                        : "bg-muted"
                    }`}
                  />
                ))}
              </div>
            </div>
          ) : (
            /* Statistics Display State */
            <div className="space-y-6">
              <div className="flex items-center space-x-3 pb-2 border-b border-border/50">
                <div className="p-2 rounded-lg bg-green-500/10 text-green-400">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-bold text-foreground">Ingestion Complete</h3>
                  <p className="text-xs text-muted-foreground">
                    Codebase successfully indexed and ready for chat.
                  </p>
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3.5 rounded-xl bg-card/65 border border-border/30">
                  <span className="text-xs text-muted-foreground block font-medium">
                    Files Processed
                  </span>
                  <span className="text-2xl font-extrabold text-foreground block pt-0.5">
                    {statistics?.files_processed}
                  </span>
                </div>
                <div className="p-3.5 rounded-xl bg-card/65 border border-border/30">
                  <span className="text-xs text-muted-foreground block font-medium">
                    Chunks Generated
                  </span>
                  <span className="text-2xl font-extrabold text-foreground block pt-0.5">
                    {statistics?.chunks_generated}
                  </span>
                </div>
                <div className="p-3.5 rounded-xl bg-card/65 border border-border/30">
                  <span className="text-xs text-muted-foreground block font-medium">
                    Embedding Time
                  </span>
                  <span className="text-lg font-bold text-foreground block pt-1">
                    {formatDuration(statistics?.embedding_time_seconds || 0)}
                  </span>
                </div>
                <div className="p-3.5 rounded-xl bg-card/65 border border-border/30">
                  <span className="text-xs text-muted-foreground block font-medium">
                    Total Duration
                  </span>
                  <span className="text-lg font-bold text-foreground block pt-1">
                    {formatDuration(statistics?.total_duration_seconds || 0)}
                  </span>
                </div>
              </div>

              {/* Warning/Skip display */}
              {(statistics?.files_skipped || 0) > 0 && (
                <p className="text-xs text-muted-foreground text-center">
                  Skipped {statistics?.files_skipped} non-code/excessive size files automatically.
                </p>
              )}

              {/* Action trigger to enter workspace */}
              <Button
                onClick={onProceed}
                className="w-full h-12 rounded-xl bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-semibold shadow-md shadow-green-950/20 hover:shadow-green-950/30 transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <span>Enter Workspace Chat</span>
                <MessageSquare className="h-4 w-4" />
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
