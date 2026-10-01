import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'QoneqtForge — AI Content Pipeline for Qoneqt',
  description: 'Transform topics into publish-ready vertical videos for the Qoneqt Global Feed using AI. Multi-agent pipeline with quality gates, batch mode, and zero cost.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="gradient-bg min-h-screen">
        {/* Navigation */}
        <nav className="fixed top-0 w-full z-50 glass-card border-t-0 border-x-0 rounded-none px-6 py-3">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <a href="/" className="flex items-center gap-2">
              <span className="text-2xl">🎬</span>
              <span className="text-xl font-bold">
                <span className="gradient-text">Qoneqt</span>
                <span className="text-white/80">Forge</span>
              </span>
            </a>
            <div className="flex items-center gap-6">
              <a href="/" className="text-sm text-white/60 hover:text-white transition-colors">Create</a>
              <a href="/batch" className="text-sm text-white/60 hover:text-white transition-colors">Batch</a>
              <a href="/gallery" className="text-sm text-white/60 hover:text-white transition-colors">Gallery</a>
              <a href="/about" className="text-sm text-white/60 hover:text-white transition-colors">About</a>
            </div>
          </div>
        </nav>

        {/* Main content */}
        <main className="pt-16 min-h-screen">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-white/5 py-6 px-6">
          <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-white/30">
            <span>QoneqtForge v1.0 · CTRL FREAK 2026</span>
            <span>Cost per video: <span className="text-green-400 font-semibold">₹0</span></span>
          </div>
        </footer>
      </body>
    </html>
  )
}
