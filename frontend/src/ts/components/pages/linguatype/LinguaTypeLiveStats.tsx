import { createMemo, JSXElement, Show } from "solid-js";
import { cn } from "../../../utils/cn";
import {
  getEffectiveMaxWords,
  getEffectiveTargetWords,
  getTargetMet,
  getTimeLeft,
  getTimerSeconds,
  getWordLimitExceeded,
  getWordsTyped,
} from "../../../states/linguatype";

export function LinguaTypeLiveStats(): JSXElement {
  const timer = () => getTimerSeconds();
  const timeLeft = () => getTimeLeft();
  const wordsTyped = () => getWordsTyped();
  const targetWords = () => getEffectiveTargetWords();
  const maxWords = () => getEffectiveMaxWords();
  const targetMet = () => getTargetMet();
  const exceeded = () => getWordLimitExceeded();

  const formattedTime = createMemo((): string => {
    if (timer() === null) return "∞";
    const sec = Math.max(0, timeLeft());
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  });

  const isLowTime = createMemo((): boolean => {
    return timer() !== null && timeLeft() <= 5 && timeLeft() > 0;
  });

  const wordProgressPct = createMemo((): number => {
    if (maxWords() <= 0) return 0;
    return Math.min(100, Math.round((wordsTyped() / maxWords()) * 100));
  });

  return (
    <div
      class="mx-auto mb-4 flex w-full max-w-4xl items-center justify-between text-sm"
      role="region"
      aria-label="LinguaType Live Stats"
    >
      {/* Timer Display */}
      <div class="flex items-center gap-2">
        <Show when={timer() !== null}>
          <span
            class={cn(
              "font-mono text-2xl font-semibold transition-colors md:text-3xl",
              isLowTime()
                ? "text-error animate-pulse"
                : "text-main",
            )}
            aria-label={`Time remaining: ${formattedTime()}`}
          >
            {formattedTime()}
          </span>
        </Show>
        <Show when={timer() === null}>
          <span class="font-mono text-xl text-sub" aria-label="Untimed mode">
            untimed
          </span>
        </Show>
      </div>

      {/* Word Counter & Progress Bar */}
      <div class="flex flex-col items-end gap-1">
        <div
          class="flex items-center gap-2 font-mono text-xs md:text-sm"
          role="status"
          aria-live="polite"
          aria-label={`${wordsTyped()} of ${targetWords()} words, limit ${maxWords()}`}
        >
          <span
            class={cn(
              "font-semibold transition-colors",
              exceeded()
                ? "text-error"
                : targetMet()
                ? "text-main"
                : "text-text",
            )}
          >
            {wordsTyped()}
          </span>
          <span class="text-sub">/</span>
          <span class="text-sub">{targetWords()} target</span>
          <span class="text-sub/60">(max {maxWords()})</span>
        </div>

        {/* Minimal Progress Bar */}
        <div class="h-1.5 w-32 overflow-hidden rounded-full bg-sub-alt md:w-44">
          <div
            class={cn(
              "h-full transition-all duration-150 ease-out",
              exceeded()
                ? "bg-error"
                : targetMet()
                ? "bg-main"
                : "bg-sub",
            )}
            style={{ width: `${wordProgressPct()}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
