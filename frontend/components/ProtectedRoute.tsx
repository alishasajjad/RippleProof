"use client";

import type {
  ReactNode,
} from "react";

import {
  useEffect,
  useState,
} from "react";

import {
  usePathname,
  useRouter,
} from "next/navigation";

import {
  ApiError,
  getCurrentUser,
} from "@/lib/api";


type ProtectedRouteProps = {
  children: ReactNode;
};


export default function ProtectedRoute({
  children,
}: ProtectedRouteProps) {
  const router =
    useRouter();

  const pathname =
    usePathname();

  const [
    checking,
    setChecking,
  ] =
    useState(true);


  useEffect(() => {
    let active = true;


    async function checkSession() {
      try {
        await getCurrentUser();

        if (active) {
          setChecking(false);
        }

      } catch (error) {
        if (!active) {
          return;
        }


        if (
          error instanceof ApiError &&
          error.status === 401
        ) {
          const next =
            encodeURIComponent(
              pathname || "/"
            );

          router.replace(
            `/login?next=${next}`
          );

          return;
        }


        /*
         * api.ts itself also handles
         * expired/invalid sessions.
         */

        setChecking(false);
      }
    }


    void checkSession();


    return () => {
      active = false;
    };
  }, [
    pathname,
    router,
  ]);


  if (checking) {
    return (
      <div
        className="
          min-h-[65vh]
          flex
          items-center
          justify-center
          bg-[#020d19]
          px-6
        "
      >
        <div
          className="
            flex
            flex-col
            items-center
            gap-4
          "
        >
          <div
            className="
              h-10
              w-10
              rounded-full
              border-2
              border-cyan-400/20
              border-t-cyan-400
              animate-spin
            "
          />

          <p
            className="
              text-sm
              text-slate-400
            "
          >
            Verifying secure session...
          </p>
        </div>
      </div>
    );
  }


  return (
    <>
      {children}
    </>
  );
}