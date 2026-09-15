import {
  NextRequest,
  NextResponse,
} from "next/server";


const COOKIE_NAMES = [
  "rippleproof_access_token",
  "access_token",
  "session",
];


export function middleware(
  request: NextRequest
) {

  const token =
    COOKIE_NAMES.some(
      (name) =>
        request.cookies.get(name)?.value
    );


  if (!token) {

    const loginUrl =
      new URL(
        "/login",
        request.url
      );


    loginUrl.searchParams.set(
      "next",
      request.nextUrl.pathname
    );


    return NextResponse.redirect(
      loginUrl
    );
  }


  return NextResponse.next();
}


export const config = {
  matcher: [
    "/custom/:path*",
    "/runs/:path*",
    "/evaluation/:path*",
  ],
};