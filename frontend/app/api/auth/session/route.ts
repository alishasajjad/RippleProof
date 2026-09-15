import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  AUTH_COOKIE,
  BACKEND_API_URL,
} from "@/lib/server-auth";


export async function GET(
  request: NextRequest
) {
  const token =
    request.cookies.get(
      AUTH_COOKIE
    )?.value;

  if (!token) {
    return NextResponse.json(
      {
        error: {
          code:
            "NOT_AUTHENTICATED",

          message:
            "Authentication required.",
        },
      },
      {
        status: 401,
      }
    );
  }

  try {
    const backendResponse =
      await fetch(
        `${BACKEND_API_URL}/api/auth/me`,
        {
          headers: {
            Authorization:
              `Bearer ${token}`,

            Accept:
              "application/json",
          },

          cache: "no-store",
        }
      );

    const data =
      await backendResponse.json();

    const response =
      NextResponse.json(
        data,
        {
          status:
            backendResponse.status,
        }
      );

    if (
      backendResponse.status === 401
    ) {
      response.cookies.set(
        AUTH_COOKIE,
        "",
        {
          path: "/",
          maxAge: 0,
        }
      );
    }

    return response;
  } catch {
    return NextResponse.json(
      {
        error: {
          code:
            "SESSION_SERVICE_ERROR",

          message:
            "Unable to verify your session.",
        },
      },
      {
        status: 503,
      }
    );
  }
}