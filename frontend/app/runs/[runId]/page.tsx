"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import Link from "next/link";

import {
  useParams,
} from "next/navigation";

import ProtectedRoute from "@/components/ProtectedRoute";

import {
  ApiError,
  approveRun,
  getRun,
  verifyDemo,
} from "@/lib/api";


type JsonObject =
  Record<
    string,
    unknown
  >;


function asObject(
  value: unknown
): JsonObject | null {
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


  return null;
}


function asString(
  value: unknown,
  fallback = ""
): string {
  return typeof value ===
    "string"
      ? value
      : fallback;
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
      (letter) =>
        letter.toUpperCase()
    );
}


function readableValue(
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
      "string" ||
    typeof value ===
      "number"
  ) {
    return String(
      value
    );
  }


  return JSON.stringify(
    value,
    null,
    2
  );
}


export default function RunDetailPage() {
  const params =
    useParams<{
      runId: string;
    }>();


  const runId =
    Array.isArray(
      params.runId
    )
      ? params.runId[0]
      : params.runId;


  const [
    run,
    setRun,
  ] =
    useState<
      JsonObject |
      null
    >(null);


  const [
    loading,
    setLoading,
  ] =
    useState(true);


  const [
    action,
    setAction,
  ] =
    useState<
      "approve" |
      "verify" |
      null
    >(null);


  const [
    error,
    setError,
  ] =
    useState("");


  const [
    success,
    setSuccess,
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


  const loadRun =
    useCallback(
      async () => {
        if (!runId) {
          return;
        }


        try {
          setLoading(true);
          setError("");
          setRequestId(
            undefined
          );


          const data =
            await getRun<
              JsonObject
            >(
              runId
            );


          setRun(
            data
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
                : "Unable to load this run."
            );
          }

        } finally {
          setLoading(false);
        }
      },
      [
        runId,
      ]
    );


  useEffect(() => {
    void loadRun();
  }, [
    loadRun,
  ]);


  async function handleApprove() {
    if (!runId) {
      return;
    }


    try {
      setAction(
        "approve"
      );

      setError("");
      setSuccess("");


      await approveRun(
        runId
      );


      setSuccess(
        "Repairs approved successfully."
      );


      await loadRun();

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
            : "Unable to approve this run."
        );
      }

    } finally {
      setAction(null);
    }
  }


  async function handleVerify() {
    if (!runId) {
      return;
    }


    try {
      setAction(
        "verify"
      );

      setError("");
      setSuccess("");


      await verifyDemo(
        runId
      );


      setSuccess(
        "Deterministic verification completed."
      );


      await loadRun();

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
            : "Verification failed."
        );
      }

    } finally {
      setAction(null);
    }
  }


  const status =
    useMemo(
      () =>
        asString(
          run?.status,
          "unknown"
        ),
      [
        run,
      ]
    );


  const policyObject =
    asObject(
      run?.policy
    );


  const policyName =
    asString(
      run?.policy_name ??
      policyObject?.name ??
      run?.name,
      "Policy analysis"
    );


  const highLevelFields =
    useMemo(
      () => {
        if (!run) {
          return [];
        }


        const preferred = [
          "status",
          "created_at",
          "updated_at",
          "findings_count",
          "affected_artifacts_count",
          "approved",
          "verified",
        ];


        return preferred
          .filter(
            (key) =>
              key in run
          )
          .map(
            (key) => ({
              key,
              value:
                run[key],
            })
          );
      },
      [
        run,
      ]
    );


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
          <Link
            href="/runs"
            className="
              inline-flex
              items-center
              gap-2
              text-sm
              font-semibold
              text-slate-400
              transition
              hover:text-cyan-300
            "
          >
            ← Run history
          </Link>


          {loading ? (
            <div
              className="
                mt-10
                space-y-5
              "
            >
              <div
                className="
                  h-52
                  animate-pulse
                  rounded-3xl
                  bg-[#061a2a]
                "
              />

              <div
                className="
                  h-72
                  animate-pulse
                  rounded-3xl
                  bg-[#061a2a]
                "
              />
            </div>
          ) : (
            <>
              <div
                className="
                  mt-8
                  rounded-3xl
                  border
                  border-cyan-400/15
                  bg-gradient-to-br
                  from-[#0a2340]
                  to-[#041522]
                  p-7
                  lg:p-10
                "
              >
                <div
                  className="
                    flex
                    flex-col
                    gap-7
                    xl:flex-row
                    xl:items-center
                    xl:justify-between
                  "
                >
                  <div>
                    <div
                      className="
                        flex
                        flex-wrap
                        items-center
                        gap-3
                      "
                    >
                      <span
                        className="
                          rounded-full
                          border
                          border-cyan-400/25
                          bg-cyan-400/10
                          px-3
                          py-1
                          text-xs
                          font-bold
                          uppercase
                          tracking-wider
                          text-cyan-300
                        "
                      >
                        {prettyLabel(
                          status
                        )}
                      </span>

                      <span
                        className="
                          font-mono
                          text-xs
                          text-slate-500
                        "
                      >
                        {runId}
                      </span>
                    </div>


                    <h1
                      className="
                        mt-5
                        text-4xl
                        font-bold
                        tracking-tight
                        md:text-5xl
                      "
                    >
                      {policyName}
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
                      Review the discovered ripple,
                      approve evidence-backed repairs,
                      then execute deterministic proof
                      against the updated rule.
                    </p>
                  </div>


                  <div
                    className="
                      flex
                      flex-wrap
                      gap-3
                    "
                  >
                    <button
                      type="button"
                      onClick={
                        handleApprove
                      }
                      disabled={
                        action !==
                        null
                      }
                      className="
                        rounded-xl
                        border
                        border-cyan-400/30
                        bg-cyan-400/10
                        px-5
                        py-3
                        font-bold
                        text-cyan-200
                        transition
                        hover:-translate-y-0.5
                        hover:bg-cyan-400/15
                        disabled:cursor-not-allowed
                        disabled:opacity-50
                      "
                    >
                      {action ===
                      "approve"
                        ? "Approving..."
                        : "Approve repairs"}
                    </button>

                    <button
                      type="button"
                      onClick={
                        handleVerify
                      }
                      disabled={
                        action !==
                        null
                      }
                      className="
                        rounded-xl
                        bg-gradient-to-r
                        from-blue-500
                        to-cyan-400
                        px-5
                        py-3
                        font-bold
                        text-white
                        transition
                        hover:-translate-y-0.5
                        disabled:cursor-not-allowed
                        disabled:opacity-50
                      "
                    >
                      {action ===
                      "verify"
                        ? "Verifying..."
                        : "Run verification"}
                    </button>
                  </div>
                </div>
              </div>


              {error && (
                <div
                  className="
                    mt-6
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


              {success && (
                <div
                  className="
                    mt-6
                    rounded-2xl
                    border
                    border-emerald-400/25
                    bg-emerald-400/5
                    p-5
                    font-semibold
                    text-emerald-300
                  "
                >
                  {success}
                </div>
              )}


              {highLevelFields.length >
                0 && (
                <div
                  className="
                    mt-8
                    grid
                    gap-4
                    sm:grid-cols-2
                    xl:grid-cols-4
                  "
                >
                  {highLevelFields.map(
                    (
                      item
                    ) => (
                      <div
                        key={
                          item.key
                        }
                        className="
                          rounded-2xl
                          border
                          border-cyan-400/15
                          bg-[#061a2a]
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
                            item.key
                          )}
                        </p>

                        <p
                          className="
                            mt-3
                            break-words
                            text-lg
                            font-semibold
                            text-white
                          "
                        >
                          {readableValue(
                            item.value
                          )}
                        </p>
                      </div>
                    )
                  )}
                </div>
              )}


              {run && (
                <div
                  className="
                    mt-8
                    rounded-3xl
                    border
                    border-cyan-400/15
                    bg-[#061a2a]
                    p-6
                    lg:p-8
                  "
                >
                  <div
                    className="
                      flex
                      items-center
                      justify-between
                    "
                  >
                    <div>
                      <p
                        className="
                          text-xs
                          font-bold
                          uppercase
                          tracking-[0.2em]
                          text-cyan-400
                        "
                      >
                        Persistent evidence
                      </p>

                      <h2
                        className="
                          mt-2
                          text-2xl
                          font-bold
                        "
                      >
                        Full run record
                      </h2>
                    </div>
                  </div>


                  <pre
                    className="
                      mt-6
                      max-h-[650px]
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
                      run,
                      null,
                      2
                    )}
                  </pre>
                </div>
              )}
            </>
          )}
        </section>
      </main>
    </ProtectedRoute>
  );
}