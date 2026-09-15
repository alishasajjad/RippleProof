import type {
  AnalysisResponse,
  VerifyResponse,
} from "@/types";


/*
|--------------------------------------------------------------------------
| API configuration
|--------------------------------------------------------------------------
|
| Browser -> Next.js secure proxy -> FastAPI
|
| JWT browser JavaScript ke paas nahi hota.
| Next.js HttpOnly cookie read karke backend ko
| Authorization: Bearer <token> bhejta hai.
|
*/

export const API_BASE =
  "/api/backend";


/*
|--------------------------------------------------------------------------
| Generic API error
|--------------------------------------------------------------------------
*/

export class ApiError extends Error {
  status: number;
  requestId?: string;
  code?: string;

  constructor(
    message: string,
    status: number,
    requestId?: string,
    code?: string
  ) {
    super(message);

    this.name =
      "ApiError";

    this.status =
      status;

    this.requestId =
      requestId;

    this.code =
      code;
  }
}


/*
|--------------------------------------------------------------------------
| Backend error shapes
|--------------------------------------------------------------------------
*/

type BackendErrorBody = {
  detail?: unknown;

  message?: unknown;

  request_id?: unknown;

  error?: {
    code?: unknown;
    message?: unknown;
    request_id?: unknown;
  };
};


/*
|--------------------------------------------------------------------------
| Utility: extract user-friendly backend error
|--------------------------------------------------------------------------
*/

function extractError(
  data: unknown,
  status: number
): {
  message: string;
  requestId?: string;
  code?: string;
} {
  if (
    typeof data !== "object" ||
    data === null
  ) {
    return {
      message:
        `Request failed with status ${status}.`,
    };
  }

  const payload =
    data as BackendErrorBody;


  let message =
    `Request failed with status ${status}.`;

  let requestId:
    string |
    undefined;

  let code:
    string |
    undefined;


  if (
    payload.error &&
    typeof payload.error ===
      "object"
  ) {
    if (
      typeof payload.error.message ===
      "string"
    ) {
      message =
        payload.error.message;
    }

    if (
      typeof payload.error.request_id ===
      "string"
    ) {
      requestId =
        payload.error.request_id;
    }

    if (
      typeof payload.error.code ===
      "string"
    ) {
      code =
        payload.error.code;
    }
  }


  if (
    typeof payload.detail ===
      "string"
  ) {
    message =
      payload.detail;
  }


  if (
    typeof payload.message ===
      "string"
  ) {
    message =
      payload.message;
  }


  if (
    typeof payload.request_id ===
      "string"
  ) {
    requestId =
      payload.request_id;
  }


  return {
    message,
    requestId,
    code,
  };
}


/*
|--------------------------------------------------------------------------
| Utility: safely read backend response
|--------------------------------------------------------------------------
*/

async function readResponse<T>(
  response: Response
): Promise<T> {
  const contentType =
    response.headers.get(
      "content-type"
    ) ?? "";


  let data: unknown = null;


  try {
    if (
      contentType.includes(
        "application/json"
      )
    ) {
      data =
        await response.json();
    } else {
      const text =
        await response.text();

      data =
        text || null;
    }
  } catch {
    if (!response.ok) {
      throw new ApiError(
        `Server returned an invalid response (${response.status}).`,
        response.status
      );
    }
  }


  if (!response.ok) {
    const parsed =
      extractError(
        data,
        response.status
      );


    const headerRequestId =
      response.headers.get(
        "x-request-id"
      ) ?? undefined;


    /*
     * If backend says JWT/session is invalid,
     * send user back to login automatically.
     */
    if (
      response.status === 401 &&
      typeof window !==
        "undefined"
    ) {
      const pathname =
        window.location.pathname;

      /*
       * Avoid redirect loop while already
       * on login/register pages.
       */
      if (
        pathname !== "/login" &&
        pathname !== "/register"
      ) {
        const target =
          `/login?reason=session-expired&next=${encodeURIComponent(
            pathname
          )}`;

        window.location.assign(
          target
        );
      }
    }


    throw new ApiError(
      parsed.message,
      response.status,
      parsed.requestId ??
        headerRequestId,
      parsed.code
    );
  }


  return data as T;
}


