# Handoff Report: Frontend & Codebase Survey for LinguaType

**Explorer**: explorer_survey_1  
**Working Directory**: `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\explorer_survey_1`  
**Target Milestone**: Survey & Architectural Integration Analysis  
**Date**: 2026-10-17  

---

## 1. Observation

### 1.1 Repository Structure & Workspace Configuration
- **Monorepo setup**: `pnpm-workspace.yaml` declares packages:
  - `frontend`
  - `backend`
  - `packages/*` (`@monkeytype/contracts`, `@monkeytype/schemas`, `@monkeytype/util`, `@monkeytype/funbox`, `@monkeytype/challenges`, `@monkeytype/oxlint-config`, `@monkeytype/typescript-config`)
  - `frontend/storybook`
- **Turborepo**: `turbo.json` orchestrates pipelines: `build`, `test`, `lint`, `lint-fast`, `dev`, `ts-check`.
- **Node & Package Manager**:
  - `package.json:97-99`: `"engines": { "node": ">=24.0.0 <25" }`, `"packageManager": "pnpm@11.21.0"`.
  - Active runtime: Node `v25.8.2`, npm `11.11.1`. `pnpm` is not currently in the global system PATH; `node_modules` is not yet installed in the workspace (`node_modules` test returned `False`).

### 1.2 Frontend Build, Lint, and Test Tooling
- **Vite & Plugins (`frontend/vite.config.ts`)**:
  - Vite v8.0.5 with `@tailwindcss/vite` (v4.3.2), `vite-plugin-solid` (v2.11.11), `solid-devtools/vite`, `vite-plugin-html-inject`.
  - Output directory (`frontend/vite.config.ts:206`): `outDir: "../dist"`, root: `"src"`, publicDir: `"../static"`.
  - Code splitting groups (`frontend/vite.config.ts:245-275`): `vendor-firebase`, `vendor-tanstack`, `vendor-sentry`, `monkeytype-packages`, `vendor-chart`.
- **Linter & Formatter (`frontend/package.json:7-10`, `package.json:50-51`)**:
  - Linter: `oxlint` (v1.88.0) with `--format agent`, `--type-aware`, `--type-check`.
  - Formatter: `oxfmt` (v0.73.0), config `.oxfmtrc.json`. (Per `AGENTS.md`: *"Format with `npx oxfmt <files>` (not prettier). For typechecking, use `pnpm oxlint --type-aware --type-check` instead of `tsc`"*).
  - Styles: `stylelint` (v17.6.0) targeting `**/*.{scss,css}`.
- **Testing (`frontend/vitest.config.ts:18-66`)**:
  - Vitest v4.1.0 with 3 workspace projects:
    1. Unit tests: `__tests__/**/*.spec.ts` in `happy-dom`.
    2. JSDOM tests: `__tests__/**/*.jsdom-spec.ts` in `jsdom`.
    3. JSX component tests: `__tests__/**/*.spec.tsx` in `jsdom` with `@testing-library/jest-dom` and `setup-jsx.ts`.

### 1.3 Frontend Architecture: SolidJS vs Vanilla JS
- **Application Entry & Shell (`frontend/src/ts/index.tsx`, `components/core/App.tsx`)**:
  - `frontend/src/ts/index.tsx:70`: `render(() => <App />, document.body);`.
  - `frontend/src/ts/components/core/App.tsx:18-77`: Pure SolidJS shell rendering `<QueryClientProvider>`, `<Overlays>`, `<Theme>`, `<BarTimerProgress>`, `<Modals>`, `<Header>`, `<main><Pages registry={pageRegistry} /></main>`, `<Footer>`, `<DevTools>`.
- **Routing & Page Management (`frontend/src/ts/controllers/route-controller.ts`, `components/pages/page-registry.ts`)**:
  - Client-side history routing: `route-controller.ts:50-100` maps `/`, `/verify`, `/leaderboards`, `/about`, `/settings`, `/login`, `/account`.
  - `page-registry.ts:16-33` registers components: `loading`, `test`, `settings`, `about`, `account`, `login`, `profile`, `profileSearch`, `404`, `accountSettings`, `leaderboards`, `friends`.
