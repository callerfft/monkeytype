import { createMemo, For, JSXElement, Show } from "solid-js";

import {
  getCheckCaseAndPeriod,
  getEffectiveMaxWords,
  getEffectiveTargetWords,
  getMode,
  getPrompt,
  getSessionStatus,
  getSpeedHistory,
  getStreamingFeedback,
  getUserText,
  getWordsTyped,
  GrammarErrorSpan,
  isCaseOrPeriodError,
} from "../../../states/linguatype";
import { cn } from "../../../utils/cn";
import { LinguaTypeSpeedChart } from "./LinguaTypeSpeedChart";

type TextSegment = {
  text: string;
  isError: boolean;
  error?: GrammarErrorSpan;
  index?: number;
};

export function StreamingFeedbackCard(): JSXElement {
  const status = () => getSessionStatus();
  const feedback = () => getStreamingFeedback();
  const userText = () => getUserText();
  const prompt = () => feedback().evaluatedPrompt ?? getPrompt();
  const mode = () => getMode();

  const isVisible = createMemo((): boolean => {
    return (
      status() === "submitting" ||
      status() === "streaming" ||
      status() === "completed" ||
      feedback().isStreamComplete ||
      feedback().tokenStream.length > 0 ||
      feedback().grammarErrors.length > 0 ||
      feedback().semanticCheck !== null
    );
  });

  const effectiveGrammarErrors = createMemo((): GrammarErrorSpan[] => {
    const raw = feedback().grammarErrors;
    if (getCheckCaseAndPeriod()) {
      return raw;
    }
    const text = userText();
    return raw.filter((err) => !isCaseOrPeriodError(err, text));
  });

  const scoreValue = createMemo((): number => {
    return Math.round(
      feedback().semanticCheck?.score ??
        feedback().metrics?.accuracy_score ??
        0,
    );
  });

  const scoreTheme = createMemo(() => {
    const s = scoreValue();
    if (s >= 80) {
      return {
        cardBorder: "border-[#22c55e]/35",
        cardBg: "bg-[#22c55e]/5",
        text: "text-[#22c55e]",
        badge: "bg-[#22c55e]/20 text-[#22c55e]",
      };
    }
    if (s >= 50) {
      return {
        cardBorder: "border-[#eab308]/35",
        cardBg: "bg-[#eab308]/5",
        text: "text-[#eab308]",
        badge: "bg-[#eab308]/20 text-[#eab308]",
      };
    }
    return {
      cardBorder: "border-error/35",
      cardBg: "bg-error/5",
      text: "text-error",
      badge: "bg-error/20 text-error",
    };
  });

  // Segments user text with highlighted error spans
  const highlightedSegments = createMemo((): TextSegment[] => {
    const text = userText();
    const errors = [...effectiveGrammarErrors()].sort(
      (a, b) => a.start - b.start,
    );

    if (errors.length === 0 || !text) {
      return [{ text, isError: false }];
    }

    const segments: TextSegment[] = [];
    let cursor = 0;

    errors.forEach((err, idx) => {
      const start = Math.max(0, Math.min(err.start, text.length));
      const end = Math.max(start, Math.min(err.end, text.length));

      if (start > cursor) {
        segments.push({
          text: text.slice(cursor, start),
          isError: false,
        });
      }

      if (end > start) {
        segments.push({
          text: text.slice(start, end),
          isError: true,
          error: err,
          index: idx,
        });
      }

      cursor = Math.max(cursor, end);
    });

    if (cursor < text.length) {
      segments.push({
        text: text.slice(cursor),
        isError: false,
      });
    }

    return segments;
  });

  return (
    <Show when={isVisible()}>
      <section
        class={cn(
          "relative w-full rounded-(--roundness) border border-sub/20 bg-sub-alt/15 p-3.5 md:p-5",
          "backdrop-blur-xs transition-all duration-200 select-none",
        )}
        role="region"
        aria-label="Evaluation Feedback"
        aria-live="polite"
      >
        {/* Top Status Bar with Latency & Status */}
        <div class="mb-3 flex flex-wrap items-center justify-between border-b border-sub/20 pb-2 text-xs text-sub">
          <div class="flex items-center gap-2">
            <span class="font-medium tracking-wider text-text uppercase">
              Evaluation Result
            </span>
            <Show when={status() === "streaming" || status() === "submitting"}>
              <span class="flex items-center gap-1.5 font-mono text-main">
                <span class="inline-block h-2 w-2 animate-ping rounded-full bg-main"></span>
                evaluating in real-time...
              </span>
            </Show>
            <Show
              when={feedback().isStreamComplete || status() === "completed"}
            >
              <span class="font-mono text-sub">
                • completed
                {feedback().error !== null ? " (offline fallback)" : ""}
              </span>
            </Show>
          </div>

          <Show when={feedback().latency}>
            {(lat) => (
              <div class="flex items-center gap-3 font-mono text-[11px] text-sub">
                <span>TTFT: {Math.round(lat().ttft_ms)}ms</span>
                <span>
                  inference: {Math.round(lat().inference_duration_ms)}ms
                </span>
                <span>total: {Math.round(lat().pipeline_duration_ms)}ms</span>
              </div>
            )}
          </Show>
        </div>

        {/* =========================================================================
            ROW 1: TWO COLUMNS (Top-Left Yellow: Prompt | Top-Right Red: Score)
           ========================================================================= */}
        <div class="mb-3 grid grid-cols-1 gap-3 md:grid-cols-2">
          {/* Top-Left: Original Prompt & Word Target (Yellow box in sketch) */}
          <div class="flex flex-col justify-between rounded-(--roundness) border border-score-yellow/30 bg-score-yellow/5 p-3 md:p-3.5">
            <div>
              <div class="mb-1.5 flex items-center justify-between text-xs">
                <span class="font-semibold tracking-wider text-score-yellow uppercase">
                  Original Prompt
                </span>
                <span class="rounded bg-sub/20 px-1.5 py-0.5 font-mono text-[10px] text-sub uppercase">
                  {mode() === "translation" ? "Mode A" : "Mode B"} •{" "}
                  {prompt()?.source_language.toUpperCase() ?? "RU"} ➔{" "}
                  {prompt()?.target_language.toUpperCase() ?? "EN"}
                </span>
              </div>

              <p class="text-sm leading-relaxed font-medium text-text md:text-base">
                {prompt()?.content ?? "No prompt content available"}
              </p>
            </div>

            <div class="mt-2.5 flex items-center justify-between border-t border-sub/15 pt-2 font-mono text-xs text-sub">
              <span>
                Target:{" "}
                <span class="font-bold text-text">
                  {getEffectiveTargetWords()}
                </span>{" "}
                words (max {getEffectiveMaxWords()})
              </span>
              <span>
                Typed:{" "}
                <span class="font-bold text-main">{getWordsTyped()}</span> words
              </span>
            </div>
          </div>

          {/* Top-Right: Score & Semantic Assessment (Dynamic Green/Yellow/Red) */}
          <div
            class={cn(
              "flex flex-col justify-between rounded-(--roundness) border p-3 transition-colors duration-200 md:p-3.5",
              scoreTheme().cardBorder,
              scoreTheme().cardBg,
            )}
          >
            <div>
              <div class="mb-1.5 flex items-center justify-between text-xs">
                <span
                  class={cn(
                    "font-semibold tracking-wider uppercase",
                    scoreTheme().text,
                  )}
                >
                  Overall Score & Evaluation
                </span>
                <Show when={feedback().semanticCheck}>
                  {(sem) => (
                    <span
                      class={cn(
                        "rounded px-2 py-0.5 font-mono text-[10px] font-bold uppercase",
                        sem().is_valid
                          ? scoreTheme().badge
                          : "bg-score-red/20 text-score-red",
                      )}
                    >
                      {sem().is_valid
                        ? "Meaning Preserved"
                        : "Meaning Incomplete"}
                    </span>
                  )}
                </Show>
              </div>

              <div class="flex items-baseline gap-2">
                <span
                  class={cn(
                    "font-mono text-3xl font-extrabold md:text-4xl",
                    scoreTheme().text,
                  )}
                >
                  {scoreValue()}%
                </span>
                <span class="text-xs text-sub uppercase">accuracy match</span>
              </div>

              <p class="mt-1 text-xs leading-relaxed text-text">
                {feedback().semanticCheck?.explanation ??
                  "Semantic evaluation in progress..."}
              </p>

              <Show
                when={
                  (feedback().semanticCheck?.missing_concepts?.length ?? 0) > 0
                }
              >
                <div class="mt-1.5 font-mono text-xs text-score-red">
                  Missing concepts:{" "}
                  {feedback().semanticCheck?.missing_concepts.join(", ")}
                </div>
              </Show>
            </div>
          </div>
        </div>

        {/* =========================================================================
            ROW 2: CENTER GREEN (User's Typed Text & Inline/Red Grammar Errors)
           ========================================================================= */}
        <div class="mb-3 rounded-(--roundness) border border-main/30 bg-main/5 p-3 md:p-3.5">
          <div class="mb-1.5 flex items-center justify-between text-xs">
            <span class="font-semibold tracking-wider text-main uppercase">
              Your Submission
            </span>
            <span class="font-mono text-xs text-sub">
              {userText().length} chars • {getWordsTyped()} words
            </span>
          </div>

          {/* User's typed sentence with inline error highlights */}
          <div
            class="rounded-(--roundness) border border-sub/20 bg-bg/90 p-3 font-mono text-sm leading-relaxed md:text-base"
            tabIndex={0}
          >
            <For each={highlightedSegments()}>
              {(seg) => (
                <Show when={seg.isError} fallback={<span>{seg.text}</span>}>
                  <span
                    class={cn(
                      "rounded-xs border-b-2 px-1 font-semibold transition-colors",
                      seg.error?.severity === "warning"
                        ? "border-yellow-500 bg-yellow-500/15 text-yellow-400"
                        : "border-error bg-error/20 text-error",
                    )}
                    aria-invalid="true"
                    aria-describedby={`error-desc-${seg.index}`}
                    title={seg.error?.message}
                  >
                    {seg.text}
                  </span>
                </Show>
              )}
            </For>
          </div>

          {/* Grammar & Spelling Issues (red listing underneath) */}
          <div class="mt-2.5">
            <div class="mb-1.5 text-xs font-semibold tracking-wider text-error uppercase">
              Grammar & Spelling Issues ({effectiveGrammarErrors().length})
            </div>

            <Show
              when={effectiveGrammarErrors().length > 0}
              fallback={
                <div class="rounded bg-bg/50 px-3 py-2 font-mono text-xs text-sub">
                  No grammar or spelling issues detected. Clear, accurate
                  phrasing!
                </div>
              }
            >
              <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
                <For each={effectiveGrammarErrors()}>
                  {(err, idx) => (
                    <div
                      id={`error-desc-${idx()}`}
                      class="flex flex-col gap-1 rounded-(--roundness) border border-error/25 bg-bg/70 p-2.5 text-xs"
                    >
                      <div class="flex items-center justify-between">
                        <span class="rounded bg-error/15 px-1.5 py-0.5 font-mono text-[9px] font-medium text-error uppercase">
                          {err.category}
                        </span>
                        <span class="font-mono text-[9px] text-sub">
                          offset: {err.start}..{err.end}
                        </span>
                      </div>
                      <div class="leading-snug text-text">{err.message}</div>
                      <div class="flex items-center gap-2 font-mono text-xs">
                        <span class="text-error line-through">
                          {err.original_text}
                        </span>
                        <span class="text-sub">➔</span>
                        <span class="font-semibold text-main">
                          {err.suggestion}
                        </span>
                      </div>
                    </div>
                  )}
                </For>
              </div>
            </Show>
          </div>
        </div>

        {/* =========================================================================
            ROW 3: BOTTOM YELLOW (Recommended Stylistic Alternative & WPM Speed Chart)
           ========================================================================= */}
        <div class="rounded-(--roundness) border border-score-yellow/30 bg-score-yellow/5 p-3 md:p-3.5">
          <div class="grid grid-cols-1 items-stretch gap-3 lg:grid-cols-12">
            {/* Left Col (Col 1-5): Recommended Stylistic Alternative */}
            <Show when={feedback().styleAlternative}>
              {(alt) => (
                <div class="flex flex-col justify-between rounded-(--roundness) border border-main/30 bg-bg/70 p-3 lg:col-span-5">
                  <div>
                    <div class="mb-1 flex items-center justify-between">
                      <span class="text-xs font-semibold tracking-wider text-main uppercase">
                        Recommended Alternative ({alt().style})
                      </span>
                    </div>
                    <p class="font-mono text-sm leading-relaxed font-medium text-text md:text-base">
                      &ldquo;{alt().text}&rdquo;
                    </p>
                  </div>
                  <p class="mt-2 text-xs leading-relaxed text-sub">
                    {alt().explanation}
                  </p>
                </div>
              )}
            </Show>

            {/* Right Col (Col 6-12): Speed Chart & Metrics */}
            <div
              class={cn(
                "flex flex-col justify-between gap-2",
                feedback().styleAlternative
                  ? "lg:col-span-7"
                  : "lg:col-span-12",
              )}
            >
              {/* Typing Speed Chart */}
              <LinguaTypeSpeedChart
                data={getSpeedHistory()}
                durationMs={feedback().metrics?.time_spent_ms ?? 1000}
                finalWpm={feedback().metrics?.wpm ?? 0}
                grammarErrors={effectiveGrammarErrors()}
              />

              {/* Session Metrics 4-Box Summary */}
              <Show when={feedback().metrics}>
                {(met) => (
                  <div class="grid grid-cols-2 gap-2 text-center sm:grid-cols-4">
                    <div class="rounded border border-sub/10 bg-bg/60 p-2">
                      <div class="text-[9px] tracking-wider text-sub uppercase">
                        Typing Speed
                      </div>
                      <div class="font-mono text-base font-bold text-main">
                        {met().wpm}{" "}
                        <span class="text-[10px] font-normal text-sub">
                          WPM
                        </span>
                      </div>
                    </div>
                    <div class="rounded border border-sub/10 bg-bg/60 p-2">
                      <div class="text-[9px] tracking-wider text-sub uppercase">
                        Accuracy Score
                      </div>
                      <div
                        class={cn(
                          "font-mono text-base font-bold",
                          scoreTheme().text,
                        )}
                      >
                        {scoreValue()}%
                      </div>
                    </div>
                    <div class="rounded border border-sub/10 bg-bg/60 p-2">
                      <div class="text-[9px] tracking-wider text-sub uppercase">
                        Time Spent
                      </div>
                      <div class="font-mono text-base font-bold text-text">
                        {(met().time_spent_ms / 1000).toFixed(1)}s
                      </div>
                    </div>
                    <div class="rounded border border-sub/10 bg-bg/60 p-2">
                      <div class="text-[9px] tracking-wider text-sub uppercase">
                        Target Met
                      </div>
                      <div
                        class={cn(
                          "font-mono text-base font-bold",
                          met().target_met ? "text-main" : "text-error",
                        )}
                      >
                        {met().target_met ? "Yes" : "No"}
                      </div>
                    </div>
                  </div>
                )}
              </Show>
            </div>
          </div>

          {/* Keyboard Navigation Helper */}
          <div class="mt-2.5 flex items-center justify-center gap-4 border-t border-sub/15 pt-2 font-mono text-xs text-sub/80">
            <span>
              <kbd class="rounded bg-sub/20 px-1.5 py-0.5 text-text">
                Tab + Enter
              </kbd>{" "}
              next prompt
            </span>
            <span>•</span>
            <span>
              <kbd class="rounded bg-sub/20 px-1.5 py-0.5 text-text">Esc</kbd>{" "}
              reset
            </span>
          </div>
        </div>

        {/* Streaming Token Debug chunk (only while actively streaming) */}
        <Show when={status() === "streaming" && feedback().tokenStream}>
          <div class="mt-2 border-t border-sub/10 pt-1 font-mono text-[11px] text-sub">
            <span class="text-sub/50">streaming token chunk: </span>
            {feedback().tokenStream}
          </div>
        </Show>
      </section>
    </Show>
  );
}
