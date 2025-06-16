🧠 Perplexity Clone – AI-Powered Search Assistant

This project is a full-stack clone of Perplexity.ai, a conversational search engine that combines real-time web search with AI to provide accurate, source-backed answers.

🚀 Features
• Real-time web search using SerpAPI
• Intelligent text extraction from web pages using boilerpy3
• Semantic search using FAISS vector store
• Real-time answer streaming with OpenAI's GPT-4
• Source citations for all answers
• Modern, responsive UI with Next.js
• Efficient embedding caching for faster responses

🔧 Tech Stack
• Frontend:
  - Next.js 15 with TypeScript
  - Tailwind CSS for styling
  - Real-time streaming with Server-Sent Events

• Backend:
  - FastAPI for high-performance API
  - OpenAI GPT-4 for answer generation
  - FAISS for semantic search
  - SerpAPI for web search
  - boilerpy3 for web scraping
  - Embedding caching for performance

🎯 Key Features
• Real-time answer streaming for better UX
• Semantic search to find most relevant content
• Efficient caching of embeddings
• Source-backed answers with clickable citations
• Modern, responsive UI with dark mode support

🚀 Getting Started

1. Clone the repository
2. Set up environment variables:
   ```
   OPENAI_API_KEY=your_openai_key
   SERPAPI_KEY=your_serpapi_key
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```bash
   cd perplexity-ui
   npm install
   ```

5. Run the development servers:
   ```bash
   # Terminal 1 - Backend
   uvicorn backend.main:app --reload

   # Terminal 2 - Frontend
   cd perplexity-ui
   npm run dev
   ```

6. Open http://localhost:3000 in your browser

🔍 How It Works
1. User asks a question
2. System searches the web using SerpAPI
3. Relevant pages are scraped and processed
4. Content is chunked and embedded
5. Semantic search finds most relevant chunks
6. GPT-4 generates a streaming answer
7. Sources are provided for verification

