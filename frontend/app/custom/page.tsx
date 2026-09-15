"use client";

import {
  ChangeEvent,
  FormEvent,
  useState,
} from "react";

import Link from "next/link";

import {
  useRouter,
} from "next/navigation";

import ProtectedRoute from "@/components/ProtectedRoute";

import {
  ApiError,
  createCustomRun,
} from "@/lib/api";


type JsonObject =
  Record<
    string,
    unknown
  >;


function getRunId(
  value: unknown
): string | null {
  if (
    typeof value !==
      "object" ||
    value === null
  ) {
    return null;
  }


  const data =
    value as JsonObject;


  const possible =
    data.run_id ??
    data.id;


  if (
    typeof possible ===
      "string"
  ) {
    return possible;
  }


  const run =
    data.run;


  if (
    typeof run ===
      "object" &&
    run !== null
  ) {
    const runObject =
      run as JsonObject;


    const nestedId =
      runObject.id ??
      runObject.run_id;


    if (
      typeof nestedId ===
        "string"
    ) {
      return nestedId;
    }
  }


  return null;
}


export default function CustomPage() {
  const router =
    useRouter();


  const [
    policyName,
    setPolicyName,
  ] =
    useState(
      "Customer Refund Policy"
    );


  const [
    oldText,
    setOldText,
  ] =
    useState(
      "Customers may request a refund within 30 days of purchase."
    );


  const [
    newText,
    setNewText,
  ] =
    useState(
      "Customers may request a refund within 14 days of purchase."
    );


  const [
    files,
    setFiles,
  ] =
    useState<File[]>(
      []
    );


  const [
    loading,
    setLoading,
  ] =
    useState(false);


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


  const [
    result,
    setResult,
  ] =
    useState<
      JsonObject |
      null
    >(null);


  const [
    runId,
    setRunId,
  ] =
    useState<
      string |
      null
    >(null);


  function handleFiles(
    event:
      ChangeEvent<HTMLInputElement>
  ) {
    setFiles(
      Array.from(
        event.target.files ??
        []
      )
    );
  }


  async function handleAnalysis(
    event:
      FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();


    setLoading(true);
    setError("");
    setRequestId(
      undefined
    );
    setResult(null);
    setRunId(null);


    try {
      const data =
        await createCustomRun<
          JsonObject
        >(
          policyName,
          oldText,
          newText,
          files
        );


      const id =
        getRunId(
          data
        );


      setResult(
        data
      );

      setRunId(
        id
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

        return;
      }


      setError(
        caught instanceof Error
          ? caught.message
          : "Analysis failed."
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <ProtectedRoute>
      <main
        className="
          min-h-screen
          bg-[#020d19]
          text-slate-100
        "
      >
        <section
          className="
            mx-auto
            w-full
            max-w-[1500px]
            px-6
            py-12
            lg:px-10
            lg:py-16
          "
        >
          <div
            className="
              mb-10
              max-w-4xl
            "
          >
            <p
              className="
                mb-3
                text-sm
                font-bold
                uppercase
                tracking-[0.2em]
                text-cyan-400
              "
            >
              Production analysis
            </p>

            <h1
              className="
                text-4xl
                font-bold
                tracking-tight
                text-white
                md:text-5xl
              "
            >
              Trace a real policy change.
            </h1>

            <p
              className="
                mt-5
                max-w-3xl
                text-lg
                leading-8
                text-slate-400
              "
            >
              Define the old and new business rule,
              upload the artifacts that may depend on it,
              and let RippleProof discover semantic drift.
            </p>
          </div>


          <form
            onSubmit={
              handleAnalysis
            }
            className="
              grid
              gap-6
              xl:grid-cols-[1.05fr_0.95fr]
            "
          >
            <div
              className="
                rounded-3xl
                border
                border-cyan-400/15
                bg-[#061a2a]
                p-6
                shadow-2xl
                shadow-black/10
                transition
                duration-300
                hover:-translate-y-1
                hover:border-cyan-400/30
                hover:shadow-cyan-500/5
                lg:p-8
              "
            >
              <label
                className="
                  mb-2
                  block
                  text-sm
                  font-semibold
                  text-slate-200
                "
              >
                Policy name
              </label>

              <input
                value={
                  policyName
                }
                onChange={
                  (
                    event
                  ) =>
                    setPolicyName(
                      event.target
                        .value
                    )
                }
                className="
                  mb-7
                  w-full
                  rounded-xl
                  border
                  border-slate-700
                  bg-[#031220]
                  px-4
                  py-3.5
                  text-white
                  outline-none
                  transition
                  focus:border-cyan-400
                  focus:ring-2
                  focus:ring-cyan-400/10
                "
                placeholder="Customer Refund Policy"
              />


              <label
                className="
                  mb-2
                  block
                  text-sm
                  font-semibold
                  text-slate-200
                "
              >
                Previous policy
              </label>

              <textarea
                value={
                  oldText
                }
                onChange={
                  (
                    event
                  ) =>
                    setOldText(
                      event.target
                        .value
                    )
                }
                rows={7}
                className="
                  mb-7
                  w-full
                  resize-y
                  rounded-xl
                  border
                  border-slate-700
                  bg-[#031220]
                  px-4
                  py-3.5
                  leading-7
                  text-white
                  outline-none
                  transition
                  focus:border-cyan-400
                  focus:ring-2
                  focus:ring-cyan-400/10
                "
              />


              <label
                className="
                  mb-2
                  block
                  text-sm
                  font-semibold
                  text-slate-200
                "
              >
                Updated policy
              </label>

              <textarea
                value={
                  newText
                }
                onChange={
                  (
                    event
                  ) =>
                    setNewText(
                      event.target
                        .value
                    )
                }
                rows={7}
                className="
                  w-full
                  resize-y
                  rounded-xl
                  border
                  border-slate-700
                  bg-[#031220]
                  px-4
                  py-3.5
                  leading-7
                  text-white
                  outline-none
                  transition
                  focus:border-cyan-400
                  focus:ring-2
                  focus:ring-cyan-400/10
                "
              />
            </div>


            <div
              className="
                flex
                flex-col
                gap-6
              "
            >
              <div
                className="
                  rounded-3xl
                  border
                  border-cyan-400/15
                  bg-[#061a2a]
                  p-6
                  transition
                  duration-300
                  hover:-translate-y-1
                  hover:border-cyan-400/30
                  lg:p-8
                "
              >
                <h2
                  className="
                    text-xl
                    font-bold
                    text-white
                  "
                >
                  Organizational artifacts
                </h2>

                <p
                  className="
                    mt-2
                    text-sm
                    leading-6
                    text-slate-400
                  "
                >
                  Upload documents, prompts,
                  forms or supported artifacts
                  that may still contain the
                  old policy.
                </p>


                <label
                  className="
                    mt-7
                    flex
                    cursor-pointer
                    flex-col
                    items-center
                    justify-center
                    rounded-2xl
                    border
                    border-dashed
                    border-cyan-400/25
                    bg-cyan-400/[0.03]
                    px-6
                    py-12
                    text-center
                    transition
                    hover:border-cyan-400/50
                    hover:bg-cyan-400/[0.06]
                  "
                >
                  <span
                    className="
                      text-lg
                      font-semibold
                      text-white
                    "
                  >
                    Select artifacts
                  </span>

                  <span
                    className="
                      mt-2
                      text-sm
                      text-slate-400
                    "
                  >
                    Multiple files are supported.
                  </span>

                  <input
                    type="file"
                    multiple
                    onChange={
                      handleFiles
                    }
                    className="hidden"
                  />
                </label>


                <div
                  className="
                    mt-5
                    space-y-2
                  "
                >
                  {files.length ===
                  0 ? (
                    <p
                      className="
                        text-sm
                        text-slate-500
                      "
                    >
                      No artifacts selected.
                    </p>
                  ) : (
                    files.map(
                      (
                        file,
                        index
                      ) => (
                        <div
                          key={
                            `${file.name}-${index}`
                          }
                          className="
                            flex
                            items-center
                            justify-between
                            rounded-xl
                            border
                            border-slate-800
                            bg-[#031220]
                            px-4
                            py-3
                          "
                        >
                          <span
                            className="
                              truncate
                              text-sm
                              text-slate-200
                            "
                          >
                            {file.name}
                          </span>

                          <span
                            className="
                              ml-4
                              whitespace-nowrap
                              text-xs
                              text-slate-500
                            "
                          >
                            {(
                              file.size /
                              1024
                            ).toFixed(
                              1
                            )}{" "}
                            KB
                          </span>
                        </div>
                      )
                    )
                  )}
                </div>
              </div>


              {error && (
                <div
                  className="
                    rounded-2xl
                    border
                    border-rose-400/25
                    bg-rose-500/5
                    px-5
                    py-4
                  "
                >
                  <p
                    className="
                      font-semibold
                      text-rose-300
                    "
                  >
                    Analysis could not be completed
                  </p>

                  <p
                    className="
                      mt-1
                      text-sm
                      leading-6
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


              <button
                type="submit"
                disabled={
                  loading
                }
                className="
                  min-h-14
                  rounded-2xl
                  bg-gradient-to-r
                  from-blue-500
                  to-cyan-400
                  px-6
                  font-bold
                  text-white
                  shadow-lg
                  shadow-cyan-500/10
                  transition
                  duration-200
                  hover:-translate-y-0.5
                  hover:shadow-cyan-500/20
                  disabled:cursor-not-allowed
                  disabled:opacity-60
                  disabled:hover:translate-y-0
                "
              >
                {loading
                  ? "Tracing policy ripple..."
                  : "Start secure analysis"}
              </button>
            </div>
          </form>


          {result && (
            <section
              className="
                mt-10
                rounded-3xl
                border
                border-emerald-400/20
                bg-[#061a2a]
                p-6
                lg:p-8
              "
            >
              <div
                className="
                  flex
                  flex-col
                  gap-5
                  lg:flex-row
                  lg:items-center
                  lg:justify-between
                "
              >
                <div>
                  <p
                    className="
                      text-xs
                      font-bold
                      uppercase
                      tracking-[0.2em]
                      text-emerald-400
                    "
                  >
                    Analysis created
                  </p>

                  <h2
                    className="
                      mt-2
                      text-2xl
                      font-bold
                      text-white
                    "
                  >
                    Ripple trace is ready.
                  </h2>

                  <p
                    className="
                      mt-2
                      text-slate-400
                    "
                  >
                    The run has been persisted
                    and can now move through
                    review and deterministic
                    verification.
                  </p>
                </div>


                <div
                  className="
                    flex
                    flex-wrap
                    gap-3
                  "
                >
                  {runId && (
                    <button
                      type="button"
                      onClick={
                        () =>
                          router.push(
                            `/runs/${encodeURIComponent(
                              runId
                            )}`
                          )
                      }
                      className="
                        rounded-xl
                        bg-cyan-400
                        px-5
                        py-3
                        font-semibold
                        text-slate-950
                        transition
                        hover:-translate-y-0.5
                      "
                    >
                      Open run
                    </button>
                  )}

                  <Link
                    href="/runs"
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
                    "
                  >
                    Run history
                  </Link>
                </div>
              </div>
            </section>
          )}
        </section>
      </main>
    </ProtectedRoute>
  );
}