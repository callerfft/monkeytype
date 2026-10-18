import { createMemo, createSignal } from "solid-js";

export type LinguaTypeMode = "translation" | "situation_image";
export type TimerOption = 15 | 30 | 60 | null;
export type StyleOption =
  | "conversational"
  | "formal"
  | "concise"
  | "academic"
  | "business";
export type DifficultyOption = "easy" | "medium" | "hard";
export type SessionStatus =
  | "idle"
  | "ready"
  | "active"
  | "submitting"
  | "streaming"
  | "completed"
  | "cancelled"
  | "error";

export type LinguaTypePrompt = {
  id: string;
  type: LinguaTypeMode;
  source_language: string;
  target_language: string;
  content: string;
  image_url?: string | null;
  difficulty: DifficultyOption;
  target_word_count: number;
  margin_buffer: number;
  max_word_count: number;
};

export type GrammarErrorSpan = {
  start: number;
  end: number;
  original_text: string;
  message: string;
  suggestion: string;
  category:
    | "grammar"
    | "spelling"
    | "punctuation"
    | "syntax"
    | "word_choice"
    | "agreement"
    | "tense"
    | string;
  severity: "error" | "warning" | "info";
};

export type SemanticValidation = {
  is_valid: boolean;
  score: number;
  explanation: string;
  missing_concepts: string[];
};

export type StyleAlternative = {
  style: StyleOption | string;
  text: string;
  explanation: string;
};

export type LatencyBreakdown = {
  ttft_ms: number;
  inference_duration_ms: number;
  pipeline_duration_ms: number;
};

export type SessionMetrics = {
  wpm: number;
  accuracy_score: number;
  time_spent_ms: number;
  word_count: number;
  target_word_count?: number;
  target_met: boolean;
  word_limit_exceeded?: boolean;
  timer_expired?: boolean;
};

export type StreamingFeedback = {
  tokenStream: string;
  grammarErrors: GrammarErrorSpan[];
  semanticCheck: SemanticValidation | null;
  styleAlternative: StyleAlternative | null;
  metrics: SessionMetrics | null;
  latency: LatencyBreakdown | null;
  error: string | null;
  isStreamComplete: boolean;
  evaluatedPrompt: LinguaTypePrompt | null;
};

const initialFeedback: StreamingFeedback = {
  tokenStream: "",
  grammarErrors: [],
  semanticCheck: null,
  styleAlternative: null,
  metrics: null,
  latency: null,
  error: null,
  isStreamComplete: false,
  evaluatedPrompt: null,
};

// Configuration signals
export const [getMode, setMode] = createSignal<LinguaTypeMode>("translation");
export const [getTimerSeconds, setTimerSeconds] = createSignal<TimerOption>(30);
export const [getPreferredStyle, setPreferredStyle] =
  createSignal<StyleOption>("conversational");
export const [getAllowLoosePhrasing, setAllowLoosePhrasing] =
  createSignal<boolean>(true);
export const [getTargetWordCount, setTargetWordCount] =
  createSignal<number>(10);
export const [getMarginBuffer, setMarginBuffer] = createSignal<number>(5);
export const [getDifficulty, setDifficulty] =
  createSignal<DifficultyOption>("medium");
export const [getCheckCaseAndPeriod, setCheckCaseAndPeriod] =
  createSignal<boolean>(false);

// Session signals
export const [getSessionId, setSessionId] = createSignal<string | null>(null);
export const [getSessionStatus, setSessionStatus] =
  createSignal<SessionStatus>("idle");
export const [getPrompt, setPrompt] = createSignal<LinguaTypePrompt | null>(
  null,
);
export const [getUserText, setUserText] = createSignal<string>("");
export const [getTimeLeft, setTimeLeft] = createSignal<number>(30);
export const [getStartTime, setStartTime] = createSignal<number | null>(null);
export const [getEndTime, setEndTime] = createSignal<number | null>(null);
export const [getStreamingFeedback, setStreamingFeedback] =
  createSignal<StreamingFeedback>({ ...initialFeedback });

