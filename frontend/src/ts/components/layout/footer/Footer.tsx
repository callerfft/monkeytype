import { JSXElement } from "solid-js";

import { getIsScreenshotting } from "../../../states/core";
import { showModal } from "../../../states/modals";
import { getFocus } from "../../../states/test";
import { cn } from "../../../utils/cn";
import { Button } from "../../common/Button";
import { Keytips } from "./Keytips";
import { ThemeIndicator } from "./ThemeIndicator";
import { VersionButton } from "./VersionButton";

export function Footer(): JSXElement {
  return (
    <footer
      class={cn("relative text-xs text-sub", {
        "opacity-0": getIsScreenshotting(),
      })}
    >
      <Keytips />

      <div
        class={cn("-m-2 flex justify-between gap-8 transition-opacity", {
          "opacity-0": getFocus(),
        })}
      >
        <div class="flex items-center gap-2 text-sub/70 text-xs py-1">
          <span class="font-semibold text-text">LinguaType</span>
          <span>•</span>
          <span>sub-3s AI translation & sentence construction trainer</span>
        </div>
        <div class="flex flex-col items-end text-right lg:flex-row">
          <ThemeIndicator />
          <VersionButton />
        </div>
      </div>
    </footer>
  );
}