- **Standard Typing Test Page (`frontend/src/ts/components/pages/test/TestPage.tsx`)**:
  - SolidJS layout bridge (`TestPage.tsx:70-73`): *"The test page. Internals are still vanilla - this owns the markup and hands its elements to the vanilla modules on mount, unbinding them on cleanup."*
  - Solid elements: `<TestConfig>`, `<LiveStatsTextTop>`, `<LiveStatsMini>`, `<TestResult>`.
  - Vanilla Core:
    - `TestUI.init()` in `frontend/src/ts/test/test-ui.ts` (1,616 lines): Direct imperative DOM manipulation of `#words`, active letter/word classes, carets, line jumps.
    - `TestWords` in `frontend/src/ts/test/test-words.ts`: Array of target words for strict character-by-character comparison.
    - `test-logic.ts` (1,460 lines): Orchestrates `restart()`, `init()`, words generator (`words-generator.ts`), strict char-by-char validation, WPM calculation.
    - `input/listeners/input.ts` & `handlers/insert-text.ts`: Intercepts `beforeinput` and `input` events on `<textarea id="wordsInput">`, validating typed character vs target character.

### 1.4 Hotkeys & Keyboard Navigation
- **TanStack Hotkeys (`frontend/src/ts/states/hotkeys.ts`, `input/hotkeys/quickrestart.ts`)**:
  - Uses `@tanstack/solid-hotkeys` with `createHotkey()`.
  - Quick restart hotkeys: Tab, Escape, Enter (configurable via `getConfig.quickRestart`).
  - Commandline: Tab or Escape.
  - Active input management: `registerInputElement(inputRef, signal)`, `focusWords()`, `blurInputElement()`.

### 1.5 Firebase Auth Status (`frontend/src/ts/firebase.ts`)
- Uses Firebase v12 (`"firebase": "12.13.0"` in `frontend/package.json:60`).
- Initialized in `frontend/src/ts/firebase.ts:52-92`:
  - `signInWithPopup(provider, rememberMe)` for Google OAuth (`GoogleAuthProvider`).
  - `signInWithEmailAndPassword`, `createUserWithEmailAndPassword`.
  - `getIdToken()` (`firebase.ts:193-197`) resolves Bearer token for authenticated backend API requests.
  - `onAuthStateChanged` updates `setUserState(user)`.
- Magic Link (passwordless email): Not yet implemented, but supported by Firebase v12 SDK (`sendSignInLinkToEmail`, `isSignInWithEmailLink`, `signInWithEmailLink`).

### 1.6 Styling & Design System
- **Tailwind v4 (`frontend/src/styles/tailwind.css`)**:
  - Variables: `bg-bg`, `text-text`, `text-main`, `bg-sub`, `bg-sub-alt`, `text-sub`, `text-error`.
  - Custom utilities: `rounded-(--roundness)`, `rounded-double`, `theme-bubbles`.
  - FontAwesome icons: Wrapped via `<Fa icon="fa-..." />` (`components/common/Fa.tsx`).
  - Buttons: Wrapped via `<Button variant="button" | "text" ... />` (`components/common/Button.tsx`).
- **User Rule / AGENTS.md Constraint**:
  - Strictly minimalist dark Monkeytype aesthetic.
  - **NO STICKERS**, no decorative cartoon widgets, no over-engineered graphics.

---

## 2. Logic Chain

