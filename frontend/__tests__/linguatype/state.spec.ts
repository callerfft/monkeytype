import { assert, describe, it } from "vitest";

import {
  calculateLocalMetrics,
  countWords,
  getCheckCaseAndPeriod,
  getDifficulty,
  getEffectiveMaxWords,
  getEffectiveTargetWords,
  getMarginBuffer,
  getMode,
  getPreferredStyle,
  getSessionStatus,
  getTargetMet,
  getTargetWordCount,
  getTimeLeft,
  getTimerSeconds,
  getUserText,
  getWordLimitExceeded,
  getWordsTyped,
  isCaseOrPeriodError,
  resetSession,
  setCheckCaseAndPeriod,
  setDifficulty,
  setMarginBuffer,
  setMode,
  setPreferredStyle,
  setPrompt,
  setSessionStatus,
  setTargetWordCount,
  setTimeLeft,
  setTimerSeconds,
  setUserText,
  type GrammarErrorSpan,
  type LinguaTypePrompt,
} from "../../src/ts/states/linguatype";

describe("LinguaType State & Metrics", () => {
  it("counts words correctly for various string inputs", () => {
    assert.strictEqual(countWords(""), 0);
    assert.strictEqual(countWords("   "), 0);
    assert.strictEqual(countWords("hello"), 1);
    assert.strictEqual(countWords("hello world"), 2);
    assert.strictEqual(countWords("   The  quick   brown  fox   jumps   "), 5);
    assert.strictEqual(countWords("one\ntwo\tthree"), 3);
  });

  it("calculates typing metrics accurately", () => {
    const metrics = calculateLocalMetrics(
      "The quick brown fox jumps over the lazy brown dog.",
      30000,
      10,
      15,
      0,
    );

    assert.strictEqual(metrics.wpm, 20);
    assert.strictEqual(metrics.word_count, 10);
    assert.strictEqual(metrics.target_met, true);
    assert.strictEqual(metrics.word_limit_exceeded, false);
    assert.strictEqual(metrics.accuracy_score, 100);
  });

  it("penalizes accuracy score for grammar errors and word deficit", () => {
    const metrics = calculateLocalMetrics(
      "This is bad text sentence",
      15000,
      10,
      15,
      2,
    );

    assert.strictEqual(metrics.accuracy_score, 65);
    assert.strictEqual(metrics.target_met, false);
  });

  it("identifies when word count limit is exceeded", () => {
    const text =
      "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen";
    const metrics = calculateLocalMetrics(text, 20000, 10, 15, 0);

    assert.strictEqual(metrics.word_count, 16);
    assert.strictEqual(metrics.word_limit_exceeded, true);
    assert.strictEqual(metrics.target_met, false);
  });

  it("manages configuration signals correctly", () => {
    setMode("situation_image");
    assert.strictEqual(getMode(), "situation_image");

    setTimerSeconds(15);
    assert.strictEqual(getTimerSeconds(), 15);

    setTargetWordCount(12);
    assert.strictEqual(getTargetWordCount(), 12);

    setMarginBuffer(4);
    assert.strictEqual(getMarginBuffer(), 4);

    setPreferredStyle("formal");
    assert.strictEqual(getPreferredStyle(), "formal");

    setDifficulty("hard");
    assert.strictEqual(getDifficulty(), "hard");

    // Revert to defaults
    setMode("translation");
    setTimerSeconds(30);
    setTargetWordCount(10);
    setMarginBuffer(5);
    setPreferredStyle("conversational");
    setDifficulty("medium");
  });

  it("manages session lifecycle and resets cleanly", () => {
    setUserText("Some typed sentence");
    setTimeLeft(12);
    setSessionStatus("active");

    assert.strictEqual(getUserText(), "Some typed sentence");
    assert.strictEqual(getWordsTyped(), 3);
    assert.strictEqual(getSessionStatus(), "active");

    resetSession();

    assert.strictEqual(getUserText(), "");
    assert.strictEqual(getWordsTyped(), 0);
    assert.strictEqual(getTimeLeft(), 30);
    assert.strictEqual(getSessionStatus(), "ready");
  });

  it("updates computed limits when a prompt is attached", () => {
    const testPrompt: LinguaTypePrompt = {
      id: "test-p1",
      type: "translation",
      source_language: "ru",
      target_language: "en",
      content: "Тестовая фраза",
      difficulty: "easy",
      target_word_count: 8,
      margin_buffer: 3,
      max_word_count: 11,
    };

    setPrompt(testPrompt);
    assert.strictEqual(getEffectiveTargetWords(), 8);
    assert.strictEqual(getEffectiveMaxWords(), 11);

    setUserText("one two three four five six seven eight");
    assert.strictEqual(getWordsTyped(), 8);
    assert.strictEqual(getTargetMet(), true);
    assert.strictEqual(getWordLimitExceeded(), false);

    setUserText(
      "one two three four five six seven eight nine ten eleven twelve",
    );
    assert.strictEqual(getWordsTyped(), 12);
    assert.strictEqual(getWordLimitExceeded(), true);
    assert.strictEqual(getTargetMet(), false);

    // Clean up
    setPrompt(null);
    setUserText("");
  });

  it("handles checkCaseAndPeriod configuration toggle", () => {
    setCheckCaseAndPeriod(true);
    assert.strictEqual(getCheckCaseAndPeriod(), true);

    setCheckCaseAndPeriod(false);
    assert.strictEqual(getCheckCaseAndPeriod(), false);
  });

  it("identifies case and terminal period errors accurately with isCaseOrPeriodError", () => {
    const text = "hello world this is a test";

    const capError: GrammarErrorSpan = {
      start: 0,
      end: 1,
      original_text: "h",
      suggestion: "H",
      message: "Sentence should start with a capital letter",
      category: "punctuation",
      severity: "warning",
    };

    const periodError: GrammarErrorSpan = {
      start: 26,
      end: 27,
      original_text: "",
      suggestion: ".",
      message: "Missing terminal period at the end of the sentence",
      category: "punctuation",
      severity: "warning",
    };

    const regularError: GrammarErrorSpan = {
      start: 6,
      end: 11,
      original_text: "world",
      suggestion: "word",
      message: "Incorrect vocabulary usage",
      category: "word_choice",
      severity: "error",
    };

    assert.strictEqual(isCaseOrPeriodError(capError, text), true);
    assert.strictEqual(isCaseOrPeriodError(periodError, text), true);
    assert.strictEqual(isCaseOrPeriodError(regularError, text), false);
  });
});
