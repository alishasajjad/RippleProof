"use client";

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  usePathname,
  useRouter,
} from "next/navigation";


export type RippleUser = {
  id: string;
  name: string;
  email: string;
  created_at: string;
};


export type RippleTeam = {
  id: string;
  name: string;
  role: string;
};


type AuthContextValue = {
  user: RippleUser | null;

  teams: RippleTeam[];

  activeTeam:
    RippleTeam |
    null;

  loading: boolean;

  refreshSession:
    () => Promise<void>;

  selectTeam:
    (teamId: string) => void;

  logout:
    () => Promise<void>;
};


const AuthContext =
  createContext<
    AuthContextValue |
    undefined
  >(undefined);


const PROTECTED_PREFIXES = [
  "/custom",
  "/runs",
  "/evaluation",
];


function isProtectedPath(
  pathname: string
) {
  return PROTECTED_PREFIXES.some(
    (prefix) =>
      pathname === prefix ||
      pathname.startsWith(
        `${prefix}/`
      )
  );
}


export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const router =
    useRouter();

  const pathname =
    usePathname();

  const [
    user,
    setUser,
  ] = useState<
    RippleUser |
    null
  >(null);

  const [
    teams,
    setTeams,
  ] = useState<
    RippleTeam[]
  >([]);

  const [
    activeTeamId,
    setActiveTeamId,
  ] = useState<
    string |
    null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(true);


  const refreshSession =
    useCallback(
      async () => {
        setLoading(true);

        try {
          const response =
            await fetch(
              "/api/auth/session",
              {
                credentials:
                  "include",

                cache:
                  "no-store",
              }
            );

          if (
            response.status === 401
          ) {
            setUser(null);
            setTeams([]);

            if (
              isProtectedPath(
                window.location.pathname
              )
            ) {
              router.replace(
                `/login?reason=session-expired&next=${encodeURIComponent(
                  window.location.pathname
                )}`
              );
            }

            return;
          }

          if (!response.ok) {
            throw new Error(
              "Session verification failed."
            );
          }

          const data =
            await response.json();

          const nextTeams:
            RippleTeam[] =
              Array.isArray(
                data.teams
              )
                ? data.teams
                : [];

          setUser(
            data.user || null
          );

          setTeams(
            nextTeams
          );

          const stored =
            window.localStorage.getItem(
              "rippleproof_active_team"
            );

          const storedExists =
            nextTeams.some(
              (team) =>
                team.id === stored
            );

          if (
            stored &&
            storedExists
          ) {
            setActiveTeamId(
              stored
            );
          } else if (
            nextTeams.length > 0
          ) {
            const first =
              nextTeams[0].id;

            setActiveTeamId(
              first
            );

            window.localStorage.setItem(
              "rippleproof_active_team",
              first
            );
          } else {
            setActiveTeamId(
              null
            );
          }
        } catch {
          setUser(null);
          setTeams([]);
        } finally {
          setLoading(false);
        }
      },
      [router]
    );


  useEffect(() => {
    refreshSession();
  }, [
    refreshSession,
  ]);


  useEffect(() => {
    if (
      !loading &&
      !user &&
      isProtectedPath(
        pathname
      )
    ) {
      router.replace(
        `/login?next=${encodeURIComponent(
          pathname
        )}`
      );
    }
  }, [
    loading,
    user,
    pathname,
    router,
  ]);


  function selectTeam(
    teamId: string
  ) {
    const exists =
      teams.some(
        (team) =>
          team.id === teamId
      );

    if (!exists) {
      return;
    }

    setActiveTeamId(
      teamId
    );

    window.localStorage.setItem(
      "rippleproof_active_team",
      teamId
    );
  }


  async function logout() {
    try {
      await fetch(
        "/api/auth/logout",
        {
          method: "POST",

          credentials:
            "include",
        }
      );
    } finally {
      window.localStorage.removeItem(
        "rippleproof_active_team"
      );

      setUser(null);
      setTeams([]);
      setActiveTeamId(null);

      router.replace(
        "/login"
      );

      router.refresh();
    }
  }


  const activeTeam =
    useMemo(
      () =>
        teams.find(
          (team) =>
            team.id ===
            activeTeamId
        ) || null,
      [
        teams,
        activeTeamId,
      ]
    );


  const value =
    useMemo(
      () => ({
        user,
        teams,
        activeTeam,
        loading,
        refreshSession,
        selectTeam,
        logout,
      }),
      [
        user,
        teams,
        activeTeam,
        loading,
        refreshSession,
      ]
    );


  if (
    loading &&
    isProtectedPath(
      pathname
    )
  ) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#020d18]">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-cyan-400/20 border-t-cyan-400" />

          <p className="text-sm text-slate-400">
            Verifying secure session…
          </p>
        </div>
      </div>
    );
  }


  return (
    <AuthContext.Provider
      value={value}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth() {
  const context =
    useContext(
      AuthContext
    );

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider."
    );
  }

  return context;
}