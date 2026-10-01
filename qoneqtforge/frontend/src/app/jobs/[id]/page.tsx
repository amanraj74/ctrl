'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import { getJob, getVideoUrl, getExportUrl, type JobResponse, type StageInfo } from '@/lib/api';
import { subscribeToJob, type SSEEvent } from '@/lib/sse';
import { STAGE_NAMES, STAGE_LABELS, type StageName } from '@/lib/types';

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
        setLogs(prev => [...prev, { id: logId++, ...event.data, timestamp: event.timestamp }]);
      } else if (
        ['stage_start', 'stage_complete', 'stage_failed', 'job_complete', 'job_failed'].includes(event.type)
      ) {
        // Refresh job state on major events
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
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-white/50">Loading job details...</p>
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

  const progressPercent = Math.max(
    5,
    Math.min(100, (STAGE_NAMES.findIndex(s => s === job.current_stage) + 1) / STAGE_NAMES.length * 100)
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold text-white">Pipeline: {job.brief.topic}</h1>
          <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
            job.status === 'completed' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
            job.status === 'failed' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
            'bg-accent/20 text-accent-light border border-accent/30 pulse-glow'
          }`}>
            {job.status.toUpperCase()}
          </span>
        </div>
        <p className="text-white/50 text-sm font-mono">ID: {job.id}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Pipeline Stages */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold mb-6 flex items-center justify-between">
              <span>Pipeline Progress</span>
              {job.status === 'processing' && (
                <span className="text-sm font-normal text-accent-light flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-accent animate-ping"></span> Live
                </span>
              )}
            </h2>

            {/* Progress Bar */}
            <div className="w-full h-2 bg-white/5 rounded-full mb-8 overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-accent-dark to-accent-light transition-all duration-500 ease-out relative"
                style={{ width: `${job.status === 'completed' ? 100 : progressPercent}%` }}
              >
                {job.status === 'processing' && (
                  <div className="absolute top-0 right-0 bottom-0 left-0 bg-[linear-gradient(90deg,transparent,rgba(255,255,255,0.3),transparent)] bg-[length:200%_100%] animate-[shimmer_2s_infinite]" />
                )}
              </div>
            </div>

            {/* Stage List */}
            <div className="space-y-4">
              {STAGE_NAMES.map((stageName, idx) => {
                const status = getStageStatus(stageName);
                const duration = getStageDuration(stageName);
                
                return (
                  <div key={stageName} className={`flex items-center p-3 rounded-lg border transition-all duration-300 ${
                    status === 'running' ? 'bg-accent/10 border-accent/30 glow' :
                    status === 'completed' ? 'bg-white/5 border-white/10 opacity-80' :
                    status === 'failed' ? 'bg-red-500/10 border-red-500/30' :
                    'border-transparent opacity-40'
                  }`}>
                    {/* Status Icon */}
                    <div className="w-10 flex justify-center">
                      {status === 'completed' ? <span className="text-green-400">✓</span> :
                       status === 'failed' ? <span className="text-red-400">✗</span> :
                       status === 'running' ? (
                         <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin"></div>
                       ) : <span className="text-white/20">{idx + 1}</span>}
                    </div>

                    {/* Stage Name */}
                    <div className="flex-1 font-medium text-white/90">
                      {STAGE_LABELS[stageName]}
                    </div>

                    {/* Duration */}
                    {duration && (
                      <div className="text-sm font-mono text-white/40">
                        {duration}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Logs */}
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold mb-4">Live Logs</h2>
            <div className="log-console">
              {logs.length === 0 ? (
                <div className="text-white/30 italic">Waiting for logs...</div>
              ) : (
                logs.map(log => (
                  <div key={log.id} className={`log-line ${log.level}`}>
                    <span className="text-white/30 mr-2">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                    <span className="text-white/50 mr-2">[{log.stage}]</span>
                    <span>{log.message}</span>
                  </div>
                ))
              )}
              <div ref={logsEndRef} />
            </div>
          </div>
        </div>

        {/* Right Column: Result / Preview */}
        <div className="space-y-6">
          <div className="glass-card p-6 sticky top-24">
            <h2 className="text-lg font-semibold mb-6 text-center">Final Output</h2>
            
            <div className="flex flex-col items-center">
              <div className="phone-frame mb-6">
                {job.status === 'completed' && job.video_url ? (
                  <video 
                    src={getVideoUrl(job.id)} 
                    controls 
                    autoPlay 
                    loop
                    className="w-full h-full object-cover"
                  />
                ) : job.status === 'failed' ? (
                  <div className="w-full h-full flex items-center justify-center bg-red-950/20 text-red-400 p-6 text-center">
                    Pipeline Failed
                    <br />
                    {job.error || 'Unknown error'}
                  </div>
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center bg-black/50 p-6 text-center relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-t from-accent/20 to-transparent opacity-50" />
                    <div className="w-12 h-12 border-4 border-accent/30 border-t-accent rounded-full animate-spin mb-4 relative z-10" />
                    <p className="text-sm text-white/50 relative z-10 font-medium">Forging Video...</p>
                    <p className="text-xs text-white/30 mt-2 relative z-10">This takes ~1-2 minutes</p>
                  </div>
                )}
              </div>

              {job.status === 'completed' && (
                <div className="w-full space-y-3">
                  <a 
                    href={getExportUrl(job.id)}
                    download
                    className="btn-primary w-full flex items-center justify-center gap-2 py-3"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download Export Pack
                  </a>
                  <p className="text-xs text-center text-white/40">Includes MP4, thumbnail, caption & hashtags</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
