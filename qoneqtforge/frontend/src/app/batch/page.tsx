'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createBatch } from '@/lib/api';
import { COMMUNITY_OPTIONS, TONE_OPTIONS, LANGUAGE_OPTIONS, DURATION_OPTIONS, STYLE_OPTIONS } from '@/lib/types';

export default function BatchPage() {
  const router = useRouter();
  const [topicsInput, setTopicsInput] = useState('');
  const [community, setCommunity] = useState('general');
  const [tone, setTone] = useState('energetic');
  const [language, setLanguage] = useState('en');
  const [duration, setDuration] = useState(30);
  const [style, setStyle] = useState('cinematic');
  const [isLoading, setIsLoading] = useState(false);
  const [batchResult, setBatchResult] = useState<{ job_ids: string[]; count: number } | null>(null);

  const topicsList = topicsInput
    .split('\n')
    .map(t => t.trim())
    .filter(t => t.length > 0);

  const handleGenerateBatch = async () => {
    if (topicsList.length === 0) return;
    setIsLoading(true);

    try {
      const result = await createBatch(topicsList, {
        community,
        tone: tone as any,
        language: language as any,
        duration_sec: duration as any,
        visual_style: style,
      });
      setBatchResult(result);
    } catch (error) {
      console.error('Failed to create batch:', error);
      alert('Failed to create batch jobs.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold mb-4">Batch Production</h1>
        <p className="text-white/50">
          Queue multiple topics at once. The QoneqtForge orchestrator will process them in parallel up to the concurrency limit.
        </p>
      </div>

      {!batchResult ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Left: Topics Input */}
          <div className="md:col-span-2 glass-card p-6">
            <h2 className="text-lg font-semibold mb-2">Topics List</h2>
            <p className="text-sm text-white/40 mb-4">Enter one topic per line (max 10 for best performance).</p>
            
            <textarea
              value={topicsInput}
              onChange={(e) => setTopicsInput(e.target.value)}
              placeholder="1. The history of artificial intelligence&#10;2. How black holes work&#10;3. Top 5 startup hubs in 2026..."
              className="input-glow w-full h-64 p-4 text-sm font-mono resize-none mb-4"
              disabled={isLoading}
            />
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-white/40">
                {topicsList.length} topic{topicsList.length !== 1 ? 's' : ''} detected
              </span>
              <button
                onClick={handleGenerateBatch}
                disabled={isLoading || topicsList.length === 0}
                className="btn-primary"
              >
                {isLoading ? 'Queueing...' : `Queue ${topicsList.length} Videos`}
              </button>
            </div>
          </div>

          {/* Right: Settings */}
          <div className="glass-card p-6 h-fit">
            <h2 className="text-lg font-semibold mb-6">Shared Settings</h2>
            
            <div className="space-y-4">
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
          </div>
        </div>
      ) : (
        /* Success State */
        <div className="glass-card p-10 text-center max-w-2xl mx-auto">
          <div className="w-16 h-16 bg-success/20 text-success rounded-full flex items-center justify-center text-3xl mx-auto mb-6 glow">
            ✓
          </div>
          <h2 className="text-2xl font-bold mb-2">Batch Queued Successfully!</h2>
          <p className="text-white/50 mb-8">
            {batchResult.count} videos have been sent to the orchestrator. They will be processed in the background.
          </p>
          
          <div className="space-y-3 mb-8 text-left max-w-sm mx-auto">
            {batchResult.job_ids.map((id, index) => (
              <a 
                key={id}
                href={`/jobs/${id}`}
                target="_blank"
                rel="noreferrer"
                className="block p-3 rounded-lg border border-white/10 hover:border-accent hover:bg-white/5 transition-colors flex justify-between items-center group"
              >
                <span className="font-medium">Video {index + 1}</span>
                <span className="text-sm font-mono text-white/40 group-hover:text-accent-light">
                  {id} ↗
                </span>
              </a>
            ))}
          </div>
          
          <button 
            onClick={() => {
              setBatchResult(null);
              setTopicsInput('');
            }}
            className="btn-secondary"
          >
            Queue Another Batch
          </button>
        </div>
      )}
    </div>
  );
}