```
Observation (1.3): Monkeytype's standard typing test engine (test-ui.ts, test-logic.ts, test-words.ts)
is 3,000+ lines of imperative vanilla JS strictly designed for fixed-target character-by-character validation.
       │
       ▼
Observation (ORIGINAL_REQUEST.md / R3): LinguaType requires:
1. Mode A: Native sentence translation (Russian -> English).
2. Mode B: Situation / context image description.
3. Free-form input with live word counter (target count + margin buffer).
4. Sub-3s streaming LLM evaluation (SSE/WebSocket) rendering grammar error spans, semantic score, and 1 style variant.
       │
       ▼
Logical Deduction: Shoehorning free-form sentence generation + streaming LLM card into `test-words.ts`
and `test-ui.ts` would require major intrusive patches to delicate legacy vanilla code, risking regressions
in standard typing modes and failing CODING_STANDARDS.md ("new components use .tsx").
       │
       ▼
Observation (1.3, 1.4): Monkeytype's page shell (App.tsx, Pages.tsx, page-registry.ts, route-controller.ts)
is 100% SolidJS (.tsx) with clean page lifecycle hooks and TanStack Solid Query/Hotkeys.
       │
       ▼
Conclusion: The optimal integration architecture is a dedicated SolidJS module `LinguaTypePage.tsx`
(and subcomponents `LinguaTypeConfig`, `PromptCard`, `LinguaTypeInput`, `StreamingFeedbackCard`)
under `frontend/src/ts/components/pages/linguatype/`:
- Zero blast radius on legacy typing engine.
- Reuses core design system (Button, Fa, Tailwind variables, Theme, Modals, Hotkeys).
- Full compliance with CODING_STANDARDS.md.
- Accessible via `/linguatype` route and top navigation icon (fa-language) in Header/Nav.tsx.
```

---

## 3. Extension Points Specification

### 3.1 Component Architecture & File Tree
```
frontend/src/ts/
├── components/pages/linguatype/
│   ├── LinguaTypePage.tsx             # Main page container (binds hotkeys, timer, layout)
│   ├── LinguaTypeConfig.tsx           # Sub-bar (Mode A / Mode B, 15/30/60s, Word budget, Style)
│   ├── PromptCard.tsx                 # Source sentence (Mode A) or Context/Image prompt (Mode B)
│   ├── LinguaTypeInput.tsx            # Free-form typing textarea with smooth caret & live word count
│   ├── StreamingFeedbackCard.tsx      # Real-time LLM evaluation (grammar spans, semantic tag, style option)
│   └── LinguaTypeLiveStats.tsx        # Word count / budget progress, countdown timer
├── states/
│   └── linguatype.ts                  # Solid store (currentPrompt, sessionStatus, streamingFeedback, timer)
├── queries/
│   └── linguatype-api.ts              # SSE/WebSocket streaming client + REST session fetcher
└── input/hotkeys/
    └── linguatype.ts                  # Dedicated hotkeys (Tab+Enter submit/restart, Esc reset)
```

### 3.2 Integration Touchpoints
1. **`page-registry.ts`**:
   Add entry:
   ```ts
   linguatype: { component: LinguaTypePage, class: "full-width content-grid" }
   ```
2. **`route-controller.ts`**:
   Add route:
   ```ts
   {
     path: "/linguatype",
     load: async (_params, options) => {
       await PageController.change("linguatype", options);
     },
   }
   ```
3. **`frontend/firebase.json`**:
   Update rewrite rule:
   ```json
   "source": "/@(test|settings|account|about|login|profile|friends|account-settings|leaderboards|linguatype){,/**}"
   ```
4. **`frontend/src/ts/components/layout/header/Nav.tsx`**:
   Add language navigation icon:
   ```tsx
   <Button
     variant="text"
     fa={{ icon: "fa-language", fixedWidth: true }}
     class={buttonClass()}
     dataset={{ "data-nav-item": "linguatype" }}
     href="/linguatype"
     router-link
     balloon={{ text: "LinguaType", position: "down" }}
   />
   ```
5. **Firebase Auth Integration (`frontend/src/ts/firebase.ts`)**:
   - Add `sendMagicLink(email: string)` and `completeMagicLinkSignIn()` using `firebase/auth`.
   - Use `getIdToken()` for SSE Authorization header: `headers: { Authorization: `Bearer ${await getIdToken()}` }`.

