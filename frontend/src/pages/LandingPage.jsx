import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Check, Loader2, ArrowRight, ChevronDown, ChevronRight,
  FileText, Newspaper, Brain, BarChart3, Scale, ShieldCheck,
} from 'lucide-react';
import { CardSwap, Card } from '../components/CardSwap';

// ── Navbar ────────────────────────────────────────────────────────────────────
function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);
  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-gray-950/95 backdrop-blur border-b border-gray-800' : 'bg-transparent'}`}>
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <span className="text-xl font-bold text-white" style={{ textShadow: '0 0 20px rgba(59,130,246,0.5)' }}>
          VeriScope
        </span>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-gray-400 hover:text-white transition-colors px-4 py-2 text-sm">
            Log In
          </Link>
          <Link to="/signup" className="bg-gradient-to-r from-blue-600 to-blue-500 text-white text-sm px-4 py-2 rounded-lg hover:from-blue-500 hover:to-blue-400 transition-all">
            Get Started
          </Link>
        </div>
      </div>
    </nav>
  );
}

// ── Claim Checker ─────────────────────────────────────────────────────────────
const CLAIM_TEXT = "Does cold water boil faster?";

const SCAN_STEPS = [
  { id: 1, icon: Search,    text: "Scanning sources...",      color: "text-blue-400"   },
  { id: 2, icon: BarChart3, text: "Comparing claims...",      color: "text-purple-400" },
  { id: 3, icon: Scale,     text: "Evaluating confidence...", color: "text-amber-400"  },
];

