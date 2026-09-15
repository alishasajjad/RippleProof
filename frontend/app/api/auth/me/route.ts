import {
  NextRequest,
  NextResponse,
} from "next/server";


const BACKEND_URL =
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";


const COOKIE_NAME =
  process.env.AUTH_COOKIE_NAME ||
  "rippleproof_access_token";


export async function GET(
  request: NextRequest
) {

  const token =
    request.cookies.get(
      COOKIE_NAME
    )?.value;


  if (!token) {

    return NextResponse.json(
      {
        detail:
          "Authentication required"
      },
      {
        status:401
      }
    );

  }


  const backendResponse =
    await fetch(
      `${BACKEND_URL}/api/auth/me`,
      {
        method:"GET",

        headers:{
          Authorization:
            `Bearer ${token}`,

          Accept:
            "application/json",
        },

        cache:
          "no-store",
      }
    );


  const data =
    await backendResponse.json();


  return NextResponse.json(
    data,
    {
      status:
        backendResponse.status,
    }
  );
}