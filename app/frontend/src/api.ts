import { useCallback, useEffect, useState } from "react";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request(path: string, init?: RequestInit) {
  const res = await fetch(path, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? `Request failed (${res.status})`);
  }
  return res.json();
}

export const get = (path: string) => request(path);
export const post = (path: string, body?: unknown) =>
  request(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body ?? {}) });

/** Fetch a path, optionally polling so the two portals stay in step while open side by side. */
export function useData<T = any>(path: string, pollMs?: number) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | Error | null>(null);
  const reload = useCallback(async () => {
    try {
      setData(await get(path));
      setError(null);
    } catch (e: any) {
      setError(e);
    }
  }, [path]);
  useEffect(() => {
    reload();
    if (!pollMs) return;
    const id = setInterval(reload, pollMs);
    return () => clearInterval(id);
  }, [reload, pollMs]);
  return { data, error, reload, setData };
}
