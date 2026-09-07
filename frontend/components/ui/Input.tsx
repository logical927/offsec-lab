"use client";

import { forwardRef, useId, type InputHTMLAttributes } from "react";

import styles from "./ui.module.css";

type InputProps = Omit<InputHTMLAttributes<HTMLInputElement>, "id"> & {
  id?: string;
  label: string;
  helpText?: string;
  errorText?: string;
};

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { id: providedId, label, helpText, errorText, className = "", ...props },
  ref,
) {
  const generatedId = useId();
  const id = providedId ?? generatedId;
  const helpId = helpText ? `${id}-help` : undefined;
  const errorId = errorText ? `${id}-error` : undefined;
  const describedBy = [helpId, errorId].filter(Boolean).join(" ") || undefined;

  return (
    <div className={styles.field}>
      <label className={styles.label} htmlFor={id}>
        {label}
      </label>
      <input
        ref={ref}
        id={id}
        className={[styles.input, className].filter(Boolean).join(" ")}
        aria-describedby={describedBy}
        aria-invalid={errorText ? true : undefined}
        {...props}
      />
      {helpText ? (
        <span className={styles.helpText} id={helpId}>
          {helpText}
        </span>
      ) : null}
      {errorText ? (
        <span className={styles.errorText} id={errorId}>
          Error: {errorText}
        </span>
      ) : null}
    </div>
  );
});