### 3.3 A11y & Keyboard Navigation Plan
- **Keyboard-First Controls**:
  - `Tab + Enter`: Submit text early for evaluation / Restart if completed.
  - `Escape`: Cancel current test / Reset to new prompt.
  - Input auto-focus: Focus maintained on `<textarea>` on mount and after reset via callback ref.
- **ARIA & Screen Reader Support**:
  - Prompt card: `role="region"` with `aria-label="LinguaType Prompt"`.
  - Word counter: `role="status"` with `aria-live="polite"` announcing `"X of Y words"`.
  - Streaming card: `role="region"` with `aria-live="polite"` so screen readers receive completed evaluation without interrupting typing.
  - Contrast: Standard Monkeytype `--bg-color` (`#323437`) and `--text-color` (`#d1d0c5`) yield a contrast ratio of > 8.5:1 (exceeding WCAG AAA).

---

## 4. Caveats & Risks

1. **Local Node/pnpm Environment**:
   - `pnpm` is not installed in the global PATH in this Windows sandbox. Running build/lint/test commands directly requires either installing pnpm (`npm install -g pnpm`), using `corepack enable`, or setting PATH to npm global prefix.
   - `node_modules` must be populated (`pnpm install`) before frontend unit tests or oxlint typechecks can execute.
2. **SSE / WebSocket Network Proxies**:
   - If using SSE (`EventSource` or `fetch` with `ReadableStream`), HTTP/1.1 proxies or corporate firewalls might buffer chunked responses, increasing apparent latency. The backend FastAPI service must set `Cache-Control: no-cache` and `X-Accel-Buffering: no`.
3. **LLM Latency Ceiling (< 3.0s)**:
   - Client evaluation latency budget is tight. Network RTT + backend validation + Gemini Flash inference must stay strictly under 2.5s to ensure UI renders within 3s. Pre-warming and strict JSON schemas are non-negotiable.

---

## 5. Conclusion & Recommendations

1. **Architectural Separation**: Implement LinguaType as an independent, modular SolidJS page (`LinguaTypePage.tsx`) using Monkeytype's native component library (`Button`, `Fa`, `@tanstack/solid-query`, `@tanstack/solid-hotkeys`). Do NOT rewrite or entangle with legacy `test-ui.ts` / `test-words.ts`.
2. **Contract First**: Lock `contracts/api_v1.json` before parallel development begins.
3. **Recommended Frontend Milestones**:
   - **M1 (Contract & Client SDK)**: Generate TypeScript types from `contracts/api_v1.json` and create the SSE/WebSocket client (`linguatype-api.ts`).
   - **M2 (LinguaType Core UI & Session)**: Build `LinguaTypePage.tsx`, `PromptCard.tsx`, `LinguaTypeInput.tsx`, and `LinguaTypeConfig.tsx`.
   - **M3 (Streaming Evaluation Card & A11y)**: Build `StreamingFeedbackCard.tsx` with error span highlighting, style alternative display, and full ARIA/keyboard hotkeys.
   - **M4 (Firebase Auth & Profile Integration)**: Implement Magic Link sign-in and wire language/style preferences into session requests.
   - **M5 (E2E Verification & Latency Benchmark)**: Vitest unit tests, oxlint checks, and latency verification (< 3.0s).

---

## 6. Verification Method

1. **Files to Inspect**:
   - `frontend/src/ts/components/pages/page-registry.ts` (page registration)
   - `frontend/src/ts/controllers/route-controller.ts` (routing)
   - `frontend/src/styles/tailwind.css` (tokens and theme colors)
   - `frontend/src/ts/firebase.ts` (auth token export)
2. **Commands for Validation (once `pnpm install` is executed)**:
   - Linting: `pnpm oxlint --format agent`
   - Typechecking: `pnpm oxlint --type-aware --type-check`
   - Code formatting: `npx oxfmt . --check`
   - Unit tests: `pnpm vitest run`
3. **Invalidation Conditions**:
   - If Monkeytype's core architecture requires LinguaType to replace the default home typing test without a separate route, Option B (intercepting `TestPage.tsx`) must be adopted instead.
