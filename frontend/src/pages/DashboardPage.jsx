import { useState, useEffect, useRef, useCallback } from 'react';
import { Plus, Menu, X, LogOut, Search, Trash2, MessageSquare } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { researchAPI, sessionAPI } from '../services/api';
import RadiantPromptInput from '../components/RadiantPromptInput';
import StreamingStatus from '../components/StreamingStatus';
import AnswerCard from '../components/AnswerCard';

// ── Helpers ────────────────────────────────────────────────────────────────

function groupSessionsByDate(sessions) {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const yesterday = new Date(today); yesterday.setDate(yesterday.getDate() - 1);
  const weekAgo = new Date(today); weekAgo.setDate(weekAgo.getDate() - 7);

  const groups = { Today: [], Yesterday: [], 'Previous 7 Days': [], Older: [] };
  for (const s of sessions) {
    const d = new Date(s.updated_at || s.created_at);
    d.setHours(0, 0, 0, 0);
    if (d >= today) groups.Today.push(s);
    else if (d >= yesterday) groups.Yesterday.push(s);
    else if (d >= weekAgo) groups['Previous 7 Days'].push(s);
    else groups.Older.push(s);
  }
  return groups;
}

// ── Sub-components ──────────────────────────────────────────────────────────

function SkeletonBar({ w = 'w-full' }) {
  return <div className={`h-4 ${w} bg-gray-800 rounded animate-pulse`} />;
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <div className="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mb-4">
        <Search className="text-gray-600" size={28} />
      </div>
      <p className="text-gray-500 text-lg">What would you like to research?</p>
      <p className="text-gray-600 text-sm mt-2">Type a question below to get started</p>
    </div>
  );
}

function QueryBubble({ prompt, mode }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-lg bg-gray-800 rounded-xl px-4 py-3">
        <p className="text-white text-sm">{prompt}</p>
        <span className={`text-xs mt-1 inline-block ${mode === 'react' ? 'text-purple-400' : 'text-blue-400'}`}>
          {mode === 'react' ? '🧠 Deep' : '⚡ Fast'}
        </span>
      </div>
    </div>
  );
}

function ErrorBubble({ message, onRetry }) {
  return (
    <div className="flex justify-center">
      <div className="bg-red-900/30 border border-red-800 rounded-xl px-4 py-3 text-center max-w-md">
        <p className="text-red-400 text-sm mb-2">{message}</p>
        {onRetry && (
          <button onClick={onRetry} className="text-xs text-gray-400 hover:text-white transition-colors underline">
            Try again
          </button>
        )}
      </div>
    </div>
  );
}

function Toast({ message, onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 5000);
    return () => clearTimeout(t);
  }, [onClose]);

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-red-900 border border-red-700 text-red-200 text-sm px-4 py-3 rounded-lg shadow-lg flex items-center gap-3">
      {message}
      <button onClick={onClose} className="text-red-400 hover:text-white"><X size={14} /></button>
    </div>
  );
}

