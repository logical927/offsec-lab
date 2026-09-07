import { Card } from "@/components/ui/Card";

import styles from "./layout.module.css";

type PlaceholderPageProps = {
  title: string;
  description: string;
  contextLabel?: string;
  contextValue?: string;
};

export function PlaceholderPage({
  title,
  description,
  contextLabel,
  contextValue,
}: PlaceholderPageProps) {
  return (
    <section aria-labelledby="page-title" className={styles.placeholderPage}>
      <header>
        <p className={styles.eyebrow}>OFFSEC LAB / v0.1</p>
        <h1 id="page-title">{title}</h1>
      </header>
      <Card>
        <p>{description}</p>
        {contextLabel && contextValue ? (
          <p className={styles.context}>
            <span>{contextLabel}</span>
            <code>{contextValue}</code>
          </p>
        ) : null}
      </Card>
    </section>
  );
}
