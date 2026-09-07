import styles from "./ui.module.css";

type ProgressBarProps = {
  value: number;
  label: string;
  max?: number;
};

export function ProgressBar({ value, label, max = 100 }: ProgressBarProps) {
  const safeMax = max > 0 ? max : 100;
  const safeValue = Math.min(Math.max(value, 0), safeMax);
  const percentage = Math.round((safeValue / safeMax) * 100);

  return (
    <div className={styles.progressGroup}>
      <div className={styles.progressLabel}>
        <span>{label}</span>
        <span>{percentage}%</span>
      </div>
      <div
        className={styles.progressTrack}
        role="progressbar"
        aria-label={label}
        aria-valuemin={0}
        aria-valuemax={safeMax}
        aria-valuenow={safeValue}
        aria-valuetext={`${percentage}%`}
      >
        <span className={styles.progressValue} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}
