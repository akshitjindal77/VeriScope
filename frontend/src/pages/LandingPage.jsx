import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Shield, Brain, FileText } from 'lucide-react';

const sampleResponse = `{
  "status": "success",
  "answer": "RAG (Retrieval-Augmented Generation) is an AI
  framework that combines retrieval systems with LLMs [1][2].
  It fetches relevant documents at inference time, allowing
  models to cite sources and stay up-to-date [3].",
  "citations": [
    { "title": "What is RAG? - AWS", "confidence": 0.95 },
    { "title": "RAG Explained - NVIDIA", "confidence": 0.91 },
    { "title": "RAG Survey - arXiv", "confidence": 0.88 }
  ],
  "confidence": 0.93
}`;

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

function CodeBlock() {
  const lines = sampleResponse.split('\n');
  return (
    <div className="rounded-xl border border-gray-700 bg-gray-900 text-left overflow-hidden text-sm font-mono">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-800 bg-gray-800/50">
        <div className="w-3 h-3 rounded-full bg-red-500/70" />
        <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
        <div className="w-3 h-3 rounded-full bg-green-500/70" />
        <span className="ml-2 text-gray-500 text-xs">response.json</span>
      </div>
      <div className="p-4 space-y-0.5">
        {lines.map((line, i) => (
          <div key={i} className="leading-relaxed">
            {line.includes('"') ? (
              <span>
                {line.split(/(\"[^\"]*\")/).map((part, j) =>
                  part.startsWith('"') ? (
                    <span key={j} className={line.indexOf(part) < line.indexOf(':') + 2 && line.includes(':') ? 'text-blue-400' : 'text-green-400'}>
                      {part}
                    </span>
                  ) : (
                    <span key={j} className="text-gray-400">{part}</span>
                  )
                )}
              </span>
            ) : (
              <span className="text-gray-500">{line}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

const features = [
  { icon: Search, title: 'Smart Query Analysis', desc: 'AI analyzes your question, detects ambiguity, and generates targeted search queries — not generic templates.' },
  { icon: Shield, title: 'Source Quality Scoring', desc: 'Every source is scored by domain authority and relevance. Only the highest-quality sources reach synthesis.' },
  { icon: Brain, title: 'Deep Reasoning Mode', desc: 'Optional ReAct agent loop that reasons step-by-step, searches multiple angles, and self-corrects.' },
  { icon: FileText, title: 'Cited Answers', desc: 'Every claim is backed by numbered sources with confidence scores. No hallucination, only evidence.' },
];

const steps = [
  { n: 1, title: 'Ask Your Question', desc: 'Type any research question. VeriScope handles ambiguity automatically.' },
  { n: 2, title: 'Sources Are Found & Scored', desc: 'Multiple search queries find diverse sources. Each is scored for quality.' },
  { n: 3, title: 'AI Synthesizes the Answer', desc: 'A local LLM writes a coherent narrative with inline citations.' },
  { n: 4, title: 'Get Cited Results', desc: 'Receive a comprehensive answer with source links and confidence scores.' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 to-gray-900 text-white">
      <Navbar />

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-36 pb-24 text-center">
        <motion.h1
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}
          className="text-5xl md:text-6xl font-bold leading-tight mb-6"
        >
          Research Smarter,{' '}
          <span className="bg-gradient-to-r from-white to-blue-400 bg-clip-text text-transparent">Not Harder</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.1 }}
          className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto mb-10"
        >
          AI-powered research engine that searches the web, analyzes sources, and synthesizes cited answers — with intelligent query understanding and deep reasoning.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }}
          className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
        >
          <Link to="/signup" className="bg-gradient-to-r from-blue-600 to-blue-500 text-white px-8 py-3 rounded-lg font-medium hover:from-blue-500 hover:to-blue-400 transition-all shadow-lg shadow-blue-500/25">
            Start Researching →
          </Link>
          <a href="#features" className="border border-gray-700 text-gray-300 px-8 py-3 rounded-lg font-medium hover:border-gray-500 hover:text-white transition-all">
            See How It Works ↓
          </a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.3 }}
          className="max-w-2xl mx-auto"
        >
          <div className="text-xs text-gray-500 mb-2 text-left px-1">Query: "What is RAG?"</div>
          <CodeBlock />
        </motion.div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-6xl mx-auto px-6 py-24">
        <motion.h2
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="text-3xl font-bold text-center mb-12"
        >
          Built for Serious Research
        </motion.h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map(({ icon: Icon, title, desc }, i) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10 transition-all"
            >
              <Icon className="text-blue-400 mb-4" size={24} />
              <h3 className="text-white font-semibold text-lg mb-2">{title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How It Works */}
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

      {/* CTA */}
      <section className="max-w-6xl mx-auto px-6 py-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="rounded-2xl border border-blue-500/30 bg-gradient-to-br from-gray-900 to-gray-800 p-12 text-center shadow-xl shadow-blue-500/10"
        >
          <h2 className="text-3xl font-bold mb-3">Ready to Research?</h2>
          <p className="text-gray-400 mb-8">Start using VeriScope for free. No credit card required.</p>
          <Link to="/signup" className="inline-block bg-gradient-to-r from-blue-600 to-blue-500 text-white px-8 py-3 rounded-lg font-medium hover:from-blue-500 hover:to-blue-400 transition-all shadow-lg shadow-blue-500/25">
            Get Started →
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 text-center">
        <p className="text-gray-500 text-sm mb-1">Built by Akshit Jindal • University of the Fraser Valley</p>
        <p className="text-gray-600 text-xs">Powered by Mistral 7B • Brave Search API • FastAPI</p>
      </footer>
    </div>
  );
}
