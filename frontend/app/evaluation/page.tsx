"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import ProtectedRoute from "@/components/ProtectedRoute";

import {
  ApiError,
  getEvaluationBenchmark,
  getEvaluationSummary,
} from "@/lib/api";


type JsonObject =
  Record<
    string,
    unknown
  >;


function asObject(
  value: unknown
): JsonObject {
  if (
    typeof value ===
      "object" &&
    value !== null &&
    !Array.isArray(
      value
    )
  ) {
    return value as
      JsonObject;
  }


  return {};
}


function prettyLabel(
  value: string
): string {
  return value
    .replaceAll(
      "_",
      " "
    )
    .replace(
      /\b\w/g,
      (
        letter
      ) =>
        letter.toUpperCase()
    );
}


function formatValue(
  value: unknown
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }


  if (
    typeof value ===
      "boolean"
  ) {
    return value
      ? "Yes"
      : "No";
  }


  if (
    typeof value ===
      "number"
  ) {
    return String(
      value
    );
  }


  if (
    typeof value ===
      "string"
  ) {
    return value;
  }


  return JSON.stringify(
    value
  );
}


function MetricGrid({
  data,
}: {
  data:
    JsonObject;
}) {
  const simpleEntries =
    Object.entries(
      data
    ).filter(
      (
        [
          ,
          value,
        ]
      ) =>
        typeof value ===
          "string" ||
        typeof value ===
          "number" ||
        typeof value ===
          "boolean"
    );


  if (
    simpleEntries.length ===
    0
  ) {
    return null;
  }


  return (
    <div
      className="
        mt-6
        grid
        gap-4
        sm:grid-cols-2
        xl:grid-cols-3
      "
    >
      {simpleEntries.map(
        (
          [
            key,
            value,
          ]
        ) => (
          <div
            key={
              key
            }
            className="
              rounded-2xl
              border
              border-cyan-400/15
              bg-[#031522]
              p-5
              transition
              duration-300
              hover:-translate-y-1
              hover:border-cyan-400/30
            "
          >
            <p
              className="
                text-xs
                font-bold
                uppercase
                tracking-wider
                text-slate-500
              "
            >
              {prettyLabel(
                key
              )}
            </p>

            <p
              className="
                mt-3
                break-words
                text-xl
                font-bold
                text-white
              "
            >
              {formatValue(
                value
              )}
            </p>
          </div>
        )
      )}
    </div>
  );
}


function JsonEvidence({
  title,
  data,
}: {
  title: string;
  data: unknown;
}) {
  return (
    <div
      className="
        rounded-3xl
        border
        border-cyan-400/15
        bg-[#061a2a]
        p-6
        lg:p-8
      "
    >
      <h2
        className="
          text-2xl
          font-bold
          text-white
        "
      >
        {title}
      </h2>

      <MetricGrid
        data={
          asObject(
            data
          )
        }
      />

      <details
        className="
          mt-6
          group
        "
      >
        <summary
          className="
            cursor-pointer
            text-sm
            font-semibold
            text-cyan-300
          "
        >
          View complete evidence
        </summary>

        <pre
          className="
            mt-4
            max-h-[500px]
            overflow-auto
            rounded-2xl
            border
            border-slate-800
            bg-[#020d19]
            p-5
            text-sm
            leading-6
            text-slate-300
          "
        >
          {JSON.stringify(
            data,
            null,
            2
          )}
        </pre>
      </details>
    </div>
  );
}


export default function EvaluationPage() {
  const [
    summary,
    setSummary,
  ] =
    useState<
      unknown
    >(null);


  const [
    benchmark,
    setBenchmark,
  ] =
    useState<
      unknown
    >(null);


  const [
    loading,
    setLoading,
  ] =
    useState(true);


  const [
    error,
    setError,
  ] =
    useState("");


  const [
    requestId,
    setRequestId,
  ] =
    useState<
      string |
      undefined
    >();


  const loadEvaluation =
    useCallback(
      async () => {
        try {
          setLoading(true);
          setError("");
          setRequestId(
            undefined
          );


          const [
            summaryData,
            benchmarkData,
          ] =
            await Promise.all([
              getEvaluationSummary<
                unknown
              >(),

              getEvaluationBenchmark<
                unknown
              >(),
            ]);


          setSummary(
            summaryData
          );

          setBenchmark(
            benchmarkData
          );

        } catch (caught) {
          if (
            caught instanceof
              ApiError
          ) {
            setError(
              caught.message
            );

            setRequestId(
              caught.requestId
            );

          } else {
            setError(
              caught instanceof Error
                ? caught.message
                : "Unable to load evaluation."
            );
          }

        } finally {
          setLoading(false);
        }
      },
      []
    );


  useEffect(() => {
    void loadEvaluation();
  }, [
    loadEvaluation,
  ]);


  return (
    <ProtectedRoute>
      <main
        className="
          min-h-screen
          bg-[#020d19]
          text-white
        "
      >
        <section
          className="
            mx-auto
            max-w-[1500px]
            px-6
            py-12
            lg:px-10
            lg:py-16
          "
        >
          <div
            className="
              flex
              flex-col
              gap-5
              md:flex-row
              md:items-end
              md:justify-between
            "
          >
            <div>
              <p
                className="
                  text-sm
                  font-bold
                  uppercase
                  tracking-[0.2em]
                  text-cyan-400
                "
              >
                Operational evaluation
              </p>

              <h1
                className="
                  mt-3
                  text-4xl
                  font-bold
                  tracking-tight
                  md:text-5xl
                "
              >
                Prove the system works.
              </h1>

              <p
                className="
                  mt-4
                  max-w-3xl
                  text-lg
                  leading-8
                  text-slate-400
                "
              >
                RippleProof combines production
                run evidence with deterministic
                benchmark results instead of
                relying on an LLM to claim
                correctness.
              </p>
            </div>


            <button
              type="button"
              onClick={
                () =>
                  void loadEvaluation()
              }
              disabled={
                loading
              }
              className="
                rounded-xl
                border
                border-cyan-400/20
                bg-cyan-400/5
                px-5
                py-3
                font-semibold
                text-cyan-200
                transition
                hover:-translate-y-0.5
                hover:bg-cyan-400/10
                disabled:opacity-50
              "
            >
              Refresh evaluation
            </button>
          </div>


          {error && (
            <div
              className="
                mt-8
                rounded-2xl
                border
                border-rose-400/25
                bg-rose-500/5
                p-5
              "
            >
              <p
                className="
                  font-semibold
                  text-rose-300
                "
              >
                Evaluation unavailable
              </p>

              <p
                className="
                  mt-1
                  text-sm
                  text-rose-200/80
                "
              >
                {error}
              </p>

              {requestId && (
                <p
                  className="
                    mt-2
                    text-xs
                    text-slate-500
                  "
                >
                  Request ID:{" "}
                  {requestId}
                </p>
              )}
            </div>
          )}


          {loading ? (
            <div
              className="
                mt-10
                grid
                gap-6
                xl:grid-cols-2
              "
            >
              <div
                className="
                  h-96
                  animate-pulse
                  rounded-3xl
                  bg-[#061a2a]
                "
              />

              <div
                className="
                  h-96
                  animate-pulse
                  rounded-3xl
                  bg-[#061a2a]
                "
              />
            </div>
          ) : (
            <div
              className="
                mt-10
                grid
                gap-6
                xl:grid-cols-2
              "
            >
              <JsonEvidence
                title="Production evaluation"
                data={
                  summary
                }
              />

              <JsonEvidence
                title="Deterministic benchmark"
                data={
                  benchmark
                }
              />
            </div>
          )}


          <div
            className="
              mt-8
              rounded-3xl
              border
              border-emerald-400/20
              bg-gradient-to-r
              from-emerald-400/[0.05]
              to-cyan-400/[0.05]
              p-6
              lg:p-8
            "
          >
            <p
              className="
                text-xs
                font-bold
                uppercase
                tracking-[0.2em]
                text-emerald-400
              "
            >
              Evidence-first architecture
            </p>

            <h2
              className="
                mt-3
                text-2xl
                font-bold
              "
            >
              AI interprets. Software proves.
            </h2>

            <p
              className="
                mt-3
                max-w-3xl
                leading-7
                text-slate-400
              "
            >
              Semantic reasoning identifies
              likely policy dependencies, while
              deterministic tests establish
              machine-verifiable proof that the
              new rule is actually enforced.
            </p>
          </div>
        </section>
      </main>
    </ProtectedRoute>
  );
}