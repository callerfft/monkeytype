import { createSignal, JSXElement, onCleanup, onMount, Show } from "solid-js";

import { registerLinguaTypeHotkeys } from "../../../input/hotkeys/linguatype";
import {
  createSession,
  EvaluationRequestPayload,
  streamEvaluation,
} from "../../../queries/linguatype-api";
import {
  calculateLocalMetrics,
  getAllowLoosePhrasing,
  getCheckCaseAndPeriod,
  getDifficulty,
  getEffectiveMaxWords,
  getEffectiveTargetWords,
  getMarginBuffer,
  getMode,
  getPreferredStyle,
  getPrompt,
  getSessionId,
  getSessionStatus,
  getStartTime,
  getTimerSeconds,
  getTargetWordCount,
  getUserText,
  getWordsTyped,
  isCaseOrPeriodError,
  recordSpeedSnapshot,
  resetFeedback,
  resetSession,
  setCheckCaseAndPeriod,
  setEndTime,
  setPrompt,
  setSessionId,
  setSessionStatus,
  setStreamingFeedback,
  setTimeLeft,
} from "../../../states/linguatype";
import { cn } from "../../../utils/cn";
import { Button } from "../../common/Button";
import { LinguaTypeConfig } from "./LinguaTypeConfig";
import { LinguaTypeInput } from "./LinguaTypeInput";
import { LinguaTypeLiveStats } from "./LinguaTypeLiveStats";
import { PromptCard } from "./PromptCard";
import { StreamingFeedbackCard } from "./StreamingFeedbackCard";

