import { JSXElement, Show } from "solid-js";

import {
  getEffectiveMaxWords,
  getEffectiveTargetWords,
  getMode,
  getPrompt,
} from "../../../states/linguatype";
import { cn } from "../../../utils/cn";

export function PromptCard(): JSXElement {
  const prompt = () => getPrompt();
  const mode = () => getMode();

  return (
    <section
      class={cn(
        "relative mx-auto mb-6 w-full max-w-4xl rounded-(--roundness) bg-sub-alt/40 p-6 md:p-8",
        "border border-sub/20 backdrop-blur-xs transition-all duration-200",
      )}
      role="region"
      aria-label="LinguaType Prompt"
    >
      {/* Top Metadata Header */}
      <div class="mb-4 flex flex-wrap items-center justify-between gap-2 text-xs text-sub">
        <div class="flex items-center gap-2">
          <span class="rounded bg-sub/30 px-2 py-0.5 font-medium tracking-wide text-text uppercase">
            {mode() === "translation"
              ? "Mode A • Translation"
              : "Mode B • Situation"}
          </span>
          <span class="text-sub">
            {prompt()?.source_language.toUpperCase() ?? "RU"} ➔{" "}
            {prompt()?.target_language.toUpperCase() ?? "EN"}
          </span>
        </div>

        <div class="flex items-center gap-3">
          <span class="text-sub">
            target:{" "}
            <span class="font-medium text-text">
              {getEffectiveTargetWords()}
            </span>{" "}
            words (max {getEffectiveMaxWords()})
          </span>
          <Show when={prompt()?.difficulty}>
            <span class="rounded bg-sub/20 px-1.5 py-0.5 text-[10px] tracking-wider text-sub uppercase">
              {prompt()?.difficulty}
            </span>
          </Show>
        </div>
      </div>

      {/* Optional Context Image for Mode B */}
      <Show when={mode() === "situation_image" && prompt()?.image_url}>
        {(imgUrl) => (
          <div class="mb-4 overflow-hidden rounded-(--roundness) border border-sub/30 bg-bg">
            <img
              src={imgUrl()}
              alt="Prompt illustration context"
              class="max-h-64 w-full object-contain"
              loading="lazy"
            />
          </div>
        )}
      </Show>

      {/* Main Prompt Text */}
      <div
        class="text-lg leading-relaxed font-normal text-text md:text-2xl"
        tabIndex={0}
        aria-label="Prompt text"
      >
        <Show
          when={prompt()}
          fallback={<span class="text-sub italic">Loading prompt...</span>}
        >
          {prompt()?.content}
        </Show>
      </div>

      <div class="mt-3 text-right text-[11px] text-sub/70">
        Type your response in English below. Press{" "}
        <kbd class="rounded bg-sub/30 px-1 py-0.5 text-text">Tab+Enter</kbd> to
        submit.
      </div>
    </section>
  );
}
