"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import Link from "next/link";

import ProtectedRoute from "@/components/ProtectedRoute";

import {
  ApiError,
  getRuns,
} from "@/lib/api";


type JsonObject =
  Record<
    string,
    unknown
  >;


type RunItem = {
  id: string;

  policyName:
    string;

  status:
    string;

  createdAt:
    string;

  raw:
    JsonObject;
};


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


function normalizeRun(
  value: unknown
): RunItem | null {
  const item =
    asObject(
      value
    );


  if (!item) {
    return null;
  }


  const id =
    asString(
      item.id ??
      item.run_id
    );


  if (!id) {
    return null;
  }


  const policy =
    asObject(
      item.policy
    );


  return {
    id,

    policyName:
      asString(
        item.policy_name ??
        policy?.name ??
        item.name,
        "Policy analysis"
      ),

    status:
      asString(
        item.status,
        "unknown"
      ),

    createdAt:
      asString(
        item.created_at ??
        item.createdAt,
        ""
      ),

    raw:
      item,
  };
}


function normalizeRuns(
  data: unknown
): RunItem[] {
  let source:
    unknown[] =
    [];


  if (
    Array.isArray(
      data
    )
  ) {
    source =
      data;

  } else {
    const object =
      asObject(
        data
      );


    if (
      object &&
      Array.isArray(
        object.runs
      )
    ) {
      source =
        object.runs;

    } else if (
      object &&
      Array.isArray(
        object.items
      )
    ) {
      source =
        object.items;

    } else if (
      object &&
      Array.isArray(
        object.results
      )
    ) {
      source =
        object.results;
    }
  }


  return source
    .map(
      normalizeRun
    )
    .filter(
      (
        item
      ): item is RunItem =>
        Boolean(
          item
        )
    );
}


function prettyStatus(
  status: string
): string {
  return status
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


function statusClasses(
  status: string
): string {
  const normalized =
    status.toLowerCase();


  if (
    normalized.includes(
      "verified"
    ) ||
    normalized.includes(
      "complete"
    )
  ) {
    return (
      "border-emerald-400/25 bg-emerald-400/10 text-emerald-300"
    );
  }


  if (
    normalized.includes(
      "approved"
    )
  ) {
    return (
      "border-cyan-400/25 bg-cyan-400/10 text-cyan-300"
    );
  }


  if (
    normalized.includes(
      "fail"
    ) ||
    normalized.includes(
      "error"
    )
  ) {
    return (
      "border-rose-400/25 bg-rose-400/10 text-rose-300"
    );
  }


  return (
    "border-amber-400/25 bg-amber-400/10 text-amber-300"
  );
}


function formatDate(
  value: string
): string {
  if (!value) {
    return "—";
  }


  const date =
    new Date(
      value
    );


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value;
  }


  return date.toLocaleString();
}


export default function RunsPage() {
  const [
    runs,
    setRuns,
  ] =
    useState<
      RunItem[]
    >([]);


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


  const loadRuns =
    useCallback(
      async () => {
        try {
          setLoading(true);
          setError("");
          setRequestId(
            undefined
          );


          const data =
            await getRuns<
              unknown
            >();


          setRuns(
            normalizeRuns(
              data
            )
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
                : "Unable to load run history."
            );
          }

        } finally {
          setLoading(false);
        }
      },
      []
    );


  useEffect(() => {
    void loadRuns();
  }, [
    loadRuns,
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
              gap-6
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
                Evidence history
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
                Analysis runs
              </h1>

              <p
                className="
                  mt-4
                  max-w-2xl
                  text-lg
                  leading-8
                  text-slate-400
                "
              >
                Every analysis, approval and
                verification step remains
                available as persistent evidence.
              </p>
            </div>


            <div
              className="
                flex
                gap-3
              "
            >
              <button
                type="button"
                onClick={
                  () =>
                    void loadRuns()
                }
                disabled={
                  loading
                }
                className="
                  rounded-xl
                  border
                  border-slate-700
                  px-5
                  py-3
                  font-semibold
                  text-slate-200
                  transition
                  hover:border-cyan-400/40
                  hover:text-white
                  disabled:opacity-50
                "
              >
                Refresh
              </button>

              <Link
                href="/custom"
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
                "
              >
                New analysis
              </Link>
            </div>
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
                Unable to load runs
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
                gap-5
                md:grid-cols-2
                xl:grid-cols-3
              "
            >
              {Array.from({
                length: 6,
              }).map(
                (
                  _,
                  index
                ) => (
                  <div
                    key={
                      index
                    }
                    className="
                      h-52
                      animate-pulse
                      rounded-3xl
                      border
                      border-slate-800
                      bg-[#061a2a]
                    "
                  />
                )
              )}
            </div>
          ) : runs.length ===
            0 ? (
            <div
              className="
                mt-10
                rounded-3xl
                border
                border-cyan-400/15
                bg-[#061a2a]
                p-10
                text-center
              "
            >
              <h2
                className="
                  text-2xl
                  font-bold
                "
              >
                No analysis runs yet.
              </h2>

              <p
                className="
                  mt-3
                  text-slate-400
                "
              >
                Run your first real policy
                change analysis to create
                persistent evidence.
              </p>

              <Link
                href="/custom"
                className="
                  mt-6
                  inline-flex
                  rounded-xl
                  bg-cyan-400
                  px-5
                  py-3
                  font-bold
                  text-slate-950
                "
              >
                Start analysis
              </Link>
            </div>
          ) : (
            <div
              className="
                mt-10
                grid
                gap-5
                md:grid-cols-2
                xl:grid-cols-3
              "
            >
              {runs.map(
                (
                  run
                ) => (
                  <Link
                    key={
                      run.id
                    }
                    href={
                      `/runs/${encodeURIComponent(
                        run.id
                      )}`
                    }
                    className="
                      group
                      rounded-3xl
                      border
                      border-cyan-400/15
                      bg-[#061a2a]
                      p-6
                      transition
                      duration-300
                      hover:-translate-y-1
                      hover:border-cyan-400/35
                      hover:shadow-xl
                      hover:shadow-cyan-500/5
                    "
                  >
                    <div
                      className="
                        flex
                        items-start
                        justify-between
                        gap-4
                      "
                    >
                      <span
                        className={`
                          rounded-full
                          border
                          px-3
                          py-1
                          text-xs
                          font-bold
                          ${statusClasses(
                            run.status
                          )}
                        `}
                      >
                        {prettyStatus(
                          run.status
                        )}
                      </span>

                      <span
                        className="
                          text-slate-600
                          transition
                          group-hover:translate-x-1
                          group-hover:text-cyan-300
                        "
                      >
                        →
                      </span>
                    </div>


                    <h2
                      className="
                        mt-6
                        text-xl
                        font-bold
                        text-white
                      "
                    >
                      {run.policyName}
                    </h2>


                    <p
                      className="
                        mt-3
                        text-sm
                        text-slate-500
                      "
                    >
                      {formatDate(
                        run.createdAt
                      )}
                    </p>


                    <div
                      className="
                        mt-7
                        border-t
                        border-slate-800
                        pt-4
                      "
                    >
                      <p
                        className="
                          truncate
                          font-mono
                          text-xs
                          text-slate-500
                        "
                      >
                        {run.id}
                      </p>
                    </div>
                  </Link>
                )
              )}
            </div>
          )}
        </section>
      </main>
    </ProtectedRoute>
  );
}