/*
|--------------------------------------------------------------------------
| Main authenticated API request helper
|--------------------------------------------------------------------------
*/

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const normalizedPath =
    path.startsWith("/")
      ? path
      : `/${path}`;


  const headers =
    new Headers(
      init.headers
    );


  if (
    !headers.has("Accept")
  ) {
    headers.set(
      "Accept",
      "application/json"
    );
  }


  /*
   * Important:
   * FormData ke saath Content-Type manually
   * set nahi karna.
   *
   * Browser automatically multipart boundary
   * generate karta hai.
   */
  const isFormData =
    typeof FormData !==
      "undefined" &&
    init.body instanceof
      FormData;


  /*
   * JSON body ho to Content-Type set karo.
   */
  if (
    init.body &&
    !isFormData &&
    typeof init.body ===
      "string" &&
    !headers.has(
      "Content-Type"
    )
  ) {
    headers.set(
      "Content-Type",
      "application/json"
    );
  }


  /*
   * Active team ID Next proxy ke through
   * backend tak bhejna.
   */
  if (
    typeof window !==
      "undefined"
  ) {
    const activeTeam =
      window.localStorage.getItem(
        "rippleproof_active_team"
      );

    if (activeTeam) {
      headers.set(
        "X-Team-ID",
        activeTeam
      );
    }
  }


  let response: Response;


  try {
    response =
      await fetch(
        `${API_BASE}${normalizedPath}`,
        {
          ...init,

          headers,

          credentials:
            "include",

          cache:
            "no-store",
        }
      );
  } catch {
    throw new ApiError(
      "RippleProof service is currently unreachable. Please try again.",
      503
    );
  }


  return readResponse<T>(
    response
  );
}


/*
|--------------------------------------------------------------------------
| Generic GET helper
|--------------------------------------------------------------------------
*/

export async function getJson<T>(
  path: string
): Promise<T> {
  return apiFetch<T>(
    path,
    {
      method: "GET",
    }
  );
}


/*
|--------------------------------------------------------------------------
| Generic POST helper
|--------------------------------------------------------------------------
*/

export async function postJson<T>(
  path: string,
  body?: unknown
): Promise<T> {
  return apiFetch<T>(
    path,
    {
      method: "POST",

      body:
        body === undefined
          ? undefined
          : JSON.stringify(
              body
            ),
    }
  );
}


/*
|--------------------------------------------------------------------------
| Homepage deterministic demo
|--------------------------------------------------------------------------
|
| Hidden backend endpoint.
| Existing polished homepage ko break nahi karta.
|
*/

export async function analyzeDemo():
Promise<AnalysisResponse> {
  return postJson<
    AnalysisResponse
  >(
    "/api/demo/analyze"
  );
}


/*
|--------------------------------------------------------------------------
| Persistent flagship demo
|--------------------------------------------------------------------------
*/

export async function createPersistentDemo():
Promise<AnalysisResponse> {
  return postJson<
    AnalysisResponse
  >(
    "/api/runs/demo"
  );
}


/*
|--------------------------------------------------------------------------
| Approve run
|--------------------------------------------------------------------------
*/

export async function approveRun(
  runId: string
): Promise<
  Record<string, unknown>
> {
  if (!runId) {
    throw new Error(
      "Run ID is required for patch approval."
    );
  }


  return postJson<
    Record<string, unknown>
  >(
    `/api/runs/${encodeURIComponent(
      runId
    )}/approve`
  );
}


/*
|--------------------------------------------------------------------------
| Verify
|--------------------------------------------------------------------------
|
| verifyDemo()
|   -> homepage deterministic demo
|
| verifyDemo(runId)
|   -> persisted production run
|
*/

export async function verifyDemo(
  runId?: string
): Promise<VerifyResponse> {
  const endpoint =
    runId
      ? `/api/runs/${encodeURIComponent(
          runId
        )}/verify`
      : "/api/demo/verify";


  return postJson<
    VerifyResponse
  >(
    endpoint
  );
}


