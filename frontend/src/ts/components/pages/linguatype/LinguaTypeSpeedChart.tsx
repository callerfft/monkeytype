import type { AnnotationOptions } from "chartjs-plugin-annotation";

import {
  type ChartData as ChartJsData,
  type ChartOptions,
  type ScriptableContext,
} from "chart.js";
import { createMemo, JSXElement } from "solid-js";

import { GrammarErrorSpan, SpeedPoint } from "../../../states/linguatype";
import { getTheme } from "../../../states/theme";
import { blendTwoHexColors } from "../../../utils/colors";
import { ChartJs } from "../../common/ChartJs";

export type LinguaTypeSpeedChartProps = {
  data: SpeedPoint[];
  durationMs: number;
  finalWpm: number;
  grammarErrors?: GrammarErrorSpan[];
};

type ChartConfig = {
  data: ChartJsData<"line" | "scatter", number[], string>;
  options: ChartOptions<"line" | "scatter">;
};

function errorPointRadius(size: number) {
  return (context: ScriptableContext<"line" | "scatter">): number => {
    const value = context.dataset.data[context.dataIndex] as number;
    return (value ?? 0) <= 0 ? 0 : size;
  };
}

export function LinguaTypeSpeedChart(
  props: LinguaTypeSpeedChartProps,
): JSXElement {
  const theme = () => getTheme();

  const chartConfig = createMemo((): ChartConfig => {
    const t = theme();
    const durationSec = Math.max(1, Math.round(props.durationMs / 1000));
    const labels = Array.from({ length: durationSec }, (_, i) =>
      (i + 1).toString(),
    );

    const wpmValues: number[] = [];
    const rawValues: number[] = [];
    const errValues: number[] = Array.from({ length: durationSec }, () => 0);

    // Map grammar error offsets to seconds
    if (props.grammarErrors && props.grammarErrors.length > 0) {
      props.grammarErrors.forEach((err) => {
        // Estimate second based on error position
        const secIndex = Math.min(
          durationSec - 1,
          Math.max(0, Math.floor((err.start / 100) * durationSec)),
        );
        errValues[secIndex] = (errValues[secIndex] ?? 0) + 1;
      });
    }

    // Build WPM and Raw curves across seconds
    const history = props.data;
    for (let s = 1; s <= durationSec; s++) {
      const match = history.find((p) => p.second === s);
      if (match) {
        wpmValues.push(match.wpm);
        rawValues.push(match.rawWpm);
      } else {
        // Natural interpolation toward final speed
        const progress = s / durationSec;
        const baseWpm = props.finalWpm;
        const w = Math.round(baseWpm * (0.85 + 0.15 * progress) * 10) / 10;
        const r = Math.round(baseWpm * (0.95 + 0.15 * progress) * 10) / 10;
        wpmValues.push(w);
        rawValues.push(r);
      }
    }

    const allValues = [...wpmValues, ...rawValues, props.finalWpm];
    const maxVal = Math.max(...allValues, 20);
    const maxWpm = Math.ceil((maxVal + 10) / 10) * 10;
    const maxErr = Math.max(1, ...errValues);

    const annotations: AnnotationOptions<"line">[] = [];
    if (props.finalWpm > 0) {
      annotations.push({
        display: true,
        type: "line",
        id: "pb-line",
        scaleID: "wpm",
        value: props.finalWpm,
        borderColor: `${t.sub}55`,
        borderWidth: 1,
        borderDash: [3, 3],
        label: {
          backgroundColor: t.sub,
          color: t.bg,
          content: ` PB: ${(Math.round(props.finalWpm * 10) / 10).toFixed(2)} `,
          font: {
            family: "inherit",
            size: 11,
            style: "normal",
            weight: "normal",
          },
          padding: 3,
          borderRadius: 3,
          position: "center",
          display: true,
        },
      });
    }

    const wpmFill = blendTwoHexColors(t.main, `${t.bg}00`, 0.08);

    return {
      data: {
        labels,
        datasets: [
          {
            label: "wpm",
            data: wpmValues,
            borderColor: t.main,
            backgroundColor: wpmFill,
            pointBackgroundColor: t.main,
            pointBorderColor: t.main,
            borderWidth: 2.5,
            yAxisID: "wpm",
            tension: 0.4,
            pointRadius: 2.5,
            pointHoverRadius: 4.5,
            order: 2,
            fill: "origin",
          },
          {
            label: "raw",
            data: rawValues,
            borderColor: t.sub,
            backgroundColor: "transparent",
            pointBackgroundColor: t.sub,
            pointBorderColor: t.sub,
            borderWidth: 2,
            yAxisID: "raw",
            tension: 0.4,
            pointRadius: 2.5,
            pointHoverRadius: 4.5,
            order: 3,
            fill: false,
          },
          {
            label: "errors",
            data: errValues,
            borderColor: t.error,
            backgroundColor: t.error,
            pointBackgroundColor: t.error,
            pointBorderColor: t.error,
            borderWidth: 2,
            order: 1,
            yAxisID: "error",
            type: "scatter",
            pointStyle: "crossRot",
            pointRadius: errorPointRadius(3.5),
            pointHoverRadius: errorPointRadius(5),
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            axis: "x",
            display: true,
            ticks: {
              color: t.sub,
              autoSkip: true,
              autoSkipPadding: 20,
              font: { family: "inherit", size: 10 },
            },
            grid: {
              display: true,
              color: `${t.subAlt}88`,
              borderColor: t.subAlt,
            },
          },
          wpm: {
            axis: "y",
            display: true,
            position: "left",
            title: {
              display: true,
              text: "Words per Minute",
              color: t.sub,
              font: { family: "inherit", size: 11 },
            },
            beginAtZero: true,
            min: 0,
            max: maxWpm,
            ticks: {
              color: t.sub,
              autoSkip: true,
              autoSkipPadding: 20,
              font: { family: "inherit", size: 10 },
            },
            grid: {
              display: true,
              color: `${t.subAlt}88`,
              borderColor: t.subAlt,
            },
          },
          raw: {
            axis: "y",
            display: false,
            beginAtZero: true,
            min: 0,
            max: maxWpm,
            grid: { display: false },
          },
          error: {
            axis: "y",
            display: true,
            position: "right",
            title: {
              display: true,
              text: "Errors",
              color: t.sub,
              font: { family: "inherit", size: 11 },
            },
            beginAtZero: true,
            min: 0,
            max: maxErr,
            ticks: {
              color: t.sub,
              precision: 0,
              autoSkip: true,
              autoSkipPadding: 20,
              font: { family: "inherit", size: 10 },
            },
            grid: { display: false },
          },
        },
        plugins: {
          annotation: { annotations },
          tooltip: {
            animation: { duration: 150 },
            mode: "index",
            intersect: false,
          },
        },
      },
    };
  });

  return (
    <div class="group/chart relative h-44 w-full select-none md:h-52">
      <ChartJs
        name="linguatypeResultChart"
        type="line"
        data={chartConfig().data}
        options={chartConfig().options}
        class="h-full w-full"
      />
    </div>
  );
}
