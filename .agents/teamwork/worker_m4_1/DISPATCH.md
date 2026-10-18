# Task Assignment: Worker M4 (Auth & Firebase App Hosting)

Working directory: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m4_1
Target files:
- frontend/src/ts/firebase.ts (Add Magic Link functions alongside Google OAuth)
- frontend/src/ts/components/pages/linguatype/LinguaTypeConfig.tsx (Persist user preferences to backend /api/v1/user/profile when authenticated)
- apphosting.yaml (Create Firebase App Hosting deployment configuration)
- frontend/src/ts/__tests__/linguatype/auth-settings.spec.ts (Automated tests for auth and settings)

Contract: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json
Project definition: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\orchestrator_1\PROJECT.md
Original Request: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Objectives
1. Firebase Auth Enhancement (`frontend/src/ts/firebase.ts`):
   - Add Magic Link (passwordless email link) authentication support:
     * `sendMagicLink(email: string, actionCodeSettings?: ActionCodeSettings): Promise<void>` using `sendSignInLinkToEmail`
     * `isMagicLink(url: string): boolean` using `isSignInWithEmailLink`
     * `completeMagicLinkSignIn(email: string, url: string): Promise<UserCredential>` using `signInWithEmailLink`
   - Preserve existing Google OAuth `signInWithPopup(GoogleAuthProvider)` and token retrieval `getIdToken()`.
2. Settings & History Synchronization:
   - In `LinguaTypeConfig.tsx`, when user is authenticated (via `getUserState()`), load user preferences from `GET /api/v1/user/profile` and persist changes via `PUT /api/v1/user/profile` (with Bearer token).
3. Firebase App Hosting Configuration:
   - Create `apphosting.yaml` at project root `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\apphosting.yaml`:
     * `runConfig`: `cpu: 1`, `memoryMiB: 1024`, `minInstances: 1` (to prevent cold starts per <3.0s SLA), `maxInstances: 5`, `concurrency: 80`
     * Environment variables configuration
4. Automated Verification:
   - Write unit tests in `frontend/src/ts/__tests__/linguatype/auth-settings.spec.ts` verifying Magic Link helper functions and profile serialization.
   - Run the unit tests and ensure all pass.
5. Write handoff report in `c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m4_1\handoff.md`.

## 2026-10-17T06:55:39Z
You are Worker 1 for Milestone 4 (Auth & Firebase App Hosting).
Your working directory is: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m4_1
Read:
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m4_1\DISPATCH.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\contracts\api_v1.json
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\orchestrator_1\PROJECT.md
- c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\ORIGINAL_REQUEST.md

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Implement:
1. Magic Link authentication functions in frontend/src/ts/firebase.ts (sendMagicLink, isMagicLink, completeMagicLinkSignIn) preserving Google OAuth.
2. User profile preference sync in LinguaTypeConfig.tsx.
3. apphosting.yaml at project root with runConfig (cpu: 1, memoryMiB: 1024, minInstances: 1, maxInstances: 5, concurrency: 80).
4. Unit tests in frontend/src/ts/__tests__/linguatype/auth-settings.spec.ts. Run tests and verify 100% pass rate.
Write your handoff report to c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype\.agents\teamwork\worker_m4_1\handoff.md and notify me via send_message when done.
