// The reader's profile: one password (the VOTE_KEY secret), entered once per
// browser or app and remembered for a year in an HttpOnly cookie, so votes
// (vote.js) don't ask for it again. POST {key} logs in, DELETE logs out, GET
// says whether this browser is logged in. The cookie holds an HMAC of the
// password, not the password; changing VOTE_KEY logs every device out.
const COOKIE = "mb_profile";
const YEAR = 31536000;

async function token(env) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey("raw", enc.encode(env.VOTE_KEY), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode("morning-brief-profile"));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// The x-key header is for the pipeline's morning sync (core/interest.py); people use the cookie.
export async function authorized(request, env) {
  if (!env.VOTE_KEY) return false;
  if (request.headers.get("x-key") === env.VOTE_KEY) return true;
  const m = (request.headers.get("cookie") || "").match(/(?:^|;\s*)mb_profile=([0-9a-f]{64})/);
  return !!m && m[1] === (await token(env));
}

const cookie = (value, maxAge) => `${COOKIE}=${value}; Path=/; Max-Age=${maxAge}; HttpOnly; Secure; SameSite=Lax`;

export async function onRequest({ request, env }) {
  if (request.method === "POST") {
    const { key } = await request.json().catch(() => ({}));
    if (!env.VOTE_KEY || key !== env.VOTE_KEY) return new Response("unauthorized", { status: 401 });
    return new Response("ok", { headers: { "set-cookie": cookie(await token(env), YEAR) } });
  }
  if (request.method === "DELETE") return new Response("ok", { headers: { "set-cookie": cookie("", 0) } });
  return Response.json({ logged: await authorized(request, env) }, { headers: { "cache-control": "no-store" } });
}
