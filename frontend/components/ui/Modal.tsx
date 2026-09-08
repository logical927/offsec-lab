"use client";
import { useEffect, useId, useRef, type ReactNode } from "react";
import styles from "./modal.module.css";
export function Modal({ title, children, onClose }: { title: string; children: ReactNode; onClose: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const dialog = ref.current;
    dialog?.showModal();
    dialog?.querySelector<HTMLElement>("button, a[href], input")?.focus();
    return () => {
      dialog?.close();
      const target = previous?.isConnected && previous !== document.body && !previous.matches(":disabled")
        ? previous : document.getElementById("main-content");
      target?.focus();
    };
  }, []);
  return <dialog ref={ref} className={styles.modal} aria-labelledby={titleId} onCancel={event => { event.preventDefault(); onClose(); }}>
    <h2 id={titleId}>{title}</h2>{children}
  </dialog>;
}
