import { JSXElement, Show } from "solid-js";

import { getConfig } from "../../../config/store";
import { getFocus } from "../../../states/test";
import { cn } from "../../../utils/cn";
import { CommandlineHotkey } from "../../hotkeys/CommandlineHotkey";
import { QuickRestartHotkey } from "../../hotkeys/QuickRestartHotkey";

export function Keytips(): JSXElement {
  return (
    <Show when={getConfig.showKeyTips}>
      <div
        class={cn("mb-8 flex flex-col items-center gap-2 transition-opacity", {
          "opacity-0": getFocus(),
        })}
      >
        <div class="flex items-center gap-2 text-xs">
          <kbd class="rounded bg-sub/20 px-1 py-0.5 font-mono text-text">tab</kbd>
          <span>+</span>
          <kbd class="rounded bg-sub/20 px-1 py-0.5 font-mono text-text">enter</kbd>
          <span>- submit / new prompt</span>
        </div>

        <div class="flex items-center gap-2 text-xs">
          <kbd class="rounded bg-sub/20 px-1 py-0.5 font-mono text-text">esc</kbd>
          <span>- reset session</span>
        </div>
      </div>
    </Show>
  );
}
