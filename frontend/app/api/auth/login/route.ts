import {
  NextRequest,
  NextResponse,
} from "next/server";


const BACKEND_URL =
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";


const AUTH_COOKIE_NAME =
  process.env.AUTH_COOKIE_NAME ||
  "rippleproof_access_token";


export async function POST(
  request: NextRequest
) {

  try {

    const body =
      await request.json();


    const response =
      await fetch(
        `${BACKEND_URL}/api/auth/login`,
        {
          method:"POST",

          headers:{
            "Content-Type":
              "application/json",

            Accept:
              "application/json",
          },

          body:
            JSON.stringify(body),

          cache:
            "no-store",
        }
      );


    const data =
      await response.json();


    if(!response.ok){

      return NextResponse.json(
        data,
        {
          status:
            response.status,
        }
      );

    }


    const token =
      data.access_token;


    if(!token){

      return NextResponse.json(
        {
          detail:
            "Access token missing from backend response"
        },
        {
          status:500,
        }
      );

    }


    const nextResponse =
      NextResponse.json(
        {
          user:
            data.user,
        },
        {
          status:200,
        }
      );


    /*
      Save JWT in HttpOnly cookie
    */

    nextResponse.cookies.set(
      AUTH_COOKIE_NAME,
      token,
      {

        httpOnly:true,

        secure:
          process.env.NODE_ENV ===
          "production",

        sameSite:"lax",

        path:"/",

        maxAge:
          60 * 60 * 24 * 7,
      }
    );


    return nextResponse;


  } catch(error){


    console.error(
      "LOGIN ERROR:",
      error
    );


    return NextResponse.json(
      {
        detail:
          "Login service unavailable"
      },
      {
        status:500,
      }
    );

  }
}