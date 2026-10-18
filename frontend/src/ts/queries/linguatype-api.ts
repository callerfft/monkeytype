import {
  setAllowLoosePhrasing,
  setPreferredStyle,
  type DifficultyOption,
  type GrammarErrorSpan,
  type LatencyBreakdown,
  type LinguaTypeMode,
  type LinguaTypePrompt,
  type SemanticValidation,
  type SessionMetrics,
  type StyleAlternative,
  type StyleOption,
  type TimerOption,
} from "../states/linguatype";
import { getIdToken, getUserState } from "../firebase";

export type SessionCreatePayload = {
  mode: LinguaTypeMode;
  timer_seconds: TimerOption;
  target_word_count: number;
  margin_buffer: number;
  source_language?: string;
  target_language?: string;
  difficulty?: DifficultyOption;
  input_mode?: "free" | "scaffolding";
  preferred_style?: StyleOption;
  allow_loose_phrasing?: boolean;
  check_case_and_period?: boolean;
};

export type SessionResponse = {
  session_id: string;
  status: "active" | "completed" | "cancelled" | "expired";
  mode: LinguaTypeMode;
  prompt: LinguaTypePrompt;
  timer_seconds: TimerOption;
  input_mode: "free" | "scaffolding";
  preferred_style: StyleOption;
  allow_loose_phrasing: boolean;
  check_case_and_period?: boolean;
  created_at: string;
  expires_at: string;
};

export type EvaluationRequestPayload = {
  user_text: string;
  time_spent_ms: number;
  words_typed: number;
  character_count?: number;
  keystroke_count?: number;
  check_case_and_period?: boolean;
};

export type ParsedSSEEvent = {
  event:
    | "session_start"
    | "token"
    | "grammar_errors"
    | "semantic_check"
    | "style_alternative"
    | "metrics"
    | "done"
    | "error"
    | string;
  data: unknown;
};

export type SSEParserState = {
  buffer: string;
  currentEvent: string;
  currentData: string;
};

export function createSSEParserState(): SSEParserState {
  return {
    buffer: "",
    currentEvent: "message",
    currentData: "",
  };
}

/**
 * Parses raw SSE chunk data progressively, preserving cross-chunk buffers.
 * Handles standard SSE formatting:
 * event: <name>
 * data: <payload>
 * [empty line signals event dispatch]
 */
export function parseSSEChunks(
  chunk: string,
  state: SSEParserState,
): ParsedSSEEvent[] {
  const events: ParsedSSEEvent[] = [];
  const text = state.buffer + chunk;
  const lines = text.split(/\r\n|\r|\n/);

  // The last element may be an incomplete line
  state.buffer = lines.pop() ?? "";

  for (const line of lines) {
    const trimmed = line.trim();

    if (trimmed === "") {
      // Empty line dispatches the accumulated event
      if (state.currentData !== "") {
        let parsedData: unknown = state.currentData;
        try {
          parsedData = JSON.parse(state.currentData);
        } catch {
          // If not valid JSON, pass raw string
          parsedData = state.currentData;
        }

        events.push({
          event: state.currentEvent,
          data: parsedData,
        });

        state.currentEvent = "message";
        state.currentData = "";
      }
      continue;
    }

    if (line.startsWith(":")) {
      // SSE comment / heartbeat - ignore
      continue;
    }

    if (line.startsWith("event:")) {
      state.currentEvent = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      const dataContent = line.slice(5).trim();
      if (state.currentData === "") {
        state.currentData = dataContent;
      } else {
        state.currentData = `${state.currentData}\n${dataContent}`;
      }
    }
  }

  return events;
}

/**
 * Normalizes grammar error span data from either array or object wrapper
 */
export function normalizeGrammarErrors(data: unknown): GrammarErrorSpan[] {
  if (Array.isArray(data)) {
    return data as GrammarErrorSpan[];
  }
  if (data !== null && typeof data === "object") {
    const errs: unknown = Reflect.get(data, "errors");
    if (Array.isArray(errs)) {
      return errs as GrammarErrorSpan[];
    }
  }

  return [];
}