function Sidebar({ isOpen, onClose, sessions, loadingSessions, onNewSession, onSelectSession, onDeleteSession, currentSessionId, user, onLogout }) {
  const groups = groupSessionsByDate(sessions);

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black/60 z-30 md:hidden" onClick={onClose} />
      )}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-40 w-72 bg-gray-900 border-r border-gray-800
        flex flex-col transform transition-transform duration-200 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          <span className="text-white font-bold text-lg">VeriScope</span>
          <button onClick={onClose} className="md:hidden text-gray-400 hover:text-white"><X size={20} /></button>
        </div>

        <div className="p-3">
          <button
            onClick={onNewSession}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-blue-500 text-white py-2.5 rounded-lg text-sm font-medium hover:from-blue-500 hover:to-blue-400 transition-all"
          >
            <Plus size={16} /> New Research
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-4">
          {loadingSessions ? (
            <div className="space-y-2 pt-2">
              {[80, 60, 70, 50].map((w, i) => <SkeletonBar key={i} w={`w-[${w}%]`} />)}
            </div>
          ) : sessions.length === 0 ? (
            <div className="flex flex-col items-center py-8 text-center">
              <MessageSquare size={24} className="text-gray-700 mb-2" />
              <p className="text-gray-600 text-xs">No previous research</p>
            </div>
          ) : (
            Object.entries(groups).map(([label, items]) =>
              items.length === 0 ? null : (
                <div key={label}>
                  <p className="text-gray-600 text-xs font-medium mb-1 px-1">{label}</p>
                  <div className="space-y-0.5">
                    {items.map((session) => (
                      <div key={session.id} className="group relative">
                        <button
                          onClick={() => onSelectSession(session.id)}
                          className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-all truncate pr-8 ${
                            currentSessionId === session.id
                              ? 'bg-gray-800 text-white border-l-2 border-blue-500'
                              : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                          }`}
                        >
                          {(session.title || 'Untitled').slice(0, 30)}
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); onDeleteSession(session.id); }}
                          className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition-all"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )
            )
          )}
        </div>

        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center justify-between">
            <div className="min-w-0">
              <p className="text-white text-sm font-medium truncate">{user?.username || 'User'}</p>
              <p className="text-gray-500 text-xs truncate">{user?.email}</p>
            </div>
            <button onClick={onLogout} className="text-gray-400 hover:text-red-400 transition-colors p-1 rounded ml-2" title="Log out">
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}

// ── Main ────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [loadingSession, setLoadingSession] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isResearching, setIsResearching] = useState(false);
  const [streamingStages, setStreamingStages] = useState([]);
  const [currentMode, setCurrentMode] = useState('linear');
  const [toast, setToast] = useState(null);
  const bottomRef = useRef(null);
  const lastPromptRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Load sessions on mount
  useEffect(() => {
    sessionAPI.list()
      .then((res) => setSessions(res.data || []))
      .catch(() => {})
      .finally(() => setLoadingSessions(false));
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        handleNewSession();
      }
      if (e.key === 'Escape') setSidebarOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingStages]);

  const refreshSessions = useCallback(() => {
    sessionAPI.list().then((res) => setSessions(res.data || [])).catch(() => {});
  }, []);

  const handleNewSession = () => {
    setCurrentSessionId(null);
    setMessages([]);
    setStreamingStages([]);
    setSidebarOpen(false);
  };

  const handleSelectSession = async (id) => {
    setSidebarOpen(false);
    setLoadingSession(true);
    setCurrentSessionId(id);
    setMessages([]);
    try {
      const res = await sessionAPI.get(id);
      const queries = res.data.queries || [];
      const loaded = queries.flatMap((q) => {
        const items = [{ type: 'query', prompt: q.prompt, mode: q.mode }];
        let citations = [];
        try { citations = JSON.parse(q.citations_json || '[]'); } catch {}
        items.push({
          type: 'result',
          data: {
            answer: q.answer,
            citations,
            confidence: q.confidence,
            query_type: q.query_type,
            resolved_meaning: q.resolved_meaning,
            react_steps: q.react_steps,
            duration_seconds: q.duration_seconds,
          },
        });
        return items;
      });
      setMessages(loaded);
    } catch {
      setToast('Failed to load session.');
    } finally {
      setLoadingSession(false);
    }
  };

  const handleDeleteSession = async (id) => {
    try {
      await sessionAPI.delete(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (currentSessionId === id) handleNewSession();
    } catch {
      setToast('Failed to delete session.');
    }
  };

  const handleStop = () => {
    abortControllerRef.current?.abort();
    setIsResearching(false);
    setStreamingStages([]);
  };

  const handleSubmit = async (prompt, mode) => {
    lastPromptRef.current = { prompt, mode };
    const controller = new AbortController();
    abortControllerRef.current = controller;
    setIsResearching(true);
    setStreamingStages([]);
    setMessages((prev) => [...prev, { type: 'query', prompt, mode }]);

    try {
      const token = localStorage.getItem('veriscope_token');
      const response = await fetch('/api/research/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ prompt, mode, session_id: currentSessionId }),
        signal: controller.signal,
      });

      if (response.status === 401) {
        logout();
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            try {
              const event = JSON.parse(trimmed.slice(6));
              if (event.event === 'status') {
                setStreamingStages((prev) => [...prev, {
                  stage: event.stage,
                  message: event.message,
                  timestamp: Date.now(),
                }]);
              } else if (event.event === 'result') {
                setMessages((prev) => [...prev, { type: 'result', data: event.data }]);
                setCurrentSessionId(event.data.session_id);
                setIsResearching(false);
                setStreamingStages([]);
                refreshSessions();
              } else if (event.event === 'error') {
                setMessages((prev) => [...prev, { type: 'error', message: event.message }]);
                setIsResearching(false);
                setStreamingStages([]);
              }
            } catch {}
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        setIsResearching(false);
        setStreamingStages(prev => [...prev, { stage: 'cancelled', message: 'Research stopped by user', timestamp: Date.now() }]);
        return;
      }
      setIsResearching(false);
      setStreamingStages([]);
      setMessages((prev) => [...prev, { type: 'error', message: 'Research failed. Please try again.' }]);
    }
  };

  const handleRetry = () => {
    if (lastPromptRef.current) {
      setMessages((prev) => prev.filter((m) => m.type !== 'error'));
      handleSubmit(lastPromptRef.current.prompt, lastPromptRef.current.mode);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="flex h-screen bg-gray-950 overflow-hidden">
      {toast && <Toast message={toast} onClose={() => setToast(null)} />}

      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        sessions={sessions}
        loadingSessions={loadingSessions}
        onNewSession={handleNewSession}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        currentSessionId={currentSessionId}
        user={user}
        onLogout={logout}
      />

      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <header className="flex items-center gap-3 px-4 py-3 border-b border-gray-800 bg-gray-950 flex-shrink-0">
          <button onClick={() => setSidebarOpen(true)} className="md:hidden text-gray-400 hover:text-white transition-colors">
            <Menu size={20} />
          </button>
          <span className={`text-xs font-medium px-2 py-1 rounded-md ${
            currentMode === 'react'
              ? 'bg-purple-900/50 text-purple-400 border border-purple-800'
              : 'bg-blue-900/50 text-blue-400 border border-blue-800'
          }`}>
            {currentMode === 'react' ? '🧠 Deep Reasoning' : '⚡ Linear'}
          </span>
        </header>

        {/* Scrollable content */}
        <div className="flex-1 overflow-y-auto">
          {loadingSession ? (
            <div className="flex items-center justify-center h-full">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : messages.length === 0 && !isResearching ? (
            <EmptyState />
          ) : (
            <div className="max-w-3xl mx-auto px-4 py-6 pb-32 space-y-4">
              {messages.map((msg, i) => {
                if (msg.type === 'query') return <QueryBubble key={i} prompt={msg.prompt} mode={msg.mode} />;
                if (msg.type === 'result') return <AnswerCard key={i} result={msg.data} />;
                if (msg.type === 'error') return <ErrorBubble key={i} message={msg.message} onRetry={i === messages.length - 1 ? handleRetry : null} />;
                return null;
              })}

              {isResearching && streamingStages.length > 0 && (
                <div className="py-4 px-2">
                  <StreamingStatus stages={streamingStages} isComplete={false} mode={currentMode} />
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          )}
        </div>

        {/* Sticky search bar */}
        <div className="sticky bottom-0 p-4 pb-6 bg-gradient-to-t from-gray-950 via-gray-950/95 to-transparent pt-8">
          <RadiantPromptInput
            onSubmit={(prompt, mode) => { setCurrentMode(mode); handleSubmit(prompt, mode); }}
            onStop={handleStop}
            isResearching={isResearching}
            mode={currentMode}
            onModeToggle={() => setCurrentMode(prev => prev === 'linear' ? 'react' : 'linear')}
            placeholder="What would you like to research?"
            disabled={false}
          />
        </div>
      </div>
    </div>
  );
}
