"use client";
import { useEffect, useState } from "react";
export function useResource<T>(loader: (signal: AbortSignal) => Promise<T>) {
  const [state, setState] = useState<{ data?: T; error?: string }>({});
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    loader(controller.signal).then(
      data => { if (!controller.signal.aborted) setState({ data }); },
      () => { if (!controller.signal.aborted) setState({ error: "Unable to load data. Check the local backend and try again." }); },
    );
    return () => controller.abort();
  }, [loader, attempt]);
  return { ...state, retry: () => { setState({}); setAttempt(value => value + 1); } };
}