export function getApiBaseUrl(): string {
  const envObj = import.meta.env as Record<string, unknown>;
  const customUrl = envObj["VITE_API_URL"];
  if (typeof customUrl === "string" && customUrl.length > 0) {
    return customUrl;
  }
  if (typeof window !== "undefined" && window.location?.origin) {
    const origin = window.location.origin;
    if (!origin.includes(":5173") && !origin.includes(":3000")) {
      return `${origin}/api/v1`;
    }
  }
  return "http://localhost:8000/api/v1";
}

export const API_BASE = getApiBaseUrl();

/**
 * Curated fallback prompts when backend server is unavailable
 */
export const FALLBACK_PROMPTS: Record<LinguaTypeMode, LinguaTypePrompt[]> = {
  translation: [
    {
      id: "fb-trans-easy",
      type: "translation",
      source_language: "ru",
      target_language: "en",
      content: "Я люблю пить горячий кофе ранним утром перед работой.",
      difficulty: "easy",
      target_word_count: 10,
      margin_buffer: 4,
      max_word_count: 14,
    },
    {
      id: "fb-trans-med",
      type: "translation",
      source_language: "ru",
      target_language: "en",
      content:
        "Технологии искусственного интеллекта стремительно меняют подход к решению сложных задач.",
      difficulty: "medium",
      target_word_count: 11,
      margin_buffer: 5,
      max_word_count: 16,
    },
    {
      id: "fb-trans-hard",
      type: "translation",
      source_language: "ru",
      target_language: "en",
      content:
        "Экономическая стабильность в условиях глобальной неопределенности требует взвешенных и стратегически выверенных решений.",
      difficulty: "hard",
      target_word_count: 13,
      margin_buffer: 6,
      max_word_count: 19,
    },
  ],
  situation_image: [
    {
      id: "fb-sit-easy",
      type: "situation_image",
      source_language: "en",
      target_language: "en",
      content:
        "You are ordering your favorite meal at a lively restaurant. Tell the waiter what you want and ask for a recommendation.",
      image_url:
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400",
      difficulty: "easy",
      target_word_count: 12,
      margin_buffer: 5,
      max_word_count: 17,
    },
    {
      id: "fb-sit-med",
      type: "situation_image",
      source_language: "en",
      target_language: "en",
      content:
        "You arrive at the airport and discover your flight was delayed by three hours. Express your reaction and next steps.",
      image_url:
        "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=400",
      difficulty: "medium",
      target_word_count: 14,
      margin_buffer: 6,
      max_word_count: 20,
    },
    {
      id: "fb-sit-hard",
      type: "situation_image",
      source_language: "en",
      target_language: "en",
      content:
        "Explain how emerging automation technologies impact modern workplace culture and employee collaboration.",
      image_url:
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400",
      difficulty: "hard",
      target_word_count: 16,
      margin_buffer: 7,
      max_word_count: 23,
    },
  ],
};

export function getFallbackPrompt(
  mode: LinguaTypeMode,
  difficulty: DifficultyOption = "medium",
): LinguaTypePrompt {
  const pool = FALLBACK_PROMPTS[mode] ?? FALLBACK_PROMPTS.translation;
  const match = pool.find((p) => p.difficulty === difficulty);
  if (match) return match;
  return pool[0] as LinguaTypePrompt;
}

export async function createSession(
  payload: SessionCreatePayload,
): Promise<SessionResponse> {
  try {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mode: payload.mode,
        timer_seconds: payload.timer_seconds,
        target_word_count: payload.target_word_count,
        margin_buffer: payload.margin_buffer,
        source_language: payload.source_language ?? "ru",
        target_language: payload.target_language ?? "en",
        difficulty: payload.difficulty ?? "medium",
        input_mode: payload.input_mode ?? "free",
        preferred_style: payload.preferred_style ?? "conversational",
        allow_loose_phrasing: payload.allow_loose_phrasing ?? true,
        check_case_and_period: payload.check_case_and_period ?? false,
      }),
    });

    if (res.ok) {
      return (await res.json()) as SessionResponse;
    }
  } catch {
    // Network or server unreachable: fallback gracefully
  }

  // Graceful local fallback session
  const fallbackPrompt = getFallbackPrompt(payload.mode, payload.difficulty);
  const now = new Date();
  const expires = new Date(now.getTime() + 3600000);

  return {
    session_id: `local-session-${Date.now()}`,

    status: "active",
    mode: payload.mode,
    prompt: fallbackPrompt,
    timer_seconds: payload.timer_seconds,
    input_mode: payload.input_mode ?? "free",
    preferred_style: payload.preferred_style ?? "conversational",
    allow_loose_phrasing: payload.allow_loose_phrasing ?? true,
    check_case_and_period: payload.check_case_and_period ?? false,
    created_at: now.toISOString(),
    expires_at: expires.toISOString(),
  };
}

