"use client";
import { useState } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    setLoading(true);
    setAnswer("");
    setSources([]);

    const res = await fetch("http://localhost:8000/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();
    setAnswer(data.answer);
    setSources(data.sources || []);
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-gray-50 p-10 text-gray-800">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">Perplexity-Style Assistant</h1>
        <div className="flex gap-2">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask me anything..."
            className="flex-1 p-3 border border-gray-300 rounded shadow-sm"
          />
          <button
            onClick={ask}
            disabled={!question || loading}
            className="bg-blue-600 text-white px-5 py-3 rounded disabled:opacity-50"
          >
            Ask
          </button>
        </div>

        {loading && <p className="mt-4 text-blue-600">Thinking...</p>}

        {answer && (
          <div className="mt-6 bg-white p-4 rounded shadow">
            <h2 className="text-xl font-semibold mb-2">Answer:</h2>
            <p>{answer}</p>

            <h3 className="text-md font-semibold mt-4">Sources:</h3>
            <ul className="list-disc ml-6 mt-2 text-sm">
              {sources.map((url, i) => (
                <li key={i}>
                  <a href={url} className="text-blue-500 underline" target="_blank" rel="noreferrer">
                    {url}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </main>
  );
}
