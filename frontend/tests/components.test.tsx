import { render, screen } from "@testing-library/react";

import { Badge, Button, Card, Input, ProgressBar, Spinner } from "@/components/ui";

describe("shared UI components", () => {
  it("uses semantic controls and accessible state text", () => {
    render(
      <Card>
        <Button disabled>Start lab</Button>
        <Badge tone="success">RUNNING</Badge>
        <Input label="Target" helpText="Enter a target identifier." />
        <ProgressBar label="Course progress" value={25} />
        <Spinner label="Starting lab" />
      </Card>,
    );

    expect(screen.getByRole("button", { name: "Start lab" })).toBeDisabled();
    expect(screen.getByText("RUNNING")).toBeVisible();
    expect(screen.getByRole("textbox", { name: "Target" })).toHaveAccessibleDescription(
      "Enter a target identifier.",
    );
    expect(screen.getByRole("progressbar", { name: "Course progress" })).toHaveAttribute(
      "aria-valuenow",
      "25",
    );
    expect(screen.getByRole("status")).toHaveTextContent("Starting lab");
  });
});
