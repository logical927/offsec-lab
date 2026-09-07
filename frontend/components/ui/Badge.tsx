import type { HTMLAttributes } from "react";

import styles from "./ui.module.css";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: "neutral" | "success" | "warning" | "error" | "info";
};

export function Badge({ children, className = "", tone = "neutral", ...props }: BadgeProps) {
  const classes = [styles.badge, styles[`badge-${tone}`], className].filter(Boolean).join(" ");

  return (
    <span className={classes} {...props}>
      <span className={styles.badgeDot} aria-hidden="true" />
      {children}
    </span>
  );
}
