"use client";
import { useState, useRef } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [followUpQuestions, setFollowUpQuestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const ask = async (questionToAsk?: string) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    const currentQuestion = questionToAsk || question;
    setLoading(true);
    setAnswer("");
    setSources([]);
    setFollowUpQuestions([]);

    try {
      const response = await fetch("http://localhost:8000/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: currentQuestion }),
        signal: abortControllerRef.current.signal,
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

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
                case 'urls':
                  setSources(parsed.urls);
                  break;
                case 'answer':
                  setAnswer(prev => prev + parsed.content);
                  break;
                case 'follow_up_questions':
                  setFollowUpQuestions(parsed.questions); 
                  break;
                case 'error':
                  setAnswer(parsed.content);
                  break;
              }
            } catch (e) {
              console.error("Error parsing JSON:", e);
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === "AbortError") {
        console.log("Request aborted");
      } else {
        console.error("Error:", error);
        setAnswer("An error occurred while fetching the answer.");
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleFollowUpClick = (followUpQuestion: string) => {
    setQuestion(followUpQuestion);
    ask(followUpQuestion);
  };

  return (
    <main className="min-h-screen bg-gray-50 p-10 text-gray-800">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">Perplexity Assistant</h1>
        <div className="flex gap-2">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask me anything..."
            className="flex-1 p-3 border border-gray-300 rounded shadow-sm"
            onKeyDown={(e) => e.key === "Enter" && !loading && ask()}
          />
          <button
            onClick={() => ask()}
            disabled={!question || loading}
            className="bg-blue-600 text-white px-5 py-3 rounded disabled:opacity-50"
          >
            {loading ? "Stop" : "Ask"}
          </button>
        </div>

        {loading && <p className="mt-4 text-blue-600">Thinking...</p>}

        {answer && (
          <div className="mt-6 bg-white p-4 rounded shadow">
            <h2 className="text-xl font-semibold mb-2">Answer:</h2>
            <p className="whitespace-pre-wrap">{answer}</p>
            
            {sources.length > 0 && (
              <>
                <h3 className="text-md font-semibold mt-4">Sources:</h3>
                <ul className="list-disc ml-6 mt-2 text-sm">
                  {sources.map((url, i) => (
                    <li key={i}>
                      <a href={url} className="text-blue-500 hover:underline" target="_blank" rel="noreferrer">
                        {url}
                      </a>
                    </li>
                  ))}
                </ul>
              </>
            )}

            {followUpQuestions.length > 0 && (
              <>
                <h3 className="text-md font-semibold mt-4">Follow-up Questions:</h3>
                <div className="mt-2 space-y-2">
                  {followUpQuestions.map((followUpQuestion, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <p className="text-blue-500 hover:text-blue-700 text-sm">{followUpQuestion}</p>
                      <button
                        onClick={() => handleFollowUpClick(followUpQuestion)}
                        className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-blue-600"
                      >
                        +
                      </button>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
