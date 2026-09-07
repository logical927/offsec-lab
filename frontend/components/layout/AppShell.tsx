import type { ReactNode } from "react";

import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import styles from "./layout.module.css";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className={styles.shell}>
      <a className={styles.skipLink} href="#main-content">
        Skip to main content
      </a>
      <TopBar />
      <div className={styles.body}>
        <Sidebar />
        <main className={styles.main} id="main-content" tabIndex={-1}>
          <div className={styles.content}>{children}</div>
        </main>
      </div>
    </div>
  );
}
