/**
 * Utility functions shared across the frontend.
 */

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind classes with conflict resolution.
 * Standard pattern used by shadcn/ui components.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Generate a unique ID for messages and conversations.
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Extract owner and repo name from a GitHub URL.
 * e.g., "https://github.com/pallets/flask" → { owner: "pallets", repo: "flask" }
 */
export function parseGitHubUrl(url: string): {
  owner: string;
  repo: string;
} | null {
  const match = url.match(
    /^https?:\/\/github\.com\/([\w\-\.]+)\/([\w\-\.]+)\/?$/
  );
  if (!match) return null;
  return { owner: match[1], repo: match[2] };
}

/**
 * Format seconds into a human-readable duration string.
 */
export function formatDuration(seconds: number): string {
  if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes}m ${remainingSeconds}s`;
}

/**
 * Format a repository ID back to a display name.
 * e.g., "pallets_flask" → "pallets/flask"
 */
export function formatRepoName(repositoryId: string): string {
  const idx = repositoryId.indexOf("_");
  if (idx === -1) return repositoryId;
  return repositoryId.substring(0, idx) + "/" + repositoryId.substring(idx + 1);
}
