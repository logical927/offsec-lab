"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import styles from "./layout.module.css";

const navigation = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/learning-path", label: "Learning Path" },
  { href: "/progress", label: "Progress" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className={styles.sidebar}>
      <nav aria-label="Primary navigation">
        <ul className={styles.navList}>
          {navigation.map(({ href, label }) => {
            const isCurrent = pathname === href;

            return (
              <li key={href}>
                <Link className={styles.navLink} href={href} aria-current={isCurrent ? "page" : undefined}>
                  {label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}
