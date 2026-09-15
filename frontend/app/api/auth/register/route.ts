import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  AUTH_COOKIE,
  BACKEND_API_URL,
  tokenMaxAge,
} from "@/lib/server-auth";


export async function POST(
  request: NextRequest
) {
  try {
    const payload =
      await request.json();

    const backendResponse =
      await fetch(
        `${BACKEND_API_URL}/api/auth/register`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",

            Accept:
              "application/json",
          },

          body: JSON.stringify(
            payload
          ),

          cache: "no-store",
        }
      );

    const data =
      await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json(
        data,
        {
          status:
            backendResponse.status,
        }
      );
    }

    const token =
      data?.access_token;

    if (
      typeof token !== "string" ||
      !token
    ) {
      return NextResponse.json(
        {
          error: {
            code:
              "AUTH_TOKEN_MISSING",

            message:
              "Account created but no access token was returned.",
          },
        },
        {
          status: 502,
        }
      );
    }

    const response =
      NextResponse.json(
        {
          user: data.user,
          team: data.team,
          token_type:
            data.token_type,
        },
        {
          status: 200,
        }
      );

    response.cookies.set(
      AUTH_COOKIE,
      token,
      {
        httpOnly: true,

        secure:
          process.env.NODE_ENV ===
          "production",

        sameSite: "lax",

        path: "/",

        maxAge:
          tokenMaxAge(token),
      }
    );

    return response;
  } catch {
    return NextResponse.json(
      {
        error: {
          code:
            "REGISTRATION_ERROR",

          message:
            "Unable to create your account right now. Please try again.",
        },
      },
      {
        status: 503,
      }
    );
  }
}