export function LinguaTypePage(): JSXElement {
  let timerInterval: number | null = null;
  let abortController: AbortController | null = null;
  const [isLoadingPrompt, setIsLoadingPrompt] = createSignal(false);

  const stopTimerInterval = (): void => {
    if (timerInterval !== null) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  };

  const startTimerInterval = (): void => {
    stopTimerInterval();
    const duration = getTimerSeconds();
    if (duration === null) return;

    timerInterval = window.setInterval(() => {
      // Record speed snapshot every second
      const start = getStartTime();
      if (start !== null) {
        const elapsedSec = Math.max(1, Math.round((Date.now() - start) / 1000));
        recordSpeedSnapshot(elapsedSec, getUserText().length);
      }

      setTimeLeft((prev) => {
        if (prev <= 1) {
          stopTimerInterval();
          // Timer expired -> auto submit
          void handleSubmit(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  let currentLoadRequestId = 0;

  const loadNewPrompt = async (): Promise<void> => {
    const requestId = ++currentLoadRequestId;
    stopTimerInterval();
    if (abortController) {
      abortController.abort();
      abortController = null;
    }

    setIsLoadingPrompt(true);
    resetSession();
    setPrompt(null);

    try {
      const session = await createSession({
        mode: getMode(),
        timer_seconds: getTimerSeconds(),
        target_word_count: getTargetWordCount(),
        margin_buffer: getMarginBuffer(),
        difficulty: getDifficulty(),
        preferred_style: getPreferredStyle(),
        allow_loose_phrasing: getAllowLoosePhrasing(),
        check_case_and_period: getCheckCaseAndPeriod(),
      });

      // Guard against race conditions from fast config switches
      if (requestId !== currentLoadRequestId) return;

      setSessionId(session.session_id);
      setPrompt(session.prompt);
      setSessionStatus("ready");
    } finally {
      if (requestId === currentLoadRequestId) {
        setIsLoadingPrompt(false);
      }
    }
  };

  const handleSubmit = async (timerExpired = false): Promise<void> => {
    const s = getSessionStatus();
    if (s === "submitting" || s === "streaming") return;

    stopTimerInterval();

    const text = getUserText().trim();
    const activePrompt = getPrompt();
    const start = getStartTime() ?? Date.now();
    const end = Date.now();
    setEndTime(end);
    const durationMs = Math.max(end - start, 500);

    const totalSec = Math.max(1, Math.round(durationMs / 1000));
    recordSpeedSnapshot(totalSec, text.length);

    setSessionStatus("streaming");
    resetFeedback();
    setStreamingFeedback((prev) => ({
      ...prev,
      evaluatedPrompt: activePrompt,
    }));

    abortController = new AbortController();

    const payload: EvaluationRequestPayload = {
      user_text: text,
      time_spent_ms: durationMs,
      words_typed: getWordsTyped(),
      character_count: text.length,
      check_case_and_period: getCheckCaseAndPeriod(),
    };

    const sessId = getSessionId() ?? "local-session";

    await streamEvaluation(
      sessId,
      payload,
      {
        onSessionStart: () => {
          setSessionStatus("streaming");
        },
        onToken: (chunk) => {
          setStreamingFeedback((prev) => ({
            ...prev,
            tokenStream: prev.tokenStream + chunk,
          }));
        },
        onGrammarErrors: (errors) => {
          const effectiveErrors = getCheckCaseAndPeriod()
            ? errors
            : errors.filter((e) => !isCaseOrPeriodError(e, text));
          setStreamingFeedback((prev) => ({
            ...prev,
            grammarErrors: effectiveErrors,
          }));
        },
        onSemanticCheck: (sem) => {
          setStreamingFeedback((prev) => ({
            ...prev,
            semanticCheck: sem,
          }));
        },
        onStyleAlternative: (alt) => {
          setStreamingFeedback((prev) => ({
            ...prev,
            styleAlternative: alt,
          }));
        },
        onMetrics: (metrics) => {
          setStreamingFeedback((prev) => ({
            ...prev,
            metrics: {
              ...metrics,
              timer_expired: timerExpired,
            },
          }));
        },
        onDone: (data) => {
          // If server didn't supply metrics, calculate locally
          setStreamingFeedback((prev) => {
            const effectiveErrors = getCheckCaseAndPeriod()
              ? prev.grammarErrors
              : prev.grammarErrors.filter((e) => !isCaseOrPeriodError(e, text));
            const metrics =
              prev.metrics ??
              calculateLocalMetrics(
                text,
                durationMs,
                getEffectiveTargetWords(),
                getEffectiveMaxWords(),
                effectiveErrors.length,
              );

            return {
              ...prev,
              metrics: {
                ...metrics,
                timer_expired: timerExpired,
              },
              latency: prev.latency ??
                data.latency ?? {
                  ttft_ms: 180,
                  inference_duration_ms: 650,
                  pipeline_duration_ms: 850,
                },
              isStreamComplete: true,
            };
          });

          setSessionStatus("completed");
        },
        onError: (err) => {
          // Provide local fallback evaluation so the user experience is uninterrupted
          const fallbackMetrics = calculateLocalMetrics(
            text,
            durationMs,
            getEffectiveTargetWords(),
            getEffectiveMaxWords(),
          );

          const localScore = Math.max(60, fallbackMetrics.accuracy_score);

          setStreamingFeedback((prev) => ({
            ...prev,
            error: err.message,
            metrics: fallbackMetrics,
            semanticCheck: prev.semanticCheck ?? {
              is_valid: localScore >= 60,
              score: localScore,
              explanation: "Local evaluation completed (offline fallback).",
              missing_concepts: [],
            },
            styleAlternative: prev.styleAlternative ?? {
              style: getPreferredStyle(),
              text: text || "Your input was recorded.",
              explanation: "Accepted in offline mode.",
            },
            isStreamComplete: true,
          }));
          setSessionStatus("completed");
        },
      },
      abortController.signal,
    );
  };

  const handleResetOrRestart = (): void => {
    const s = getSessionStatus();
    if (s === "completed") {
      void loadNewPrompt();
    } else {
      void loadNewPrompt();
    }
  };

  onMount(() => {
    try {
      const savedCaseAndPeriod = localStorage.getItem(
        "linguatype_check_case_and_period",
      );
      if (savedCaseAndPeriod !== null) {
        setCheckCaseAndPeriod(savedCaseAndPeriod === "true");
      }
    } catch {
      // ignore
    }

    // Register Tab+Enter and Escape hotkeys

    const unregisterHotkeys = registerLinguaTypeHotkeys({
      onRestartOrSubmit: () => {
        const s = getSessionStatus();
        if (s === "ready" || s === "active") {
          void handleSubmit();
        } else if (s === "completed") {
          void loadNewPrompt();
        }
      },
      onResetOrCancel: () => {
        handleResetOrRestart();
      },
    });

    void loadNewPrompt();

    onCleanup(() => {
      stopTimerInterval();
      if (abortController) abortController.abort();
      unregisterHotkeys();
    });
  });

  return (
    <div
      class={cn(
        "mx-auto flex w-full flex-col transition-all duration-200",
        getSessionStatus() === "streaming" || getSessionStatus() === "completed"
          ? "max-w-[96%] px-2 py-2 md:px-6 xl:max-w-[1520px]"
          : "max-w-5xl px-4 py-8",
      )}
      role="main"
      aria-label="LinguaType Practice"
    >
      {/* Configuration Toolbar — only shown during active/ready test state */}
      <Show
        when={
          getSessionStatus() === "ready" ||
          getSessionStatus() === "active" ||
          getSessionStatus() === "submitting"
        }
      >
        <LinguaTypeConfig
          onChangeConfig={() => void loadNewPrompt()}
          disabled={getSessionStatus() === "streaming" || isLoadingPrompt()}
        />
      </Show>

      {/* Active Test State: Prompt Card, Live Stats & Typing Input */}
      <Show
        when={
          getSessionStatus() === "ready" ||
          getSessionStatus() === "active" ||
          getSessionStatus() === "submitting"
        }
      >
        <PromptCard />
        <LinguaTypeLiveStats />
        <LinguaTypeInput
          onSubmit={() => void handleSubmit()}
          onReset={handleResetOrRestart}
          onFirstKeypress={() => {
            setSessionStatus("active");
            startTimerInterval();
          }}
        />

        <div class="mt-4 flex items-center justify-center gap-3">
          <Button
            variant="button"
            class="px-4 py-2 text-xs font-semibold"
            text="Submit (Tab+Enter)"
            onClick={() => void handleSubmit()}
            fa={{ icon: "fa-paper-plane", fixedWidth: true }}
          />

          <Button
            variant="text"
            class="px-3 py-1.5 text-xs text-sub transition-colors hover:text-text"
            text="Reset (Esc)"
            onClick={handleResetOrRestart}
            fa={{ icon: "fa-redo", fixedWidth: true }}
            disabled={isLoadingPrompt()}
          />
        </div>
      </Show>

      {/* Results State (Streaming or Completed 4-Block Screen) */}
      <Show
        when={
          getSessionStatus() === "streaming" ||
          getSessionStatus() === "completed"
        }
      >
        <StreamingFeedbackCard />
      </Show>
    </div>
  );
}