export async function getSessionById(
  sessionId: string,
): Promise<SessionResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
    if (res.ok) {
      return (await res.json()) as SessionResponse;
    }
  } catch {
    // ignore
  }
  return null;
}

export type StreamEvaluationCallbacks = {
  onSessionStart?: (data: { session_id: string; status: string }) => void;
  onToken?: (text: string) => void;
  onGrammarErrors?: (errors: GrammarErrorSpan[]) => void;
  onSemanticCheck?: (val: SemanticValidation) => void;
  onStyleAlternative?: (alt: StyleAlternative) => void;
  onMetrics?: (metrics: SessionMetrics) => void;
  onDone?: (data: { latency?: LatencyBreakdown }) => void;
  onError?: (err: Error) => void;
};

/**
 * Connects to SSE evaluation endpoint and dispatches events to callbacks.
 * Falls back to sync evaluation if streaming fails.
 */
export async function streamEvaluation(
  sessionId: string,
  payload: EvaluationRequestPayload,
  callbacks: StreamEvaluationCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/evaluate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify(payload),
      signal,
    });

    if (!res.ok || !res.body) {
      throw new Error(`SSE request failed with status ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    const parserState = createSSEParserState();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const events = parseSSEChunks(chunk, parserState);

      for (const ev of events) {
        dispatchSSEEvent(ev, callbacks);
      }
    }

    // Flush any remaining buffered chunk
    const trailingEvents = parseSSEChunks("\n\n", parserState);
    for (const ev of trailingEvents) {
      dispatchSSEEvent(ev, callbacks);
    }
  } catch (err: unknown) {
    if (signal?.aborted) return;
    const error = err instanceof Error ? err : new Error(String(err));
    // Attempt sync fallback
    try {
      const syncResult = await evaluateSync(sessionId, payload);
      if (syncResult !== null) {
        callbacks.onGrammarErrors?.(syncResult.grammar_errors);
        callbacks.onSemanticCheck?.(syncResult.semantic_validation);
        callbacks.onStyleAlternative?.(syncResult.style_alternative);
        callbacks.onMetrics?.(syncResult.metrics);
        callbacks.onDone?.({ latency: syncResult.latency });
        return;
      }
    } catch {
      // Both failed
    }

    callbacks.onError?.(error);
  }
}

function dispatchSSEEvent(
  ev: ParsedSSEEvent,
  callbacks: StreamEvaluationCallbacks,
): void {
  switch (ev.event) {
    case "session_start":
      callbacks.onSessionStart?.(
        ev.data as { session_id: string; status: string },
      );
      break;
    case "token": {
      const tokenPayload = ev.data as
        | { text?: string; token?: string }
        | string;
      const text =
        typeof tokenPayload === "string"
          ? tokenPayload
          : (tokenPayload?.text ?? tokenPayload?.token ?? "");
      callbacks.onToken?.(text);
      break;
    }
    case "grammar_errors":
      callbacks.onGrammarErrors?.(normalizeGrammarErrors(ev.data));
      break;
    case "semantic_check":
      callbacks.onSemanticCheck?.(ev.data as SemanticValidation);
      break;
    case "style_alternative":
      callbacks.onStyleAlternative?.(ev.data as StyleAlternative);
      break;
    case "metrics":
      callbacks.onMetrics?.(ev.data as SessionMetrics);
      break;
    case "done":
      callbacks.onDone?.(ev.data as { latency?: LatencyBreakdown });
      break;
    case "error": {
      const errData = ev.data as { message?: string } | string;
      const msg =
        typeof errData === "string"
          ? errData
          : (errData?.message ?? "Stream evaluation error");
      callbacks.onError?.(new Error(msg));
      break;
    }
    default:
      break;
  }
}

export type EvaluationResultSync = {
  result_id: string;
  session_id: string;
  user_text: string;
  semantic_validation: SemanticValidation;
  grammar_errors: GrammarErrorSpan[];
  style_alternative: StyleAlternative;
  metrics: SessionMetrics;
  latency: LatencyBreakdown;
};

export async function evaluateSync(
  sessionId: string,
  payload: EvaluationRequestPayload,
): Promise<EvaluationResultSync | null> {
  try {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/evaluate/sync`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      return (await res.json()) as EvaluationResultSync;
    }
  } catch {
    // ignore
  }
  return null;
}

