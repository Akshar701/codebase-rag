/**
 * Landing Page — Root page for the AI GitHub Codebase Assistant.
 * Combines full-page ambient backlights, floating grid animations, URL input,
 * error boundaries, and pipeline stats dashboards.
 */

"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { HeroSection } from "@/components/landing/hero-section";
import { URLInput } from "@/components/landing/url-input";
import { IngestionProgress } from "@/components/landing/ingestion-progress";
import { useIngest } from "@/hooks/use-ingest";
import { Sparkles, Terminal } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const { ingest, isLoading, error, statistics, repositoryId } = useIngest();

  const handleProceed = () => {
    if (repositoryId) {
      // Redirect to the chat page with the ingested repo ID as query parameter
      router.push(`/chat?repo=${repositoryId}`);
    }
  };

  return (
    <main className="relative min-h-screen flex flex-col justify-between overflow-hidden bg-zinc-950 font-sans antialiased text-white selection:bg-purple-500/30">
      {/* Decorative ambient backgrounds */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[500px] pointer-events-none opacity-30 select-none">
        <div className="absolute top-[-10%] left-[-20%] w-[80%] h-[80%] rounded-full bg-indigo-500/20 blur-[120px]" />
        <div className="absolute top-[-20%] right-[-10%] w-[70%] h-[75%] rounded-full bg-purple-500/20 blur-[130px]" />
      </div>

      {/* Decorative grid pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.08),rgba(255,255,255,0))] -z-10" />

      {/* Top Header */}
      <header className="relative w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between border-b border-border/10">
        <div className="flex items-center space-x-3 select-none">
          <div className="p-2 rounded-xl bg-purple-600/10 border border-purple-500/25">
            <Terminal className="h-5 w-5 text-purple-400" />
          </div>
          <span className="font-bold tracking-tight text-lg bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
            CodebaseRAG
          </span>
        </div>

        <a
          href="https://github.com/aksharjain/codebase-rag"
          target="_blank"
          rel="noreferrer"
          className="flex items-center space-x-2 text-xs font-semibold text-zinc-400 hover:text-white px-4 py-2 rounded-xl border border-border/10 bg-card/20 hover:bg-card/50 transition-all duration-300"
        >
          <span>Star on GitHub</span>
          <Sparkles className="h-3 w-3 text-yellow-400" />
        </a>
      </header>

      {/* Main Container */}
      <div className="flex-1 flex flex-col items-center justify-center py-12 md:py-20 z-10">
        <div className="w-full space-y-10">
          <HeroSection />

          {/* Conditional rendering for Input vs Progress stats */}
          {!isLoading && !statistics ? (
            <URLInput onIngest={ingest} isLoading={isLoading} />
          ) : (
            <IngestionProgress
              isLoading={isLoading}
              statistics={statistics}
              onProceed={handleProceed}
            />
          )}

          {/* Endpoint Error boundary rendering */}
          {error && (
            <div className="w-full max-w-lg mx-auto px-4">
              <div className="p-4 rounded-xl border border-red-500/20 bg-red-950/15 text-center">
                <p className="text-sm font-semibold text-red-400">Ingestion Failed</p>
                <p className="text-xs text-red-300/80 pt-1 leading-relaxed">
                  {error}
                </p>
                <button
                  onClick={() => window.location.reload()}
                  className="mt-3 text-xs font-semibold text-purple-400 hover:text-purple-300 underline"
                >
                  Try another repository
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="relative w-full max-w-7xl mx-auto px-6 py-8 border-t border-border/5 text-center text-xs text-zinc-500 select-none">
        <p>© 2026 CodebaseRAG. Built with Next.js 15, FastAPI, Gemini API, and Pinecone Serverless.</p>
      </footer>
    </main>
  );
}
