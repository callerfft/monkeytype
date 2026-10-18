# Progress Tracker — Milestone 4 (Auth & Firebase App Hosting)
Last visited: 2026-10-17T07:15:35Z

- [x] Initial dispatch received and BRIEFING.md created
- [x] Read contracts, PROJECT.md, ORIGINAL_REQUEST.md
- [x] Inspect existing `frontend/src/ts/firebase.ts` and `LinguaTypeConfig.tsx`
- [x] Plan implementation details
- [x] Implement Magic Link auth functions in `frontend/src/ts/firebase.ts` (sendMagicLink, isMagicLink, completeMagicLinkSignIn) preserving Google OAuth
- [x] Implement user profile preference sync in `LinguaTypeConfig.tsx` and `linguatype-api.ts` (GET & PUT /api/v1/user/profile with Bearer token)
- [x] Create `apphosting.yaml` at project root with runConfig (cpu: 1, memoryMiB: 1024, minInstances: 1, maxInstances: 5, concurrency: 80) and env vars
- [x] Write comprehensive unit tests in `frontend/src/ts/__tests__/linguatype/auth-settings.spec.ts`
- [x] Run vitest/node test runner on `auth-settings.spec.ts` and ensure 100% pass rate (14/14 tests pass, full suite 33/33 tests pass)
- [x] Verify backend tests (26/26 passed)
- [x] Write handoff report and notify orchestrator
