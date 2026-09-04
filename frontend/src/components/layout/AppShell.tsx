import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { CursorGlow } from "./CursorGlow";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="relative min-h-screen bg-bg text-text-primary">
      <CursorGlow />
      <Sidebar />
      <main className="relative z-10 md:pl-72">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</div>
      </main>
    </div>
  );
}
