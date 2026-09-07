import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { AppShell } from "@/components/layout/AppShell";

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
}));

describe("AppShell", () => {
  it("renders the application landmarks and primary navigation", () => {
    render(
      <AppShell>
        <h1>Dashboard</h1>
      </AppShell>,
    );

    expect(screen.getByRole("banner")).toHaveTextContent("OFFSEC LAB");
    expect(screen.getByRole("main")).toContainElement(screen.getByRole("heading", { name: "Dashboard" }));

    const navigation = screen.getByRole("navigation", { name: "Primary navigation" });
    expect(navigation).toHaveTextContent("Dashboard");
    expect(navigation).toHaveTextContent("Learning Path");
    expect(navigation).toHaveTextContent("Progress");
    expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute("aria-current", "page");
  });
});
