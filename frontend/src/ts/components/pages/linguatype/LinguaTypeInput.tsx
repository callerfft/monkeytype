import { createEffect, JSXElement, onMount } from "solid-js";

import {
  getSessionStatus,
  getStartTime,
  getUserText,
  getWordLimitExceeded,
  setStartTime,
  setUserText,
} from "../../../states/linguatype";
import { cn } from "../../../utils/cn";

export type LinguaTypeInputProps = {
  onSubmit: () => void;
  onReset: () => void;
  onFirstKeypress?: () => void;
};

export function LinguaTypeInput(props: LinguaTypeInputProps): JSXElement {
  let textareaRef: HTMLTextAreaElement | undefined;

  onMount(() => {
    // Focus textarea on mount per CODING_STANDARDS.md
    if (textareaRef) {
      textareaRef.focus();
    }
  });

  // Ensure native DOM textarea value strictly mirrors reactive userText state
  createEffect(() => {
    const current = getUserText();
    if (textareaRef && textareaRef.value !== current) {
      textareaRef.value = current;
    }
  });

  const isInputDisabled = (): boolean => {
    const s = getSessionStatus();
    return s === "submitting" || s === "streaming" || s === "completed";
  };

  const handleInput = (
    e: InputEvent & { currentTarget: HTMLTextAreaElement },
  ): void => {
    const val = e.currentTarget.value;
    setUserText(val);

    if (getStartTime() === null && val.trim().length > 0) {
      setStartTime(Date.now());
      props.onFirstKeypress?.();
    }
  };

  const handleKeyDown = (e: KeyboardEvent): void => {
    // Escape resets test
    if (e.key === "Escape") {
      e.preventDefault();
      props.onReset();
      return;
    }

    // Tab+Enter or Ctrl+Enter submits
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      props.onSubmit();
      return;
    }
  };

  return (
    <div class="relative mx-auto w-full max-w-4xl">
      <textarea
        ref={(el) => {
          textareaRef = el;
        }}
        value={getUserText()}
        onInput={handleInput}
        onKeyDown={handleKeyDown}
        disabled={isInputDisabled()}
        placeholder="Type your translation or sentence here..."
        rows={4}
        class={cn(
          "w-full rounded-(--roundness) border bg-bg/90 p-4 font-mono text-base leading-relaxed md:text-lg",
          "transition-all duration-150 ease-out placeholder:text-sub/50",
          "focus:ring-2 focus:ring-main/30 focus:outline-none",
          getWordLimitExceeded()
            ? "border-error focus:border-error"
            : "border-sub/30 focus:border-main",
          isInputDisabled() && "cursor-not-allowed bg-sub-alt/30 opacity-80",
        )}
        aria-label="Your translation or sentence input"
        aria-invalid={getWordLimitExceeded()}
        aria-describedby="linguatype-input-hint"
        autocomplete="off"
      ></textarea>

      <div
        id="linguatype-input-hint"
        class="mt-2 flex items-center justify-between text-xs text-sub"
      >
        <span>
          <kbd class="rounded bg-sub/20 px-1 py-0.5 font-mono text-text">
            Esc
          </kbd>{" "}
          reset
          <span class="mx-2">•</span>
          <kbd class="rounded bg-sub/20 px-1 py-0.5 font-mono text-text">
            Tab+Enter
          </kbd>{" "}
          submit
        </span>

        <span
          class={cn(
            "transition-colors",
            getWordLimitExceeded() ? "font-medium text-error" : "text-sub/70",
          )}
        >
          {getWordLimitExceeded()
            ? "Word limit exceeded!"
            : "Keep within the word budget"}
        </span>
      </div>
    </div>
  );
}
