import { For, JSXElement, onMount } from "solid-js";

import { setConfig } from "../../../config/setters";
import { getConfig } from "../../../config/store";
import { applyPreset } from "../../../controllers/theme-controller";
import {
  loadUserProfilePreferences,
  persistUserProfilePreferences,
} from "../../../queries/linguatype-api";
import {
  DifficultyOption,
  getCheckCaseAndPeriod,
  getDifficulty,
  getMode,
  getPreferredStyle,
  getTimerSeconds,
  getTargetWordCount,
  LinguaTypeMode,
  setCheckCaseAndPeriod,
  setDifficulty,
  setMode,
  setPreferredStyle,
  setTimerSeconds,
  setTargetWordCount,
  StyleOption,
  TimerOption,
} from "../../../states/linguatype";
import { cn } from "../../../utils/cn";
import { Button } from "../../common/Button";

export { loadUserProfilePreferences, persistUserProfilePreferences };

export type LinguaTypeConfigProps = {
  onChangeConfig?: () => void;
  disabled?: boolean;
};

export function LinguaTypeConfig(props: LinguaTypeConfigProps): JSXElement {
  onMount(() => {
    void loadUserProfilePreferences();
  });

  const modes = [
    {
      id: "translation" as const,
      label: "translation",
      faIcon: "fa-language" as const,
    },
    {
      id: "situation_image" as const,
      label: "situation",
      faIcon: "fa-lightbulb" as const,
    },
  ];

  const timers: { value: TimerOption; label: string }[] = [
    { value: 15, label: "15s" },
    { value: 30, label: "30s" },
    { value: 60, label: "60s" },
    { value: null, label: "∞" },
  ];

  const wordBudgets: number[] = [8, 12, 16, 20];

  const styles: StyleOption[] = [
    "conversational",
    "formal",
    "concise",
    "academic",
    "business",
  ];

  const difficulties: DifficultyOption[] = ["easy", "medium", "hard"];

  const handleModeChange = (mode: LinguaTypeMode): void => {
    if (props.disabled) return;
    setMode(mode);
    props.onChangeConfig?.();
  };

  const handleTimerChange = (timer: TimerOption): void => {
    if (props.disabled) return;
    setTimerSeconds(timer);
    props.onChangeConfig?.();
  };

  const handleWordBudgetChange = (words: number): void => {
    if (props.disabled) return;
    setTargetWordCount(words);
    props.onChangeConfig?.();
  };

  const handleDifficultyChange = (diff: DifficultyOption): void => {
    if (props.disabled) return;
    setDifficulty(diff);
    props.onChangeConfig?.();
  };

  const handleStyleChange = (style: StyleOption): void => {
    if (props.disabled) return;
    setPreferredStyle(style);
    void persistUserProfilePreferences({ preferred_style: style });
  };

  return (
    <div
      class="mb-6 flex flex-wrap items-center justify-center gap-2 font-mono text-xs select-none"
      role="toolbar"
      aria-label="LinguaType Game Configuration"
    >
      {/* Mode Selection */}
      <div class="flex items-center gap-1 rounded-(--roundness) bg-sub-alt px-2 py-1">
        <For each={modes}>
          {(m) => {
            const isActive = (): boolean => getMode() === m.id;
            return (
              <Button
                variant="text"
                fa={{ icon: m.faIcon, fixedWidth: true }}
                text={m.label}
                class={cn(
                  "px-2 py-1 text-xs transition-colors",
                  isActive()
                    ? "font-semibold text-main"
                    : "text-sub hover:text-text",
                )}
                onClick={() => handleModeChange(m.id)}
                disabled={props.disabled}
                balloon={{ text: `Mode: ${m.label}`, position: "up" }}
              />
            );
          }}
        </For>
      </div>

      {/* Timer Selection */}
      <div class="flex items-center gap-1 rounded-(--roundness) bg-sub-alt px-2 py-1">
        <span class="mr-1 text-sub">time:</span>
        <For each={timers}>
          {(t) => {
            const isActive = (): boolean => getTimerSeconds() === t.value;
            return (
              <Button
                variant="text"
                text={t.label}
                class={cn(
                  "px-2 py-1 text-xs transition-colors",
                  isActive()
                    ? "font-semibold text-main"
                    : "text-sub hover:text-text",
                )}
                onClick={() => handleTimerChange(t.value)}
                disabled={props.disabled}
                balloon={{
                  text: t.value ? `${t.value} seconds` : "Untimed",
                  position: "up",
                }}
              />
            );
          }}
        </For>
      </div>

      {/* Target Word Budget */}
      <div class="flex items-center gap-1 rounded-(--roundness) bg-sub-alt px-2 py-1">
        <span class="mr-1 text-sub">words:</span>
        <For each={wordBudgets}>
          {(w) => {
            const isActive = (): boolean => getTargetWordCount() === w;
            return (
              <Button
                variant="text"
                text={`${w}`}
                class={cn(
                  "px-2 py-1 text-xs transition-colors",
                  isActive()
                    ? "font-semibold text-main"
                    : "text-sub hover:text-text",
                )}
                onClick={() => handleWordBudgetChange(w)}
                disabled={props.disabled}
                balloon={{ text: `Target ${w} words`, position: "up" }}
              />
            );
          }}
        </For>
      </div>

      {/* Difficulty */}
      <div class="flex items-center gap-1 rounded-(--roundness) bg-sub-alt px-2 py-1">
        <For each={difficulties}>
          {(d) => {
            const isActive = (): boolean => getDifficulty() === d;
            return (
              <Button
                variant="text"
                text={d}
                class={cn(
                  "px-2 py-1 text-xs transition-colors",
                  isActive()
                    ? "font-semibold text-main"
                    : "text-sub hover:text-text",
                )}
                onClick={() => handleDifficultyChange(d)}
                disabled={props.disabled}
                balloon={{ text: `Difficulty: ${d}`, position: "up" }}
              />
            );
          }}
        </For>
      </div>

      {/* Style Preference */}
      <div class="flex items-center gap-1 rounded-(--roundness) bg-sub-alt px-2 py-1">
        <span class="mr-1 text-sub">style:</span>
        <select
          value={getPreferredStyle()}
          onChange={(e) =>
            handleStyleChange(e.currentTarget.value as StyleOption)
          }
          disabled={props.disabled}
          class={cn(
            "rounded bg-transparent px-1 py-0.5 text-xs text-sub transition-colors focus:text-text focus:outline-none",
            "cursor-pointer hover:text-text",
          )}
          aria-label="Preferred stylistic tone"
        >
          <For each={styles}>
            {(s) => (
              <option value={s} class="bg-bg text-text">
                {s}
              </option>
            )}
          </For>
        </select>
      </div>

      {/* Capitalization & Terminal Period Toggle */}
      <div class="flex items-center gap-1 rounded-(--roundness) bg-sub-alt px-2 py-1">
        <Button
          variant="text"
          fa={{ icon: "fa-font", fixedWidth: true }}
          text={getCheckCaseAndPeriod() ? "case & . : on" : "case & . : off"}
          class={cn(
            "px-2 py-1 text-xs transition-colors",
            getCheckCaseAndPeriod()
              ? "font-semibold text-main"
              : "text-sub hover:text-text",
          )}
          onClick={() => {
            if (props.disabled) return;
            const next = !getCheckCaseAndPeriod();
            setCheckCaseAndPeriod(next);
            try {
              localStorage.setItem(
                "linguatype_check_case_and_period",
                String(next),
              );
            } catch {
              // ignore
            }
          }}
          disabled={props.disabled}
          balloon={{
            text: getCheckCaseAndPeriod()
              ? "Strict: capital letter & ending period checked"
              : "Relaxed: capital letter & ending period ignored",
            position: "up",
          }}
        />
      </div>

      {/* Quick Pinned Theme: Classic (#000000 / #e2b714) */}
      <div class="flex items-center gap-1 rounded-(--roundness) bg-sub-alt px-2 py-1">
        <Button
          variant="text"
          fa={{ icon: "fa-palette", fixedWidth: true }}
          text="classic"
          class={cn(
            "px-2 py-1 text-xs transition-colors",
            getConfig.theme === "classic" && !getConfig.customTheme
              ? "font-semibold text-main"
              : "text-sub hover:text-text",
          )}
          onClick={() => {
            applyPreset("classic");
            setConfig("theme", "classic");
            setConfig("customTheme", false);
          }}
          disabled={props.disabled}
          balloon={{
            text: "Classic theme (#000000 / #e2b714)",
            position: "up",
          }}
        />
      </div>
    </div>
  );
}
