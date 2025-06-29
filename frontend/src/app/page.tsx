"use client";
import { useState, useRef } from "react";
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { TypewriterEffect } from "@/components/ui/typewriter-effect";
import { BackgroundGradient } from "@/components/ui/background-gradient";
import { HoverEffect } from "@/components/ui/card-hover-effect";
import { TextGenerateEffect } from "@/components/ui/text-generate-effect";
import { SparklesCore } from "@/components/ui/sparkles";
import { motion } from "framer-motion";

export default function HomePage() {
  const { isLoggedIn, logout } = useAuth();
  const router = useRouter();
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [followUpQuestions, setFollowUpQuestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const [lastRequestTime, setLastRequestTime] = useState(0);
  const [mode, setMode] = useState<'ultra' | 'serp' | 'deep'>('ultra');
  const [status, setStatus] = useState<string>('');

  const words = [
    {
      text: "Ask",
    },
    {
      text: "anything.",
    },
    {
      text: "Get",
    },
    {
      text: "intelligent",
      className: "text-blue-500 dark:text-blue-500",
    },
    {
      text: "answers.",
      className: "text-blue-500 dark:text-blue-500",
    },
  ];

  const features = [
    {
      title: "Smart Search",
      description: "Advanced AI algorithms provide accurate and relevant results with contextual understanding.",
      link: "#smart-search",
    },
    {
      title: "Fast Results",
      description: "Get instant answers with lightning-fast response times powered by cutting-edge technology.",
      link: "#fast-results",
    },
    {
      title: "Secure & Private",
      description: "Your data is protected with enterprise-grade security and privacy-first approach.",
      link: "#secure-private",
    },
  ];

  const ask = async (questionToAsk?: string, requestMode: 'ultra' | 'serp' | 'deep' = 'ultra') => {
    const currentQuestion = questionToAsk || question;
    if (!currentQuestion.trim()) return;

    // Debounce requests (prevent spam)
    const now = Date.now();
    if (now - lastRequestTime < 1000) {
      console.log("Request debounced");
      return;
    }
    setLastRequestTime(now);

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setLoading(true);
    setAnswer("");
    setSources([]);
    setFollowUpQuestions([]);
    setStatus("");
    setMode(requestMode);

    const endpointMap = {
      'ultra': '/ask',
      'serp': '/ask-serp',
      'deep': '/ask-deep'
    };
    const endpoint = endpointMap[requestMode];

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "text/event-stream"
        },
        body: JSON.stringify({ question: currentQuestion }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || ""; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") {
              setLoading(false);
              break;
            }
            
            try {
              const parsed = JSON.parse(data);
              switch (parsed.type) {
                case 'mode':
                  setMode(parsed.mode);
                  break;
                case 'status':
                  setStatus(parsed.message);
                  break;
                case 'urls':
                  setSources(parsed.urls);
                  break;
                case 'answer':
                  setAnswer(prev => prev + parsed.content);
                  setStatus(""); // Clear status when answer starts
                  break;
                case 'follow_up_questions':
                  setFollowUpQuestions(parsed.questions); 
                  break;
                case 'error':
                  setAnswer(parsed.content);
                  setLoading(false);
                  break;
              }
            } catch (e) {
              console.error("Error parsing JSON:", e, "Data:", data);
            }
          }
        }
      }
    } catch (error: unknown) {
      if (error instanceof Error && error.name === "AbortError") {
        console.log("Request aborted");
      } else {
        console.error("Error:", error);
        setAnswer("An error occurred while fetching the answer. Please try again.");
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleFollowUpClick = (followUpQuestion: string) => {
    setQuestion(followUpQuestion);
    ask(followUpQuestion, mode); // Follow-ups use the same mode as the current question
  };

  const handleLogin = () => {
    router.push('/login');
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-black dark:bg-black relative overflow-hidden">
      {/* Sparkles Background */}
      <div className="w-full absolute inset-0 h-screen">
        <SparklesCore
          id="tsparticlesfullpage"
          background="transparent"
          minSize={0.6}
          maxSize={1.4}
          particleDensity={100}
          className="w-full h-full"
          particleColor="#FFFFFF"
        />
      </div>

      {/* Navigation Bar */}
      <nav className="relative z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center"
            >
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Top3URL.ai
              </h1>
            </motion.div>

            {/* Auth Status */}
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-4"
            >
              {isLoggedIn ? (
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-sm text-gray-300">Logged in</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
                    <span className="text-sm text-gray-400">Not logged in</span>
                  </div>
                  <button
                    onClick={handleLogin}
                    className="bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 border border-blue-500/30 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                  >
                    Login
                  </button>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative z-40 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          {/* Hero Section with Typewriter */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8"
          >
            <TypewriterEffect words={words} className="text-4xl md:text-6xl font-bold" />
          </motion.div>
          
          <TextGenerateEffect 
            words="Get intelligent answers to your questions with our advanced AI search technology" 
            className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto"
          />
        </div>

        {/* Search Interface */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-12"
        >
          <BackgroundGradient className="rounded-[22px] p-1 bg-white dark:bg-zinc-900">
            <div className="bg-black rounded-[20px] p-8">
              <div className="space-y-4 mb-6">
                <input
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask me anything..."
                  className="w-full p-4 bg-zinc-900/50 border border-zinc-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-white placeholder-gray-400 text-lg backdrop-blur-sm"
                  onKeyDown={(e) => e.key === "Enter" && !loading && question.trim() && ask()}
                />
                
                <div className="grid grid-cols-3 gap-3">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => ask(undefined, 'ultra')}
                    disabled={!question.trim() || loading}
                    className="bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-all duration-200 text-sm flex items-center justify-center gap-2"
                  >
                    <span>🚀</span>
                    <div className="text-center">
                      <div>{loading && mode === 'ultra' ? "Thinking..." : "Ultra Fast"}</div>
                      <div className="text-xs opacity-75">(1-2s)</div>
                    </div>
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => ask(undefined, 'serp')}
                    disabled={!question.trim() || loading}
                    className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-all duration-200 text-sm flex items-center justify-center gap-2"
                  >
                    <span>⚡</span>
                    <div className="text-center">
                      <div>{loading && mode === 'serp' ? "Searching..." : "Web Search"}</div>
                      <div className="text-xs opacity-75">(3-5s)</div>
                    </div>
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => ask(undefined, 'deep')}
                    disabled={!question.trim() || loading}
                    className="bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-all duration-200 text-sm flex items-center justify-center gap-2"
                  >
                    <span>🔍</span>
                    <div className="text-center">
                      <div>{loading && mode === 'deep' ? "Deep Diving..." : "Deep Dive"}</div>
                      <div className="text-xs opacity-75">(10-20s)</div>
                    </div>
                  </motion.button>
                </div>
                
                {status && (
                  <div className="text-center text-sm text-blue-400 animate-pulse">
                    {status}
                  </div>
                )}
              </div>

              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center justify-center py-8"
                >
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  <span className="ml-3 text-blue-400 font-medium">Thinking...</span>
                </motion.div>
              )}

              {answer && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="border-t border-zinc-700 pt-6"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <h3 className="text-xl font-semibold text-white">Answer:</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      mode === 'ultra' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                      mode === 'serp' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                      mode === 'deep' ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' :
                      'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                    }`}>
                      {mode === 'ultra' ? '🚀 Ultra Fast' :
                       mode === 'serp' ? '⚡ Web Search' :
                       mode === 'deep' ? '🔍 Deep Dive' : mode}
                    </span>
                  </div>
                  <div className="prose prose-lg prose-invert max-w-none">
                    <p className="whitespace-pre-wrap text-gray-300 leading-relaxed">{answer}</p>
                  </div>
                  
                  {sources.length > 0 && (
                    <div className="mt-6">
                      <h4 className="text-lg font-semibold text-white mb-3">Sources:</h4>
                      <div className="space-y-2">
                        {sources.map((url, i) => (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="flex items-center space-x-2"
                          >
                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                            <a 
                              href={url} 
                              className="text-blue-400 hover:text-blue-300 hover:underline text-sm" 
                              target="_blank" 
                              rel="noreferrer"
                            >
                              {url}
                            </a>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  )}

                  {mode === 'ultra' && sources.length === 0 && (
                    <div className="mt-6">
                      <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                        <div className="flex items-center gap-2">
                          <span className="text-yellow-400">💡</span>
                          <p className="text-yellow-200 text-sm">
                            This answer is based on my training data. For the most current information, try <strong>Web Search</strong> or <strong>Deep Dive</strong> mode.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {followUpQuestions.length > 0 && (
                    <div className="mt-6">
                      <div className="flex items-center gap-2 mb-3">
                        <h4 className="text-lg font-semibold text-white">Follow-up Questions:</h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          mode === 'ultra' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                          mode === 'serp' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                          mode === 'deep' ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' :
                          'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                        }`}>
                          Will use {mode === 'ultra' ? '🚀 Ultra Fast' :
                                   mode === 'serp' ? '⚡ Web Search' :
                                   mode === 'deep' ? '🔍 Deep Dive' : mode} mode
                        </span>
                      </div>
                      <div className="space-y-2">
                        {followUpQuestions.map((followUpQuestion, i) => (
                          <motion.button
                            key={i}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            whileHover={{ scale: 1.02 }}
                            onClick={() => handleFollowUpClick(followUpQuestion)}
                            className="block w-full text-left p-3 bg-zinc-800/50 hover:bg-zinc-700/50 rounded-lg border border-zinc-700 transition-all duration-200"
                          >
                            <span className="text-blue-400 hover:text-blue-300 text-sm font-medium">
                              {followUpQuestion}
                            </span>
                          </motion.button>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </div>
          </BackgroundGradient>
        </motion.div>

        {/* Features Section - Only show when no search results */}
        {!answer && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <HoverEffect items={features} />
          </motion.div>
        )}

        {/* Login Prompt for Non-authenticated Users */}
        {!isLoggedIn && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mt-12"
          >
            <BackgroundGradient className="rounded-[22px] p-1">
              <div className="bg-black rounded-[20px] p-6 text-center">
                <h3 className="text-lg font-semibold text-white mb-2">
                  Get the Full Experience
                </h3>
                <p className="text-gray-400 mb-4">
                  Sign in to save your search history and get personalized results
                </p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleLogin}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-6 py-2 rounded-lg font-medium transition-all duration-200"
                >
                  Sign In Now
                </motion.button>
              </div>
            </BackgroundGradient>
          </motion.div>
        )}
      </main>
    </div>
  );
}
