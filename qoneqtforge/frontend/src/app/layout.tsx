import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'QoneqtForge — AI Video Pipeline for Qoneqt',
  description: 'Transform any topic into a publish-ready vertical video for the Qoneqt Global Feed. 12-stage AI pipeline with quality gates, batch mode, and zero cost.',
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
        <nav className="fixed top-0 w-full z-50" style={{
          background: 'hsla(240, 20%, 4%, 0.75)',
          backdropFilter: 'blur(20px) saturate(1.3)',
          borderBottom: '1px solid hsla(240, 20%, 30%, 0.12)',
        }}>
          <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-3.5">
            <a href="/" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm" style={{
                background: 'linear-gradient(135deg, hsl(258, 100%, 65%), hsl(185, 100%, 55%))',
                boxShadow: '0 2px 12px hsla(258, 100%, 65%, 0.3)',
              }}>
                ⚡
              </div>
              <span className="text-lg font-display font-bold tracking-tight">
                <span className="gradient-text">Qoneqt</span>
                <span className="text-white/80">Forge</span>
              </span>
            </a>
            <div className="flex items-center gap-1">
              {[
                { href: '/', label: 'Create' },
                { href: '/batch', label: 'Batch' },
              ].map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  className="px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 text-white/75 hover:text-white hover:bg-white/10"
                >
                  {link.label}
                </a>
              ))}
            </div>
          </div>
        </nav>

        {/* Main content */}
        <main className="pt-16 min-h-screen relative" style={{ zIndex: 1 }}>
          {children}
        </main>

        {/* Footer */}
        <footer className="relative" style={{
          zIndex: 1,
          borderTop: '1px solid hsla(240, 20%, 20%, 0.15)',
        }}>
          <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-5 text-sm" style={{ color: 'var(--text-muted)' }}>
            <span className="font-display font-medium">QoneqtForge v1.0 · CTRL FREAK 2026</span>
            <span>Cost per video: <span className="font-semibold" style={{ color: 'var(--success)' }}>₹0</span></span>
          </div>
        </footer>
      </body>
    </html>
  )
}
