import styles from "./ui.module.css";

type SpinnerProps = {
  label?: string;
  showLabel?: boolean;
};

export function Spinner({ label = "Loading", showLabel = false }: SpinnerProps) {
  return (
    <span className={styles.spinnerWrapper} role="status" aria-live="polite">
      <span className={styles.spinner} aria-hidden="true" />
      <span className={showLabel ? styles.spinnerLabel : "sr-only"}>{label}</span>
    </span>
  );
}
