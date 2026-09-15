export const AUTH_COOKIE = "rippleproof_access_token";

export const BACKEND_API_URL = (
  process.env.BACKEND_API_URL ||
  "http://127.0.0.1:8000"
).replace(/\/+$/, "");


export function tokenMaxAge(
  token: string,
  fallbackSeconds = 60 * 60 * 12
): number {
  try {
    const parts = token.split(".");

    if (parts.length !== 3) {
      return fallbackSeconds;
    }

    const payload = JSON.parse(
      Buffer.from(parts[1], "base64url").toString("utf8")
    );

    if (typeof payload.exp !== "number") {
      return fallbackSeconds;
    }

    const now = Math.floor(Date.now() / 1000);

    return Math.max(
      60,
      payload.exp - now
    );
  } catch {
    return fallbackSeconds;
  }
}