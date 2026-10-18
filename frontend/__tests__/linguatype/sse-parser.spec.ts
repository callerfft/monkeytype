import { assert, describe, it } from "vitest";

import {
  createSSEParserState,
  normalizeGrammarErrors,
  parseSSEChunks,
} from "../../src/ts/queries/linguatype-api";
import type {
  GrammarErrorSpan,
  LatencyBreakdown,
  SemanticValidation,
  SessionMetrics,
  StyleAlternative,
} from "../../src/ts/states/linguatype";

describe("LinguaType SSE Stream Parser", () => {
  it("parses session_start event correctly", () => {
    const state = createSSEParserState();
    const rawChunk =
      'event: session_start\ndata: {"session_id":"uuid-1234","status":"active"}\n\n';

    const events = parseSSEChunks(rawChunk, state);
    assert.strictEqual(events.length, 1);
    assert.strictEqual(events[0]?.event, "session_start");
    assert.deepStrictEqual(events[0]?.data, {
      session_id: "uuid-1234",
      status: "active",
    });
  });

  it("parses progressive token events", () => {
    const state = createSSEParserState();
    const chunk1 = 'event: token\ndata: {"text":"Hello "}\n\n';
    const chunk2 = 'event: token\ndata: {"text":"world!"}\n\n';

    const events1 = parseSSEChunks(chunk1, state);
    const events2 = parseSSEChunks(chunk2, state);

    assert.strictEqual(events1.length, 1);
    assert.strictEqual(events1[0]?.event, "token");
    assert.deepStrictEqual(events1[0]?.data, { text: "Hello " });

    assert.strictEqual(events2.length, 1);
    assert.strictEqual(events2[0]?.event, "token");
    assert.deepStrictEqual(events2[0]?.data, { text: "world!" });
  });

  it("parses grammar_errors event (array format)", () => {
    const state = createSSEParserState();
    const errors: GrammarErrorSpan[] = [
      {
        start: 0,
        end: 4,
        original_text: "Thsi",
        message: "Spelling mistake",
        suggestion: "This",
        category: "spelling",
        severity: "error",
      },
    ];
    const chunk = `event: grammar_errors\ndata: ${JSON.stringify(errors)}\n\n`;

    const events = parseSSEChunks(chunk, state);
    assert.strictEqual(events.length, 1);
    assert.strictEqual(events[0]?.event, "grammar_errors");

    const normalized = normalizeGrammarErrors(events[0]?.data);
    assert.strictEqual(normalized.length, 1);
    assert.strictEqual(normalized[0]?.original_text, "Thsi");
    assert.strictEqual(normalized[0]?.suggestion, "This");
    assert.strictEqual(normalized[0]?.start, 0);
    assert.strictEqual(normalized[0]?.end, 4);
  });

  it("normalizes grammar_errors object wrapper ({ errors: [...] })", () => {
    const wrapped = {
      errors: [
        {
          start: 5,
          end: 7,
          original_text: "is",
          message: "Subject-verb agreement",
          suggestion: "are",
          category: "agreement",
          severity: "error",
        },
      ],
    };
    const normalized = normalizeGrammarErrors(wrapped);
    assert.strictEqual(normalized.length, 1);
    assert.strictEqual(normalized[0]?.suggestion, "are");
  });

  it("parses semantic_check event correctly", () => {
    const state = createSSEParserState();
    const semPayload: SemanticValidation = {
      is_valid: true,
      score: 95.5,
      explanation: "Sentence accurately translates the source text.",
      missing_concepts: [],
    };
    const chunk = `event: semantic_check\ndata: ${JSON.stringify(semPayload)}\n\n`;

    const events = parseSSEChunks(chunk, state);
    assert.strictEqual(events.length, 1);
    assert.strictEqual(events[0]?.event, "semantic_check");
    assert.deepStrictEqual(events[0]?.data, semPayload);
  });

  it("parses style_alternative event (strictly ONE suggestion)", () => {
    const state = createSSEParserState();
    const stylePayload: StyleAlternative = {
      style: "conversational",
      text: "AI tech is quickly transforming how we learn foreign languages.",
      explanation: "Uses more natural everyday conversational idioms.",
    };
    const chunk = `event: style_alternative\ndata: ${JSON.stringify(stylePayload)}\n\n`;

    const events = parseSSEChunks(chunk, state);
    assert.strictEqual(events.length, 1);
    assert.strictEqual(events[0]?.event, "style_alternative");
    assert.deepStrictEqual(events[0]?.data, stylePayload);
  });

  it("parses metrics event correctly", () => {
    const state = createSSEParserState();
    const metricsPayload: SessionMetrics = {
      wpm: 68.4,
      accuracy_score: 98.0,
      time_spent_ms: 12500,
      word_count: 14,
      target_word_count: 12,
      target_met: true,
      word_limit_exceeded: false,
      timer_expired: false,
    };
    const chunk = `event: metrics\ndata: ${JSON.stringify(metricsPayload)}\n\n`;

    const events = parseSSEChunks(chunk, state);
    assert.strictEqual(events.length, 1);
    assert.strictEqual(events[0]?.event, "metrics");
    assert.deepStrictEqual(events[0]?.data, metricsPayload);
  });

  it("parses done event with latency telemetry", () => {
    const state = createSSEParserState();
    const latency: LatencyBreakdown = {
      ttft_ms: 220,
      inference_duration_ms: 1100,
      pipeline_duration_ms: 1350,
    };
    const donePayload = {
      evaluation_id: "eval-9999",
      result_id: "res-8888",
      latency,
    };
    const chunk = `event: done\ndata: ${JSON.stringify(donePayload)}\n\n`;

    const events = parseSSEChunks(chunk, state);
    assert.strictEqual(events.length, 1);
    assert.strictEqual(events[0]?.event, "done");
    assert.deepStrictEqual(events[0]?.data, donePayload);
  });

  it("parses error event cleanly", () => {
    const state = createSSEParserState();
    const errorPayload = {
      code: "INFERENCE_TIMEOUT",
      message: "LLM evaluation timeout exceeded (> 3s)",
    };
    const chunk = `event: error\ndata: ${JSON.stringify(errorPayload)}\n\n`;

    const events = parseSSEChunks(chunk, state);
    assert.strictEqual(events.length, 1);
    assert.strictEqual(events[0]?.event, "error");
    assert.deepStrictEqual(events[0]?.data, errorPayload);
  });

  it("handles chunk fragmentation and partial lines across boundaries", () => {
    const state = createSSEParserState();

    // Split across arbitrary character boundaries
    const part1 = "event: to";
    const part2 = 'ken\ndata: {"te';
    const part3 = 'xt":"split chunk"}\n\n';

    const res1 = parseSSEChunks(part1, state);
    assert.strictEqual(res1.length, 0);

    const res2 = parseSSEChunks(part2, state);
    assert.strictEqual(res2.length, 0);

    const res3 = parseSSEChunks(part3, state);
    assert.strictEqual(res3.length, 1);
    assert.strictEqual(res3[0]?.event, "token");
    assert.deepStrictEqual(res3[0]?.data, { text: "split chunk" });
  });

  it("ignores SSE comments and heartbeats", () => {
    const state = createSSEParserState();
    const chunk =
      ': keepalive heartbeat\n\nevent: token\ndata: {"text":"hi"}\n\n';

    const events = parseSSEChunks(chunk, state);
    assert.strictEqual(events.length, 1);
    assert.strictEqual(events[0]?.event, "token");
    assert.deepStrictEqual(events[0]?.data, { text: "hi" });
  });

  it("handles multi-line and carriage-return newlines", () => {
    const state = createSSEParserState();
    const chunk = 'event: token\r\ndata: {"text":"CRLF"}\r\n\r\n';

    const events = parseSSEChunks(chunk, state);
    assert.strictEqual(events.length, 1);
    assert.strictEqual(events[0]?.event, "token");
    assert.deepStrictEqual(events[0]?.data, { text: "CRLF" });
  });
});
