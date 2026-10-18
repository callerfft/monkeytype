# BRIEFING — 2026-10-17T05:41:00Z

## Mission
Survey Monkeytype frontend architecture and determine exact integration points for LinguaType modes, streaming evaluation, and keyboard navigation.

## 🔒 My Identity
- Archetype: explorer
- Roles: investigation, synthesis
- Working directory: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\explorer_survey_1
- Original parent: 3b1515b3-2073-47ba-bf07-f8f58de22f4d
- Milestone: survey

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Strictly no stickers, minimalist Monkeytype aesthetic
- Be concise (AGENTS.md)
- SolidJS for new components (.tsx), legacy remains vanilla
- Oxlint and Vitest tooling compliance

## Current Parent
- Conversation ID: 3b1515b3-2073-47ba-bf07-f8f58de22f4d
- Updated: not yet

## Investigation State
- **Explored paths**:
  - `package.json`, `pnpm-workspace.yaml`, `frontend/package.json`
  - `frontend/vite.config.ts`, `frontend/vitest.config.ts`, `vitest.config.ts`
  - `frontend/src/index.html`, `frontend/src/ts/index.tsx`
  - `frontend/src/ts/components/core/App.tsx`, `Header.tsx`, `Nav.tsx`, `page-registry.ts`, `Pages.tsx`
  - `frontend/src/ts/components/pages/test/TestPage.tsx`, `TestConfig.tsx`
  - `frontend/src/ts/test/test-logic.ts`, `test-ui.ts`, `test-words.ts`
  - `frontend/src/ts/input/listeners/input.ts`, `hotkeys/quickrestart.ts`, `states/hotkeys.ts`
  - `frontend/src/ts/firebase.ts`, `frontend/firebase.json`
  - `packages/schemas/src/configs.ts`, `shared.ts`
  - `docs/AGENT_BROWSER.md`, `CODING_STANDARDS.md`, `AGENTS.md`
- **Key findings**:
  - Monkeytype frontend is hybrid: App shell, routing, modals, headers, and pages are SolidJS (`.tsx`), while the standard typing engine (`test-ui.ts`, `test-words.ts`, `test-logic.ts`) is 3000+ lines of imperative vanilla DOM manipulation.
  - LinguaType requirements (free-form target translation/description, word counter with budget margin, timer, SSE/WebSocket streaming LLM evaluation with error spans and style alternatives) are fundamentally different from character-by-character word matching tests.
  - Cleanest integration point with minimal blast radius: Dedicated SolidJS page `LinguaTypePage.tsx` (`frontend/src/ts/components/pages/linguatype/`) registered in `page-registry.ts` and `route-controller.ts` (`/linguatype`), linked from `Nav.tsx` or `Header.tsx`.
  - Firebase Auth already present with v12 SDK (`signInWithPopup`, `getIdToken()`); Magic Link can be added using `sendSignInLinkToEmail` / `signInWithEmailLink`.
  - Keyboard navigation can leverage `@tanstack/solid-hotkeys` with `Tab+Enter` (submit/restart), `Esc` (reset), and autofocus.
  - Node is v25.8.2; global `pnpm` and `node_modules` are not installed yet in sandbox.
- **Unexplored areas**:
  - Python FastAPI backend architecture (handled by backend explorer).

## Key Decisions Made
- Recommend Option A (Dedicated SolidJS page/container registered in `page-registry.ts`) as primary architectural path to ensure zero blast radius on legacy typing engine, strict compliance with CODING_STANDARDS.md, and robust a11y.

## Artifact Index
- handoff.md — Complete structured survey report
- progress.md — Liveness heartbeat
