\# LinguaType — Project Architecture & Specification

\#\# 1\. Overview  
Fast, gamified translation and sentence construction trainer inspired by Monkeytype.  
Key performance goal: End-to-end evaluation latency under 3 seconds.

\---

\#\# 2\. Core Game Loop  
1\. User receives a prompt:  
   \- Mode A: Short source sentence (native language) to translate.  
   \- Mode B: Image/situation description (describe the context directly in target language).  
2\. User selects session constraints:  
   \- Time limit: 15s / 30s / 60s.  
   \- Word limit: Target length \+ margin buffer (e.g. required \~10 words, capped at 15 words max).  
3\. Input mechanics:  
   \- Free input: Standard text input with real-time word counter and live timer.  
   \- Scaffolding mode (optional beginner assist): Word-by-word / guided assembly.  
4\. Evaluation & Feedback (\< 3s):  
   \- User submission sent via WebSocket / HTTP streaming.  
   \- Grammar error highlighting directly on user text.  
   \- Meaning validation: Semantic match (loose phrasing allowed if core idea is preserved).  
   \- Exactly ONE optimized alternative sentence based on user preference (Casual/Conversational, Formal/Literary, Concise, etc.).  
   \- Speed metrics: WPM, time taken, accuracy score.

\---

\#\# 3\. Low-Latency Architecture (\< 3s Target)

\#\#\# 3.1 Latency Breakdown & Budget  
\- Network RTT (Client \-\> Backend): \~100-200ms  
\- Backend Processing & Validation: \~50ms  
\- LLM Time to First Token (TTFT): \~400-800ms (using fast models like Gemini Flash / GPT-4o-mini)  
\- LLM Token Generation: \~600-1200ms (strict JSON output, \<= 100 tokens total)  
\- Response Delivery & UI Render: \~150ms  
\- Total: \~1.5s \- 2.5s (safely under the 3-second ceiling).

\#\#\# 3.2 Optimization Strategies  
\- Pre-warmed backend connections & keep-alive to LLM provider endpoints.  
\- Structured JSON Schema / constrained decoding to eliminate parsing overhead and output bloat.  
\- Caching prompt stems and system prompts via provider context caching.  
\- Fallback heuristic check: Instant local regex/spellcheck while waiting for semantic LLM response.

\---

\#\# 4\. System Components

\#\#\# Frontend (Forked from Monkeytype core)  
\- Framework: TypeScript, Vite / React / Next.js  
\- State Management: Lightweight store (Zustand)  
\- UI: Minimalist dark theme, keyboard-first navigation (Tab+Enter to restart, Esc to reset)  
\- Communication: SSE or WebSocket for streaming evaluation results instantly

\#\#\# Backend API  
\- Framework: FastAPI (Python) or Fastify (Node.js) for high-throughput asynchronous handling.  
\- Auth Service:  
  \- Google OAuth 2.0  
  \- Magic Link / Email Passwordless  
  \- Persistent refresh tokens in secure HttpOnly cookies (auto-login after initial setup)  
\- Prompt Engine:  
  \- Curated database of situational prompts, paired with reference embeddings.  
  \- Image prompts served via CDN.  
\- Evaluation Service:  
  \- Calls fast LLM endpoint with strict temperature (0.1 \- 0.2).  
  \- Validates meaning preservation, extracts grammar error spans, and formats a single stylistic alternative.

\---

\#\# 5\. Data Model

\#\#\# Users  
\- \`id\`: UUID  
\- \`email\`: String (unique)  
\- \`native\_language\`: String (e.g., "ru", "uz")  
\- \`target\_language\`: String (e.g., "en")  
\- \`preferred\_style\`: Enum ("conversational", "formal", "concise")  
\- \`allow\_loose\_phrasing\`: Boolean (default: true)  
\- \`created\_at\`: Timestamp

\#\#\# Prompts  
\- \`id\`: UUID  
\- \`type\`: Enum ("translation", "situation\_image")  
\- \`source\_language\`: String  
\- \`target\_language\`: String  
\- \`content\`: Text (or image\_url)  
\- \`difficulty\`: Enum ("easy", "medium", "hard")  
\- \`target\_word\_count\`: Integer

\#\#\# Game Results  
\- \`id\`: UUID  
\- \`user\_id\`: UUID  
\- \`prompt\_id\`: UUID  
\- \`user\_text\`: Text  
\- \`time\_spent\_ms\`: Integer  
\- \`wpm\`: Float  
\- \`accuracy\_score\`: Integer (0-100)  
\- \`grammar\_errors\`: JSON  
\- \`recommended\_variant\`: Text  
\- \`created\_at\`: Timestamp

\---

\#\# 6\. Development Roadmap  
\- Phase 1: Minimal headless prototype (FastAPI \+ LLM structured evaluation endpoint, bench latency).  
\- Phase 2: Monkeytype UI strip-down & custom input layer (timer \+ word budget counter).  
\- Phase 3: Auth integration (Google OAuth \+ Magic Link \+ Profile language settings).  
\- Phase 4: Game modes (timed vs word limit, translation vs image prompt).  
\- Phase 5: Feedback card UI (inline grammar highlights \+ style variant).  