export type SpeedPoint = {
  second: number;
  wpm: number;
  rawWpm: number;
  charCount: number;
};

export const [getSpeedHistory, setSpeedHistory] = createSignal<SpeedPoint[]>(
  [],
);

export function recordSpeedSnapshot(second: number, charCount: number): void {
  const minutes = Math.max(second / 60, 0.01);
  const wpm = Math.round((charCount / 5 / minutes) * 10) / 10;
  setSpeedHistory((prev) => [...prev, { second, wpm, rawWpm: wpm, charCount }]);
}

// Computed memos
export const getEffectiveTargetWords = createMemo((): number => {
  return getPrompt()?.target_word_count ?? getTargetWordCount();
});

export const getEffectiveMaxWords = createMemo((): number => {
  const p = getPrompt();
  if (p) return p.max_word_count;
  return getTargetWordCount() + getMarginBuffer();
});

export const countWords = (text: string): number => {
  const trimmed = text.trim();
  if (!trimmed) return 0;
  return trimmed.split(/\s+/).length;
};

export const getWordsTyped = createMemo((): number => {
  return countWords(getUserText());
});

export const getWordLimitExceeded = createMemo((): boolean => {
  return getWordsTyped() > getEffectiveMaxWords();
});

export const getTargetMet = createMemo((): boolean => {
  const count = getWordsTyped();
  return count >= getEffectiveTargetWords() && count <= getEffectiveMaxWords();
});

export function resetFeedback(): void {
  setStreamingFeedback({ ...initialFeedback, grammarErrors: [] });
}

export function resetSession(): void {
  setUserText("");
  resetFeedback();
  setSpeedHistory([]);
  setStartTime(null);
  setEndTime(null);
  const timer = getTimerSeconds();
  setTimeLeft(timer ?? 0);
  setSessionStatus("ready");
}

export function calculateLocalMetrics(
  text: string,
  timeSpentMs: number,
  targetWords: number,
  maxWords: number,
  grammarErrorsCount = 0,
): SessionMetrics {
  const charCount = text.length;
  const words = countWords(text);
  const minutes = Math.max(timeSpentMs / 60000, 0.01);
  const rawWpm = charCount / 5 / minutes;
  const wpm = Math.max(0, Math.round(rawWpm * 10) / 10);

  // Compute accuracy estimate: base 100 minus errors penalty
  const errorPenalty = grammarErrorsCount * 10;
  const lengthPenalty =
    words < targetWords ? ((targetWords - words) / targetWords) * 30 : 0;
  const accuracy_score = Math.max(
    0,
    Math.min(100, Math.round(100 - errorPenalty - lengthPenalty)),
  );

  return {
    wpm,
    accuracy_score,
    time_spent_ms: timeSpentMs,
    word_count: words,
    target_word_count: targetWords,
    target_met: words >= targetWords && words <= maxWords,
    word_limit_exceeded: words > maxWords,
    timer_expired: false,
  };
}

export function isCaseOrPeriodError(
  err: GrammarErrorSpan,
  text: string,
): boolean {
  const msg = err.message.toLowerCase();
  const cat = err.category.toLowerCase();
  const orig = err.original_text.trim();

  const trimmedLen = text.trimEnd().length;

  // Capitalization error at sentence start
  if (
    msg.includes("capital") ||
    msg.includes("uppercase") ||
    (err.start === 0 &&
      (cat === "punctuation" || cat === "grammar" || cat === "spelling") &&
      orig.length <= 1)
  ) {
    return true;
  }

  // Terminal punctuation error (missing period/dot) at sentence end
  if (
    msg.includes("terminal") ||
    msg.includes("period") ||
    msg.includes("full stop") ||
    (msg.includes("punctuation") &&
      (err.end >= trimmedLen || err.start >= Math.max(0, trimmedLen - 1)))
  ) {
    return true;
  }

  return false;
}
