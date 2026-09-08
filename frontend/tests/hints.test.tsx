import { fireEvent, render, screen } from "@testing-library/react";
import { HintPanel } from "@/components/lab/HintPanel";
it("reveals an arbitrary number of fixture hints sequentially", () => {
  const hints = Array.from({ length: 5 }, (_, index) => ({ id: String(index), content: `Fixture guidance ${index + 1}` }));
  render(<HintPanel hints={hints} />);
  expect(screen.queryByText("Fixture guidance 1")).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Hint 2 — LOCKED" })).toBeDisabled();
  for (let index = 1; index <= 5; index++) {
    const button = screen.getByRole("button", { name: `Hint ${index} — AVAILABLE` });
    button.focus();
    expect(button).toHaveFocus();
    expect(button.tagName).toBe("BUTTON");
    fireEvent.click(button);
    expect(button).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByText(`Fixture guidance ${index}`)).toBeVisible();
  }
});
it("handles missing data and resets unlocks for different hint identities", () => {
  const { rerender } = render(<HintPanel hints={[]} />);
  expect(screen.getByText(/not available/)).toBeVisible();
  rerender(<HintPanel hints={[{ id: "a", content: "First fixture" }]} />);
  fireEvent.click(screen.getByRole("button"));
  rerender(<HintPanel hints={[{ id: "b", content: "Second fixture" }]} />);
  expect(screen.queryByText("Second fixture")).not.toBeInTheDocument();
  expect(screen.getByRole("button")).toHaveTextContent("AVAILABLE");
});
