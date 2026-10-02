'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import { getJob, getVideoUrl, getExportUrl, type JobResponse, type StageInfo } from '@/lib/api';
import { subscribeToJob, type SSEEvent } from '@/lib/sse';
import { STAGE_NAMES, STAGE_LABELS, STAGE_ICONS, type StageName } from '@/lib/types';

export default function JobPage() {
  const { id } = useParams() as { id: string };
  const [job, setJob] = useState<JobResponse | null>(null);
  const [logs, setLogs] = useState<{ id: number; timestamp: string; level: string; stage: string; message: string }[]>([]);
  const [isLive, setIsLive] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Initial load
  useEffect(() => {
    getJob(id)
      .then(data => {
        setJob(data);
        if (data.status === 'completed' || data.status === 'failed') {
          setIsLive(false);
        }
      })
      .catch(console.error);
  }, [id]);

  // SSE Subscription
  useEffect(() => {
    if (!isLive) return;

    let logId = 0;
    const cleanup = subscribeToJob(id, (event: SSEEvent) => {
      if (event.type === 'log') {
        setLogs(prev => [...prev, { id: logId++, ...(event.data as { level: string; stage: string; message: string }), timestamp: event.timestamp }]);
      } else if (
        ['stage_start', 'stage_complete', 'stage_failed', 'job_complete', 'job_failed', 'reconnect'].includes(event.type)
      ) {
        getJob(id).then(setJob).catch(console.error);

        if (event.type === 'job_complete' || event.type === 'job_failed') {
          setIsLive(false);
        }
      }
    });

    return cleanup;
  }, [id, isLive]);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  if (!job) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 rounded-full animate-spin" style={{
            border: '3px solid hsla(258, 100%, 65%, 0.15)',
            borderTopColor: 'var(--accent)',
          }} />
          <p style={{ color: 'var(--text-muted)' }}>Loading pipeline...</p>
        </div>
      </div>
    );
  }

  const getStageStatus = (stageName: string): StageInfo['status'] => {
    const stage = job.stages.find(s => s.name === stageName);
    if (stage) return stage.status;
    if (job.current_stage === stageName) return 'running';
    return 'pending';
  };

  const getStageDuration = (stageName: string): string => {
    const stage = job.stages.find(s => s.name === stageName);
    if (stage && stage.duration_ms) {
      return `${(stage.duration_ms / 1000).toFixed(1)}s`;
    }
    return '';
  };

  const completedStages = STAGE_NAMES.filter(s => getStageStatus(s) === 'completed').length;
  const progressPercent = job.status === 'completed'
    ? 100
    : Math.max(3, (completedStages / STAGE_NAMES.length) * 100);

  const statusClass =
    job.status === 'completed' ? 'completed' :
    job.status === 'failed' ? 'failed' :
    job.status === 'processing' ? 'processing' : 'queued';

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">

      {/* ── Header ──────────────────────────────────────────── */}
      <div className="mb-8 animate-fade-up">
        <div className="flex items-start gap-4 mb-1">
          <div>
            <div className="flex items-center gap-3 mb-1.5">
              <h1 className="font-display text-2xl md:text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {job.brief.topic}
              </h1>
              <span className={`status-badge ${statusClass}`}>
                {job.status === 'processing' && (
                  <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: 'var(--accent-light)' }} />
                )}
                {job.status}
              </span>
            </div>
            <p className="text-sm font-mono" style={{ color: 'var(--text-muted)' }}>
              Job ID: {job.id}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* ── Left: Pipeline ────────────────────────────────── */}
        <div className="lg:col-span-2 space-y-6">

          {/* Progress Card */}
          <div className="glass-card p-6 animate-fade-up delay-100">
            <div className="flex items-center justify-between mb-5">
              <h2 className="font-display font-semibold text-base" style={{ color: 'var(--text-primary)' }}>
                Pipeline Progress
              </h2>
              {job.status === 'processing' && (
                <span className="flex items-center gap-2 text-xs font-medium" style={{ color: 'var(--accent-light)' }}>
                  <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: 'var(--accent)' }} />
                  Live
                </span>
              )}
              {job.status === 'completed' && (
                <span className="flex items-center gap-2 text-xs font-medium" style={{ color: 'var(--success)' }}>
                  ✓ Complete
                </span>
              )}
            </div>

            {/* Progress Bar */}
            <div className="progress-track mb-6">
              <div
                className={`progress-fill ${job.status === 'processing' ? 'active' : ''}`}
                style={{ width: `${progressPercent}%` }}
              />
            </div>

            {/* Stage List */}
            <div className="space-y-2">
              {STAGE_NAMES.map((stageName) => {
                const status = getStageStatus(stageName);
                const duration = getStageDuration(stageName);

                return (
                  <div key={stageName} className={`stage-item ${status}`}>
                    {/* Icon */}
                    <div className="w-10 flex justify-center text-base">
                      {status === 'completed' ? (
                        <span style={{ color: 'var(--success)' }}>✓</span>
                      ) : status === 'failed' ? (
                        <span style={{ color: 'var(--error)' }}>✗</span>
                      ) : status === 'running' ? (
                        <div className="w-4 h-4 rounded-full animate-spin" style={{
                          border: '2px solid hsla(258, 100%, 65%, 0.2)',
                          borderTopColor: 'var(--accent)',
                        }} />
                      ) : (
                        <span>{STAGE_ICONS[stageName]}</span>
                      )}
                    </div>

                    {/* Name */}
                    <div className="flex-1 text-sm font-medium" style={{
                      color: status === 'pending' ? 'var(--text-muted)' : 'var(--text-primary)',
                    }}>
                      {STAGE_LABELS[stageName]}
                    </div>

                    {/* Duration */}
                    {duration && (
                      <div className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
                        {duration}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Logs */}
          <div className="glass-card p-6 animate-fade-up delay-200">
            <h2 className="font-display font-semibold text-base mb-4" style={{ color: 'var(--text-primary)' }}>
              Live Logs
            </h2>
            <div className="log-console">
              {logs.length === 0 ? (
                <div className="italic" style={{ color: 'var(--text-muted)' }}>Waiting for pipeline events...</div>
              ) : (
                logs.map(log => (
                  <div key={log.id} className={`log-line ${log.level}`}>
                    <span style={{ color: 'var(--text-muted)' }}>[{new Date(log.timestamp).toLocaleTimeString()}]</span>{' '}
                    <span style={{ color: 'var(--accent-light)' }}>[{log.stage}]</span>{' '}
                    <span>{log.message}</span>
                  </div>
                ))
              )}
              <div ref={logsEndRef} />
            </div>
          </div>
        </div>

        {/* ── Right: Preview ────────────────────────────────── */}
        <div className="space-y-6">
          <div className="glass-card p-6 sticky top-24 animate-fade-up delay-200">
            <h2 className="font-display font-semibold text-base mb-6 text-center" style={{ color: 'var(--text-primary)' }}>
              Final Output
            </h2>

            <div className="flex flex-col items-center">
              <div className="phone-frame mb-6 float">
                {job.status === 'completed' && job.video_url ? (
                  <video
                    src={getVideoUrl(job.id)}
                    controls
                    autoPlay
                    loop
                    className="w-full h-full object-cover"
                  />
                ) : job.status === 'failed' ? (
                  <div className="w-full h-full flex flex-col items-center justify-center p-6 text-center" style={{
                    background: 'hsla(0, 40%, 10%, 0.8)',
                  }}>
                    <span className="text-3xl mb-3">⚠️</span>
                    <p className="text-sm font-medium" style={{ color: 'var(--error)' }}>Pipeline Failed</p>
                    <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>{job.error || 'Unknown error'}</p>
                  </div>
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center relative overflow-hidden" style={{
                    background: 'linear-gradient(180deg, hsla(258, 30%, 8%, 1), hsla(240, 20%, 4%, 1))',
                  }}>
                    <div className="absolute inset-0" style={{
                      background: 'radial-gradient(circle at 50% 40%, hsla(258, 80%, 50%, 0.1), transparent 60%)',
                    }} />
                    <div className="w-12 h-12 rounded-full animate-spin mb-4 relative z-10" style={{
                      border: '3px solid hsla(258, 100%, 65%, 0.15)',
                      borderTopColor: 'var(--accent)',
                    }} />
                    <p className="text-sm font-medium relative z-10" style={{ color: 'var(--text-secondary)' }}>
                      Forging video...
                    </p>
                    <p className="text-xs mt-2 relative z-10" style={{ color: 'var(--text-muted)' }}>
                      This takes ~1-2 minutes
                    </p>
                  </div>
                )}
              </div>

              {job.status === 'completed' && (
                <div className="w-full space-y-3">
                  <a
                    href={getExportUrl(job.id)}
                    download
                    className="btn-primary w-full flex items-center justify-center gap-2 py-3.5"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download Export Pack
                  </a>
                  <p className="text-xs text-center" style={{ color: 'var(--text-muted)' }}>
                    Includes MP4, thumbnail, caption & hashtags
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
