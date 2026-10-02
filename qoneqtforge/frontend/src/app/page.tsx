'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createJob, getTrends, type BriefSpec, type TrendItem } from '@/lib/api';
import { COMMUNITY_OPTIONS, TONE_OPTIONS, LANGUAGE_OPTIONS, DURATION_OPTIONS, STYLE_OPTIONS } from '@/lib/types';

export default function HomePage() {
  const router = useRouter();
  const [topic, setTopic] = useState('');
  const [community, setCommunity] = useState('general');
  const [tone, setTone] = useState('energetic');
  const [language, setLanguage] = useState('en');
  const [duration, setDuration] = useState(30);
  const [style, setStyle] = useState('cinematic');
  const [isLoading, setIsLoading] = useState(false);
  const [trends, setTrends] = useState<TrendItem[]>([]);
  const [showOptions, setShowOptions] = useState(false);

  useEffect(() => {
    getTrends('all').then(setTrends).catch(console.error);
  }, []);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setIsLoading(true);

    try {
      const brief: BriefSpec = {
        topic: topic.trim(),
        community,
        tone,
        language,
        duration_sec: duration,
        visual_style: style,
      };
      const result = await createJob(brief);
      router.push(`/jobs/${result.id}`);
    } catch (error) {
      console.error('Failed to create job:', error);
      alert('Failed to create job. Make sure the backend is running on port 8000.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-4 py-20">

      {/* ── Hero ─────────────────────────────────────────────── */}
      <div className="text-center mb-14 max-w-3xl animate-fade-up">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium mb-6"
          style={{
            background: 'hsla(258, 60%, 50%, 0.08)',
            border: '1px solid hsla(258, 60%, 50%, 0.15)',
            color: 'var(--accent-light)',
          }}>
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--success)' }} />
          12-Stage AI Pipeline · 100% Free
        </div>

        <h1 className="font-display text-5xl md:text-7xl font-bold tracking-tight leading-[1.1] mb-5">
          <span className="gradient-text">What should the world</span>
          <br />
          <span style={{ color: 'var(--text-primary)' }}>see today?</span>
        </h1>

        <p className="text-base md:text-lg leading-relaxed max-w-lg mx-auto" style={{ color: 'var(--text-secondary)' }}>
          Turn any topic into a publish-ready vertical video for the
          <span className="gradient-text-subtle font-semibold"> Qoneqt Global Feed</span>.
          AI-powered. Multi-agent. Zero cost.
        </p>
      </div>

      {/* ── Input Bar ────────────────────────────────────────── */}
      <div className="w-full max-w-2xl mb-6 animate-fade-up delay-100">
        <div className="glass-card glass-card-active p-1.5" style={{
          boxShadow: '0 0 60px hsla(258, 100%, 65%, 0.08), 0 20px 60px hsla(0, 0%, 0%, 0.2)',
        }}>
          <div className="flex gap-1.5">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
              placeholder="Enter a topic, idea, or trend..."
              className="input-glow flex-1 px-5 py-4 text-base"
              style={{ border: 'none', background: 'transparent' }}
              disabled={isLoading}
            />
            <button
              onClick={handleGenerate}
              disabled={isLoading || !topic.trim()}
              className="btn-primary px-8 py-4 text-base whitespace-nowrap"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Generating...
                </span>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                  </svg>
                  Generate
                </>
              )}
            </button>
          </div>
        </div>

        {/* Options toggle */}
        <button
          onClick={() => setShowOptions(!showOptions)}
          className="mt-4 text-sm font-medium flex items-center gap-1.5 mx-auto transition-colors duration-200"
          style={{ color: 'var(--text-muted)' }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
          </svg>
          {showOptions ? 'Hide options' : 'Advanced options'}
        </button>

        {/* Options drawer */}
        {showOptions && (
          <div className="glass-card p-5 mt-3 grid grid-cols-2 md:grid-cols-3 gap-4" style={{
            animation: 'fade-up 0.3s ease forwards',
          }}>
            {[
              { label: 'Community', value: community, setter: (v: string) => setCommunity(v), options: COMMUNITY_OPTIONS },
              { label: 'Tone', value: tone, setter: (v: string) => setTone(v), options: TONE_OPTIONS },
              { label: 'Language', value: language, setter: (v: string) => setLanguage(v), options: LANGUAGE_OPTIONS },
              { label: 'Duration', value: String(duration), setter: (v: string) => setDuration(Number(v)), options: DURATION_OPTIONS.map(o => ({ value: String(o.value), label: o.label })) },
              { label: 'Visual Style', value: style, setter: (v: string) => setStyle(v), options: STYLE_OPTIONS },
            ].map((field) => (
              <div key={field.label}>
                <label className="text-xs font-medium mb-1.5 block" style={{ color: 'var(--text-muted)' }}>
                  {field.label}
                </label>
                <select
                  value={field.value}
                  onChange={(e) => field.setter(e.target.value)}
                  className="input-glow w-full px-3 py-2.5 text-sm"
                >
                  {field.options.map((o: { value: string; label: string }) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Trending Topics ──────────────────────────────────── */}
      {trends.length > 0 && (
        <div className="w-full max-w-2xl mb-16 animate-fade-up delay-200">
          <p className="text-xs font-medium mb-3 text-center" style={{ color: 'var(--text-muted)' }}>
            <span className="inline-block w-1.5 h-1.5 rounded-full mr-1.5" style={{ background: 'var(--warning)', verticalAlign: 'middle' }} />
            Trending now
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {trends.slice(0, 8).map((trend, i) => (
              <button
                key={i}
                onClick={() => setTopic(trend.title)}
                className="chip"
                title={`Source: ${trend.source}`}
              >
                {trend.title.length > 45 ? trend.title.slice(0, 45) + '…' : trend.title}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Feature Cards ────────────────────────────────────── */}
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-5 animate-fade-up delay-300">
        {[
          {
            icon: '🧠',
            title: 'Multi-Agent AI',
            desc: '12-stage pipeline with research, scripting, and self-critiquing quality gate.',
            gradient: 'hsla(258, 60%, 50%, 0.08)',
          },
          {
            icon: '🔄',
            title: 'Never Fails',
            desc: 'Triple fallback on every provider — Gemini → Groq → Ollama. Always delivers.',
            gradient: 'hsla(185, 60%, 50%, 0.06)',
          },
          {
            icon: '💰',
            title: '₹0 Per Video',
            desc: '100% free-tier stack. No credit card. No GPU. Just pure creativity.',
            gradient: 'hsla(155, 60%, 50%, 0.06)',
          },
        ].map((f, i) => (
          <div key={i} className="feature-card">
            <div className="feature-icon" style={{ background: f.gradient }}>{f.icon}</div>
            <h3 className="font-display font-semibold text-base mb-2" style={{ color: 'var(--text-primary)' }}>
              {f.title}
            </h3>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              {f.desc}
            </p>
          </div>
        ))}
      </div>

      {/* ── Pipeline Visual ──────────────────────────────────── */}
      <div className="w-full max-w-5xl mt-20 animate-fade-up delay-400">
        <h2 className="font-display text-2xl font-bold text-center mb-2" style={{ color: 'var(--text-primary)' }}>
          How it works
        </h2>
        <p className="text-sm text-center mb-10" style={{ color: 'var(--text-muted)' }}>
          Your topic flows through 12 intelligent stages
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          {['📥 Ingest', '🔍 Research', '✍️ Script', '🎬 Scenes', '🧠 Critic', '🖼️ Visuals', '🎙️ Voice', '💬 Captions', '🎵 Music', '🎞️ Compose', '✅ QA', '📦 Export'].map((stage, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className="glass-card px-4 py-2.5 text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                {stage}
              </div>
              {i < 11 && (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--text-muted)', flexShrink: 0 }}>
                  <path d="m9 18 6-6-6-6" />
                </svg>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
