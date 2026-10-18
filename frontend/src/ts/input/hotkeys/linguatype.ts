import { onCleanup } from "solid-js";
import { getActivePage } from "../../states/core";

export type LinguaTypeHotkeyHandlers = {
  onRestartOrSubmit: () => void;
  onResetOrCancel: () => void;
  isEnabled?: () => boolean;
};

/**
 * Handles Tab+Enter and Escape hotkeys specifically for LinguaType page.
 * Tracks Tab key modifier state to allow Tab+Enter combo inside textarea without losing focus.
 */
export function registerLinguaTypeHotkeys(
  handlers: LinguaTypeHotkeyHandlers,
): () => void {
  let isTabDown = false;

  const handleKeyDown = (e: KeyboardEvent): void => {
    if (handlers.isEnabled && !handlers.isEnabled()) return;
    if (getActivePage() !== "linguatype") return;

    if (e.key === "Tab") {
      isTabDown = true;
      e.preventDefault();
    }

    // Tab+Enter combo OR Ctrl+Enter / Meta+Enter for submitting
    if (e.key === "Enter" && (isTabDown || e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      e.stopPropagation();
      handlers.onRestartOrSubmit();
      return;
    }

    // Escape resets or cancels current test
    if (e.key === "Escape") {
      e.preventDefault();
      e.stopPropagation();
      handlers.onResetOrCancel();
      return;
    }
  };

  const handleKeyUp = (e: KeyboardEvent): void => {
    if (e.key === "Tab") {
      isTabDown = false;
    }
  };

  if (typeof window !== "undefined") {
    window.addEventListener("keydown", handleKeyDown, { capture: true });
    window.addEventListener("keyup", handleKeyUp, { capture: true });
  }

  const cleanup = (): void => {
    if (typeof window !== "undefined") {
      window.removeEventListener("keydown", handleKeyDown, { capture: true });
      window.removeEventListener("keyup", handleKeyUp, { capture: true });
    }
  };

  onCleanup(cleanup);
  return cleanup;
}