export type UserProfile = {
  id: string;
  email: string;
  display_name?: string | null;
  native_language: string;
  target_language: string;
  preferred_style: StyleOption;
  allow_loose_phrasing: boolean;
  input_mode: "free" | "scaffolding";
  created_at?: string;
  updated_at?: string;
};

export type UserProfileUpdate = {
  native_language?: string;
  target_language?: string;
  preferred_style?: StyleOption;
  allow_loose_phrasing?: boolean;
  input_mode?: "free" | "scaffolding";
};

export type GameResultSummary = {
  id: string;
  session_id: string;
  mode: LinguaTypeMode;
  source_language: string;
  target_language: string;
  prompt_content: string;
  user_text: string;
  time_spent_ms: number;
  wpm: number;
  accuracy_score: number;
  semantic_valid: boolean;
  error_count: number;
  recommended_variant: string;
  preferred_style: string;
  created_at: string;
};

export type HistoryListResponse = {
  results: GameResultSummary[];
  total: number;
  offset: number;
  limit: number;
};

/**
 * Fetches user profile preferences from GET /api/v1/user/profile.
 * Requires Firebase ID token in Authorization header.
 */
export async function getUserProfile(
  token: string,
): Promise<UserProfile | null> {
  try {
    const res = await fetch(`${API_BASE}/user/profile`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.ok) {
      return (await res.json()) as UserProfile;
    }
  } catch {
    // Network or server error
  }
  return null;
}

/**
 * Updates user profile preferences via PUT /api/v1/user/profile.
 * Requires Firebase ID token in Authorization header.
 */
export async function updateUserProfile(
  token: string,
  update: UserProfileUpdate,
): Promise<UserProfile | null> {
  try {
    const res = await fetch(`${API_BASE}/user/profile`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(update),
    });

    if (res.ok) {
      return (await res.json()) as UserProfile;
    }
  } catch {
    // Network or server error
  }
  return null;
}

/**
 * Retrieves paginated session results history for authenticated user via GET /api/v1/results.
 */
export async function getUserResultsHistory(
  token: string,
  options?: { limit?: number; offset?: number; mode?: string },
): Promise<HistoryListResponse | null> {
  try {
    const params = new URLSearchParams();
    if (options?.limit !== undefined) {
      params.set("limit", String(options.limit));
    }
    if (options?.offset !== undefined) {
      params.set("offset", String(options.offset));
    }
    if (typeof options?.mode === "string" && options.mode !== "") {
      params.set("mode", options.mode);
    }

    const query = params.toString() ? `?${params.toString()}` : "";
    const res = await fetch(`${API_BASE}/results${query}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.ok) {
      return (await res.json()) as HistoryListResponse;
    }
  } catch {
    // Network or server error
  }
  return null;
}

/**
 * Loads user profile preferences from GET /api/v1/user/profile when authenticated,
 * and synchronizes reactive LinguaType state.
 */
export async function loadUserProfilePreferences(): Promise<UserProfile | null> {
  const user = getUserState();
  if (user === null) return null;

  try {
    const token = await getIdToken();
    if (token === null || token === "") return null;

    const profile = await getUserProfile(token);
    if (profile !== null) {
      if (profile.preferred_style !== undefined) {
        setPreferredStyle(profile.preferred_style);
      }
      if (profile.allow_loose_phrasing !== undefined) {
        setAllowLoosePhrasing(profile.allow_loose_phrasing);
      }
      return profile;
    }
  } catch (err) {
    console.warn("Failed to load user profile preferences:", err);
  }
  return null;
}

/**
 * Persists user profile preference updates via PUT /api/v1/user/profile when authenticated.
 */
export async function persistUserProfilePreferences(
  update: UserProfileUpdate,
): Promise<UserProfile | null> {
  const user = getUserState();
  if (user === null) return null;

  try {
    const token = await getIdToken();
    if (token === null || token === "") return null;

    return await updateUserProfile(token, update);
  } catch (err) {
    console.warn("Failed to persist user profile preferences:", err);
  }
  return null;
}
