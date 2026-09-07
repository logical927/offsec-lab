import styles from "./layout.module.css";

export function TopBar() {
  return (
    <header className={styles.topBar}>
      <span className={styles.brand}>OFFSEC LAB</span>
      <dl className={styles.playerStats} aria-label="Player status">
        <div>
          <dt>XP</dt>
          <dd>—</dd>
        </div>
        <div>
          <dt>LEVEL</dt>
          <dd>—</dd>
        </div>
      </dl>
    </header>
  );
}
