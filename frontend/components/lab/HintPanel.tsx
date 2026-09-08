"use client";
import { useId, useState } from "react";
import { Button, Card } from "@/components/ui";
import styles from "@/components/mission/mission.module.css";
export type Hint = { id: string; title?: string; content: string };
export function HintPanel({ hints }: { hints: readonly Hint[] }) {
  const [opened, setOpened] = useState<string[]>([]);
  const prefix = useId();
  // Only the contiguous prefix stays unlocked if supplied content changes.
  let count = 0;
  while (count < hints.length && opened[count] === hints[count].id) count++;
  return <Card className={styles.stack}><h2>Hints</h2>
    {!hints.length ? <p>Hints are not available for this challenge yet.</p> : hints.map((hint, index) => {
      const state = index < count ? "OPENED" : index === count ? "AVAILABLE" : "LOCKED";
      const id = `${prefix}-${index}`;
      return <section key={hint.id}>
        <Button variant="secondary" disabled={state === "LOCKED"} aria-expanded={state === "OPENED"} aria-controls={state === "OPENED" ? id : undefined} onClick={() => { if (index === count) setOpened(hints.slice(0, count + 1).map(h => h.id)); }}>
          Hint {index + 1}{hint.title ? ` · ${hint.title}` : ""} — {state}
        </Button>
        {state === "OPENED" && <p id={id} className={styles.text}>{hint.content}</p>}
      </section>;
    })}
  </Card>;
}