function ClaimChecker() {
  const [typedText, setTypedText]      = useState('');
  const [currentStep, setCurrentStep]  = useState(0); // 0=typing, 1-3=scan steps, 4=result
  const [completedSteps, setCompleted] = useState([]);
  const intervalRef = useRef(null);
  const timeoutsRef = useRef([]);

  const addTimeout = (fn, ms) => {
    const t = setTimeout(fn, ms);
    timeoutsRef.current.push(t);
    return t;
  };

  useEffect(() => {
    addTimeout(() => {
      let i = 0;
      intervalRef.current = setInterval(() => {
        i++;
        setTypedText(CLAIM_TEXT.slice(0, i));
        if (i >= CLAIM_TEXT.length) {
          clearInterval(intervalRef.current);
          addTimeout(() => setCurrentStep(1), 1000);
        }
      }, 50);
    }, 1500);

    return () => {
      timeoutsRef.current.forEach(clearTimeout);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (currentStep >= 1 && currentStep <= 3) {
      const t = setTimeout(() => {
        setCompleted(prev => [...prev, currentStep]);
        setCurrentStep(prev => prev + 1);
      }, 800);
      return () => clearTimeout(t);
    }
  }, [currentStep]);

  return (
    <div className="mt-12 max-w-2xl mx-auto">
      {/* Glass input panel */}
      <div className="bg-gray-900/60 backdrop-blur-xl border border-gray-700/50 rounded-2xl px-4 py-3 md:px-6 md:py-4 flex items-center gap-3 ring-1 ring-blue-500/20">
        <Search size={18} className="text-gray-500 flex-shrink-0" />
        <span className="text-gray-300 text-sm flex-1 min-h-[20px] text-left">
          {typedText}
          {currentStep === 0 && typedText.length > 0 && typedText.length < CLAIM_TEXT.length && (
            <span className="inline-block w-0.5 h-4 bg-blue-400 animate-pulse ml-0.5 align-middle" />
          )}
        </span>
      </div>

      {/* Scanning steps */}
      <AnimatePresence>
        {currentStep >= 1 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 space-y-2"
          >
            {SCAN_STEPS.map(({ id, icon: Icon, text, color }) => {
              if (currentStep < id) return null;
              const isDone = completedSteps.includes(id);
              return (
                <motion.div
                  key={id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center gap-3 px-2"
                >
                  {isDone
                    ? <Check size={16} className="text-emerald-400 flex-shrink-0" />
                    : <Loader2 size={16} className={`${color} animate-spin flex-shrink-0`} />
                  }
                  <span className={`text-sm ${isDone ? 'text-gray-500' : color}`}>{text}</span>
                </motion.div>
              );
            })}

            {/* Final result */}
            {currentStep >= 4 && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mt-4 flex items-center gap-3 px-3 py-2.5 rounded-xl bg-emerald-500/5 border border-emerald-500/20"
              >
                <Check size={16} className="text-emerald-400 flex-shrink-0" />
                <span className="text-sm text-emerald-400 font-medium">
                  Mostly True — 73% confidence across 8 sources
                </span>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── Truth Lens visualization ──────────────────────────────────────────────────
function TruthLens() {
  const analysisItems = [
    { dot: 'bg-emerald-400', text: 'Verified: AI is automating some job categories', color: 'text-emerald-400', delay: 0.5 },
    { dot: 'bg-amber-400',   text: "Unclear: 'Replacing' is overly broad",           color: 'text-amber-400',   delay: 0.8 },
    { dot: 'bg-red-400',     text: 'Misleading: Specific timeframe varies by industry', color: 'text-red-400', delay: 1.1 },
  ];

  return (
    <div className="mt-20 max-w-4xl mx-auto px-2" id="truth-lens">
      <style>{`
        @keyframes scanline {
          0%   { transform: translateY(0); }
          100% { transform: translateY(280px); }
        }
      `}</style>

      {/* ── Desktop 3-column ── */}
      <div className="hidden lg:flex items-start gap-0">

        {/* Left: Raw Input */}
        <motion.div
          className="w-1/3"
          initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: 0.6 }}
        >
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Raw Claim</p>
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
            <p className="text-gray-300 text-sm leading-relaxed">
              Is{' '}
              <motion.span
                className="border-b-2 border-blue-400"
                initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
                viewport={{ once: true }} transition={{ delay: 0.6 }}
              >AI</motion.span>
              {' '}
              <motion.span
                className="border-b-2 border-amber-400"
                initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
                viewport={{ once: true }} transition={{ delay: 0.85 }}
              >replacing jobs</motion.span>
              {' in '}
              <motion.span
                className="border-b-2 border-blue-400"
                initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
                viewport={{ once: true }} transition={{ delay: 1.1 }}
              >2026</motion.span>
              ?
            </p>
          </div>
        </motion.div>

        {/* Arrow */}
        <div className="flex items-center self-center mx-2 flex-shrink-0 mt-6">
          <ChevronRight size={20} className="text-gray-700" />
        </div>

        {/* Center: Analysis Lens */}
        <motion.div
          className="w-1/3"
          initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: 0.6, delay: 0.2 }}
        >
          <p className="text-xs text-blue-400 uppercase tracking-wider mb-3">VeriScope Analysis</p>
          <div className="bg-blue-500/5 border border-blue-500/20 rounded-xl p-5 relative overflow-hidden min-h-[160px]">
            {/* Scan line */}
            <div
              className="absolute left-0 right-0 h-px"
              style={{
                top: 0,
                background: 'linear-gradient(90deg, transparent, rgba(96,165,250,0.5), transparent)',
                animation: 'scanline 3s linear infinite',
              }}
            />
            {/* Content above scan line */}
            <div className="relative z-10">
              {analysisItems.map(({ dot, text, color, delay }, i) => (
                <motion.div
                  key={i}
                  className="flex items-start gap-2 mt-2 first:mt-0"
                  initial={{ opacity: 0, x: -10 }} whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }} transition={{ delay }}
                >
                  <span className={`w-2 h-2 rounded-full ${dot} flex-shrink-0 mt-1`} />
                  <span className={`text-xs ${color}`}>{text}</span>
                </motion.div>
              ))}
              <motion.p
                className="text-xs text-gray-500 mt-3"
                initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
                viewport={{ once: true }} transition={{ delay: 1.4 }}
              >
                8 sources analyzed
              </motion.p>
            </div>
          </div>
        </motion.div>

        {/* Arrow */}
        <div className="flex items-center self-center mx-2 flex-shrink-0 mt-6">
          <ChevronRight size={20} className="text-gray-700" />
        </div>

        {/* Right: Verified Output */}
        <motion.div
          className="w-1/3"
          initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: 0.6, delay: 0.4 }}
        >
          <p className="text-xs text-emerald-400 uppercase tracking-wider mb-3">Result</p>
          <div className="bg-gray-900/50 border border-emerald-500/20 rounded-xl p-5">
            <div className="flex items-center gap-2">
              <Check size={20} className="text-emerald-400 flex-shrink-0" />
              <span className="text-emerald-400 font-medium text-sm">Partially True</span>
            </div>
            <p className="text-amber-400 text-xs mt-3">2 conflicting claims found</p>
            <div className="mt-4">
              <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-emerald-400"
                  initial={{ width: '0%' }}
                  whileInView={{ width: '73%' }}
                  viewport={{ once: true }}
                  transition={{ duration: 1.5, ease: 'easeOut' }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1.5">Confidence: 73%</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* ── Mobile simplified card ── */}
      <div className="lg:hidden">
        <p className="text-xs text-gray-500 text-center mb-3">Sample Analysis</p>
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <Check size={18} className="text-emerald-400 flex-shrink-0" />
            <span className="text-emerald-400 font-medium text-sm">Partially True — 73% confidence</span>
          </div>
          <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-emerald-400"
              initial={{ width: '0%' }}
              whileInView={{ width: '73%' }}
              viewport={{ once: true }}
              transition={{ duration: 1.5, ease: 'easeOut' }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Static data ───────────────────────────────────────────────────────────────

const steps = [
  { n: 1, title: 'Ask Your Question',          desc: 'Type any research question. VeriScope handles ambiguity automatically.' },
  { n: 2, title: 'Sources Are Found & Scored', desc: 'Multiple search queries find diverse sources. Each is scored for quality.' },
  { n: 3, title: 'AI Synthesizes the Answer',  desc: 'A local LLM writes a coherent narrative with inline citations.' },
  { n: 4, title: 'Get Cited Results',          desc: 'Receive a comprehensive answer with source links and confidence scores.' },
];

const trustItems = [
  { icon: FileText,  label: 'Research Papers' },
  { icon: Newspaper, label: 'News Sources'    },
  { icon: Brain,     label: 'AI Models'       },
  { icon: BarChart3, label: 'Data Analysis'   },
];

// ── Landing Page ──────────────────────────────────────────────────────────────
export default function LandingPage() {
  const [ctaPulse, setCtaPulse] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => {
      setCtaPulse(true);
      const t2 = setTimeout(() => setCtaPulse(false), 1000);
      return () => clearTimeout(t2);
    }, 6500);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 to-gray-900 text-white">
      <Navbar />

      {/* ═══════════════════════════════ HERO ═══════════════════════════════ */}
      <section className="max-w-6xl mx-auto px-6 pt-32 pb-8 text-center">

        {/* Part 1 — Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-5xl md:text-6xl lg:text-7xl font-bold"
          style={{
            background: 'linear-gradient(to right, #ffffff, #dbeafe, #93c5fd)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          See Through the Noise.
        </motion.h1>

        {/* Part 1 — Subheading */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-6 max-w-2xl mx-auto text-base md:text-lg text-gray-400 leading-relaxed text-center"
        >
          VeriScope analyzes, compares, and verifies information across sources — so you don't have to guess what's real.
        </motion.p>

        {/* Part 2 — Claim Checker */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <ClaimChecker />
        </motion.div>

        {/* Part 3 — CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-10 flex flex-col sm:flex-row gap-4 justify-center"
        >
          <motion.div
            whileHover={{ scale: 1.02 }}
            animate={ctaPulse ? { scale: [1, 1.04, 1] } : {}}
            transition={ctaPulse ? { duration: 0.5 } : {}}
          >
            <Link
              to="/signup"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-500 text-white font-medium px-8 py-3.5 rounded-xl hover:from-blue-500 hover:to-blue-400 transition-all shadow-lg shadow-blue-500/25"
            >
              Analyze a Claim
              <ArrowRight size={16} />
            </Link>
          </motion.div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            animate={ctaPulse ? { scale: [1, 1.04, 1] } : {}}
            transition={ctaPulse ? { duration: 0.5, delay: 0.05 } : {}}
            onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
            className="inline-flex items-center gap-2 border border-gray-700 text-gray-300 hover:text-white hover:border-gray-500 px-8 py-3.5 rounded-xl transition-all"
          >
            See How It Works
            <ChevronDown size={16} />
          </motion.button>
        </motion.div>

        {/* Part 4 — Truth Lens */}
        <TruthLens />

        {/* Part 5 — Trust Strip */}
        <div className="mt-20 mb-16">
          <p className="text-sm text-gray-600 text-center mb-6">Powered by multi-source verification</p>
          <div className="flex flex-wrap justify-center gap-x-10 gap-y-4">
            {trustItems.map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex items-center gap-2 opacity-50 hover:opacity-100 transition-opacity duration-300"
              >
                <Icon size={16} className="text-gray-600" />
                <span className="text-xs text-gray-600">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ════════════════════════════ FEATURES ══════════════════════════════ */}
      <section id="features" className="max-w-6xl mx-auto px-6 py-24">
        <motion.h2
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="text-3xl font-bold text-center mb-12"
        >
          Built for Serious Research
        </motion.h2>

        {/* CardSwap container */}
        <div className="flex items-center justify-center py-20 relative">
          {/* Ambient glow */}
          <div className="absolute w-96 h-96 rounded-full bg-blue-500/5 blur-3xl pointer-events-none" />

          {/* Offset padding to accommodate card stacking spread */}
          <div className="pt-10 pb-20 px-10 flex items-center justify-center">
            <CardSwap
              width={550}
              height={350}
              cardDistance={40}
              verticalDistance={40}
              delay={4500}
              pauseOnHover={true}
              skewAmount={4}
              easing="elastic"
            >
              {/* Card 1 — Smart Query Analysis */}
              <Card className="p-0 overflow-hidden">
                <div className="w-full h-full rounded-xl bg-gradient-to-br from-gray-800/80 to-gray-900/80 p-8 flex flex-col">
                  <Search size={28} className="text-blue-400" />
                  <h3 className="text-white text-xl font-semibold mt-4">Smart Query Analysis</h3>
                  <p className="text-gray-400 text-sm mt-2 leading-relaxed">
                    AI analyzes your question, detects ambiguity, and generates targeted search queries — not generic templates.
                  </p>
                  <div className="mt-4 flex items-center gap-2 flex-wrap">
                    <span className="bg-gray-800 rounded-full px-3 py-1 text-xs text-gray-300">
                      "What is RAG?"
                    </span>
                    <span className="text-gray-600 text-xs">→</span>
                    <span className="bg-blue-500/10 rounded-full px-3 py-1 text-xs text-blue-300">
                      Retrieval-Augmented Generation
                    </span>
                  </div>
                </div>
              </Card>

              {/* Card 2 — Source Quality Scoring */}
              <Card className="p-0 overflow-hidden">
                <div className="w-full h-full rounded-xl bg-gradient-to-br from-gray-800/80 to-gray-900/80 p-8 flex flex-col">
                  <ShieldCheck size={28} className="text-emerald-400" />
                  <h3 className="text-white text-xl font-semibold mt-4">Source Quality Scoring</h3>
                  <p className="text-gray-400 text-sm mt-2 leading-relaxed">
                    Every source is scored by domain authority and relevance. Only the highest-quality sources reach synthesis.
                  </p>
                  <div className="mt-4 space-y-1">
                    {[
                      { dot: 'bg-emerald-400', label: 'aws.amazon.com',  score: '0.92', scoreColor: 'text-emerald-400', strike: false },
                      { dot: 'bg-emerald-400', label: 'arxiv.org',       score: '0.88', scoreColor: 'text-emerald-400', strike: false },
                      { dot: 'bg-red-400',     label: 'random-blog.com', score: '0.31', scoreColor: 'text-red-400',     strike: true  },
                    ].map(({ dot, label, score, scoreColor, strike }) => (
                      <div key={label} className="flex items-center gap-2 text-xs">
                        <span className={`w-1.5 h-1.5 rounded-full ${dot} flex-shrink-0`} />
                        <span className={`flex-1 text-gray-400 ${strike ? 'line-through opacity-50' : ''}`}>{label}</span>
                        <span className={scoreColor}>{score}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>

              {/* Card 3 — Deep Reasoning Mode */}
              <Card className="p-0 overflow-hidden">
                <div className="w-full h-full rounded-xl bg-gradient-to-br from-gray-800/80 to-gray-900/80 p-8 flex flex-col">
                  <Brain size={28} className="text-purple-400" />
                  <h3 className="text-white text-xl font-semibold mt-4">Deep Reasoning Mode</h3>
                  <p className="text-gray-400 text-sm mt-2 leading-relaxed">
                    Optional ReAct agent loop that reasons step-by-step, searches multiple angles, and self-corrects.
                  </p>
                  <div className="mt-4 space-y-1.5">
                    <p className="text-xs text-gray-500">→ Step 1: Analyzing query...</p>
                    <p className="text-xs text-gray-500">→ Step 2: Searching 3 angles...</p>
                    <p className="text-xs text-gray-500">→ Step 3: Synthesizing answer...</p>
                    <p className="text-xs text-purple-400 font-medium mt-2">✓ Complete in 5 steps</p>
                  </div>
                </div>
              </Card>

              {/* Card 4 — Cited Answers */}
              <Card className="p-0 overflow-hidden">
                <div className="w-full h-full rounded-xl bg-gradient-to-br from-gray-800/80 to-gray-900/80 p-8 flex flex-col">
                  <FileText size={28} className="text-amber-400" />
                  <h3 className="text-white text-xl font-semibold mt-4">Cited Answers</h3>
                  <p className="text-gray-400 text-sm mt-2 leading-relaxed">
                    Every claim is backed by numbered sources with confidence scores. No hallucination, only evidence.
                  </p>
                  <div className="mt-4">
                    <p className="text-xs text-gray-300 leading-relaxed">
                      RAG is a technique that{' '}
                      <span className="bg-blue-500/20 text-blue-400 text-xs px-1.5 py-0.5 rounded font-mono">[1]</span>
                      {' '}optimizes LLM output by{' '}
                      <span className="bg-blue-500/20 text-blue-400 text-xs px-1.5 py-0.5 rounded font-mono">[2]</span>
                      {' '}referencing external knowledge.
                    </p>
                    <div className="mt-3">
                      <div className="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
                        <div className="h-full w-[82%] bg-emerald-400 rounded-full" />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">Confidence: 82%</p>
                    </div>
                  </div>
                </div>
              </Card>
            </CardSwap>
          </div>
        </div>

        <p className="text-xs text-gray-600 text-center mt-4">
          Hover to pause • Auto-cycles every 4.5s
        </p>
      </section>

      {/* ══════════════════════════ HOW IT WORKS ════════════════════════════ */}
      <section className="max-w-6xl mx-auto px-6 py-24">
        <motion.h2
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="text-3xl font-bold text-center mb-16"
        >
          How VeriScope Works
        </motion.h2>
        <div className="max-w-xl mx-auto space-y-8">
          {steps.map(({ n, title, desc }, i) => (
            <motion.div
              key={n}
              initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="flex gap-5"
            >
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-600 to-blue-500 flex items-center justify-center font-bold text-sm shadow-lg shadow-blue-500/30">
                {n}
              </div>
              <div>
                <h3 className="text-white font-semibold mb-1">{title}</h3>
                <p className="text-gray-400 text-sm">{desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════ CTA ═════════════════════════════════ */}
      <section className="max-w-6xl mx-auto px-6 py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="rounded-2xl border border-blue-500/30 bg-gradient-to-br from-gray-900 to-gray-800 p-12 text-center shadow-xl shadow-blue-500/10"
        >
          <h2 className="text-3xl font-bold mb-3">Ready to Research?</h2>
          <p className="text-gray-400 mb-8">Start using VeriScope for free. No credit card required.</p>
          <Link
            to="/signup"
            className="inline-block bg-gradient-to-r from-blue-600 to-blue-500 text-white px-8 py-3 rounded-lg font-medium hover:from-blue-500 hover:to-blue-400 transition-all shadow-lg shadow-blue-500/25"
          >
            Get Started →
          </Link>
        </motion.div>
      </section>

      {/* ════════════════════════════ FOOTER ════════════════════════════════ */}
      <footer className="border-t border-gray-800 py-8 text-center">
        <p className="text-gray-500 text-sm mb-1">Built by Akshit Jindal • University of the Fraser Valley</p>
        <p className="text-gray-600 text-xs">Powered by Mistral 7B • Brave Search API • FastAPI</p>
      </footer>
    </div>
  );
}
