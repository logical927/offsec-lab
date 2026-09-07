import type { ButtonHTMLAttributes } from "react";

import styles from "./ui.module.css";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "destructive";
};

export function Button({ className = "", type = "button", variant = "primary", ...props }: ButtonProps) {
  const classes = [styles.button, styles[variant], className].filter(Boolean).join(" ");

  return <button className={classes} type={type} {...props} />;
}
