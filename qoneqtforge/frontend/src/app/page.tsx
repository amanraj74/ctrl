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
    getTrends('all')
      .then(setTrends)
      .catch(console.error);
  }, []);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setIsLoading(true);

    try {
      const brief: BriefSpec = {
        topic: topic.trim(),
        community,
        tone: tone as any,
        language: language as any,
        duration_sec: duration as any,
        visual_style: style,
      };

      const result = await createJob(brief);
      router.push(`/jobs/${result.id}`);
    } catch (error) {
      console.error('Failed to create job:', error);
      alert('Failed to create job. Make sure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-4 py-16">
      {/* Hero */}
      <div className="text-center mb-12 max-w-3xl">
        <h1 className="text-5xl md:text-6xl font-extrabold mb-4" style={{ fontFamily: 'Poppins, sans-serif' }}>
          <span className="gradient-text">What should the world</span>
          <br />
          <span className="text-white">see today?</span>
        </h1>
        <p className="text-lg text-white/50 max-w-xl mx-auto">
          Turn any topic into a publish-ready vertical video for the Qoneqt Global Feed.
          AI-powered. Multi-agent pipeline. Zero cost.
        </p>
      </div>

      {/* Input */}
      <div className="w-full max-w-2xl mb-8">
        <div className="glass-card p-2 glow">
          <div className="flex gap-2">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
              placeholder="Enter a topic, idea, or trend..."
              className="input-glow flex-1 px-5 py-4 text-lg"
              disabled={isLoading}
            />
            <button
              onClick={handleGenerate}
              disabled={isLoading || !topic.trim()}
              className="btn-primary px-8 py-4 text-lg whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                  Generating...
                </span>
              ) : (
                '🚀 Generate'
              )}
            </button>
          </div>
        </div>

        {/* Options toggle */}
        <button
          onClick={() => setShowOptions(!showOptions)}
          className="mt-3 text-sm text-white/40 hover:text-white/70 transition-colors flex items-center gap-1 mx-auto"
        >
          ⚙️ {showOptions ? 'Hide' : 'Show'} options
        </button>

        {/* Options drawer */}
        {showOptions && (
          <div className="glass-card p-6 mt-3 grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <label className="text-xs text-white/40 mb-1 block">Community</label>
              <select value={community} onChange={(e) => setCommunity(e.target.value)} className="input-glow w-full px-3 py-2 text-sm">
                {COMMUNITY_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-white/40 mb-1 block">Tone</label>
              <select value={tone} onChange={(e) => setTone(e.target.value)} className="input-glow w-full px-3 py-2 text-sm">
                {TONE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-white/40 mb-1 block">Language</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value)} className="input-glow w-full px-3 py-2 text-sm">
                {LANGUAGE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-white/40 mb-1 block">Duration</label>
              <select value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="input-glow w-full px-3 py-2 text-sm">
                {DURATION_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-white/40 mb-1 block">Visual Style</label>
              <select value={style} onChange={(e) => setStyle(e.target.value)} className="input-glow w-full px-3 py-2 text-sm">
                {STYLE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Trending topics */}
      {trends.length > 0 && (
        <div className="w-full max-w-2xl">
          <p className="text-xs text-white/30 mb-3 text-center">🔥 Trending now</p>
          <div className="flex flex-wrap justify-center gap-2">
            {trends.slice(0, 8).map((trend, i) => (
              <button
                key={i}
                onClick={() => setTopic(trend.title)}
                className="chip"
                title={`Source: ${trend.source}`}
              >
                {trend.title.length > 50 ? trend.title.slice(0, 50) + '...' : trend.title}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Features grid */}
      <div className="w-full max-w-4xl mt-20 grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { icon: '🧠', title: 'Multi-Agent AI', desc: '12-stage pipeline with research, scripting, and self-critiquing quality gate' },
          { icon: '🔄', title: 'Never Fails', desc: 'Triple fallback on every provider — Gemini → Groq → Ollama for LLM' },
          { icon: '💰', title: '₹0 Per Video', desc: '100% free-tier stack. No credit card. No limits on creativity.' },
        ].map((f, i) => (
          <div key={i} className="glass-card p-6 text-center">
            <div className="text-3xl mb-3">{f.icon}</div>
            <h3 className="font-semibold text-white mb-1">{f.title}</h3>
            <p className="text-sm text-white/40">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