/*
|--------------------------------------------------------------------------
| Runs
|--------------------------------------------------------------------------
*/

export async function getRuns<T =
  Record<string, unknown>[]
>(): Promise<T> {
  return getJson<T>(
    "/api/runs"
  );
}


export async function getRun<T =
  Record<string, unknown>
>(
  runId: string
): Promise<T> {
  if (!runId) {
    throw new Error(
      "Run ID is required."
    );
  }


  return getJson<T>(
    `/api/runs/${encodeURIComponent(
      runId
    )}`
  );
}


/*
|--------------------------------------------------------------------------
| Evaluation
|--------------------------------------------------------------------------
*/

export async function getEvaluationSummary<T =
  Record<string, unknown>
>(): Promise<T> {
  return getJson<T>(
    "/api/evaluation/summary"
  );
}


export async function getEvaluationBenchmark<T =
  Record<string, unknown>
>(): Promise<T> {
  return getJson<T>(
    "/api/evaluation/benchmark"
  );
}


/*
|--------------------------------------------------------------------------
| Dashboard
|--------------------------------------------------------------------------
*/

export async function getDashboardSummary<T =
  Record<string, unknown>
>(): Promise<T> {
  return getJson<T>(
    "/api/dashboard/summary"
  );
}


/*
|--------------------------------------------------------------------------
| Policy contract
|--------------------------------------------------------------------------
*/

export async function createPolicyContract<T =
  Record<string, unknown>
>(
  payload: {
    policy_name: string;
    old_text: string;
    new_text: string;
  }
): Promise<T> {
  return postJson<T>(
    "/api/policy-contract",
    payload
  );
}


/*
|--------------------------------------------------------------------------
| Custom production analysis
|--------------------------------------------------------------------------
*/

export async function createCustomRun<T =
  Record<string, unknown>
>(
  policyName: string,
  oldText: string,
  newText: string,
  files: File[]
): Promise<T> {
  if (!policyName.trim()) {
    throw new Error(
      "Policy name is required."
    );
  }


  if (!oldText.trim()) {
    throw new Error(
      "Previous policy text is required."
    );
  }


  if (!newText.trim()) {
    throw new Error(
      "Updated policy text is required."
    );
  }


  if (!files.length) {
    throw new Error(
      "Upload at least one artifact."
    );
  }


  const formData =
    new FormData();


  formData.append(
    "policy_name",
    policyName.trim()
  );


  formData.append(
    "old_text",
    oldText.trim()
  );


  formData.append(
    "new_text",
    newText.trim()
  );


  files.forEach(
    (file) => {
      formData.append(
        "files",
        file
      );
    }
  );


  /*
   * Do NOT set Content-Type here.
   */
  return apiFetch<T>(
    "/api/runs/custom",
    {
      method: "POST",

      body:
        formData,
    }
  );
}


/*
|--------------------------------------------------------------------------
| System endpoints
|--------------------------------------------------------------------------
*/

export async function getHealth<T =
  Record<string, unknown>
>(): Promise<T> {
  return getJson<T>(
    "/health"
  );
}


export async function getSystemStatus<T =
  Record<string, unknown>
>(): Promise<T> {
  return getJson<T>(
    "/api/system/status"
  );
}


export async function getReadiness<T =
  Record<string, unknown>
>(): Promise<T> {
  return getJson<T>(
    "/api/system/readiness"
  );
}


/*
|--------------------------------------------------------------------------
| Identity / Teams
|--------------------------------------------------------------------------
*/

export async function getCurrentUser<T =
  Record<string, unknown>
>(): Promise<T> {
  return getJson<T>(
    "/api/auth/me"
  );
}


export async function getTeams<T =
  Record<string, unknown>[]
>(): Promise<T> {
  return getJson<T>(
    "/api/teams"
  );
}


export async function getTeamMembers<T =
  Record<string, unknown>[]
>(
  teamId: string
): Promise<T> {
  if (!teamId) {
    throw new Error(
      "Team ID is required."
    );
  }


  return getJson<T>(
    `/api/teams/${encodeURIComponent(
      teamId
    )}/members`
  );
}