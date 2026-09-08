import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";

function docker(...args: string[]) {
  return execFileSync("docker", args, { encoding: "utf8", timeout: 120_000 });
}
// Fixed Mission 01 observations documented in challenges/m01-recon/README.md.
// Never read accepted_answers or another private database field.
const observations = ["reachable", "22,80", "ssh,http", "OpenSSH 9.2p1", "Northbridge Systems Status Portal"];

test("Mission selection, reconnaissance, five answers, completion, reset and stop", async ({ page, request }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  const api = "http://127.0.0.1:8001/api/v1";
  try {
    expect((await request.post(`${api}/labs/1/stop`)).ok()).toBeTruthy();
    await page.goto("/learning-path");
    await expect(page.getByRole("heading", { name: "Reconnaissance Fundamentals" })).toBeVisible();
    await page.getByRole("link", { name: "View Mission", exact: true }).click();
    await expect(page).toHaveURL(/\/missions\/1$/);
    await expect(page.getByRole("heading", { name: "Reconnaissance Fundamentals" })).toBeVisible();
    await page.getByRole("link", { name: /Lab/ }).click();
    await expect(page).toHaveURL(/\/missions\/1\/lab$/);
    await expect(page.getByText("0 of 5 challenges completed")).toBeVisible();
    await page.getByRole("button", { name: "Start Lab", exact: true }).click();
    await expect(page.getByText("RUNNING", { exact: true })).toBeVisible({ timeout: 150_000 });
    expect(docker("exec", "offsec-m01-attacker", "getent", "hosts", "target-m01")).toContain("target-m01");
    expect(docker("exec", "offsec-m01-attacker", "ping", "-c", "1", "-W", "3", "target-m01")).toContain("1 received");
    const scan = docker("exec", "offsec-m01-attacker", "nmap", "-sT", "-sV", "-p", "22,80", "target-m01");
    expect(scan).toMatch(/22\/tcp\s+open\s+ssh/);
    expect(scan).toMatch(/80\/tcp\s+open\s+http/);
    expect(scan).toContain(observations[3]);
    expect(docker("exec", "offsec-m01-attacker", "curl", "-fsS", "--max-time", "10", "http://target-m01")).toContain(`<title>${observations[4]}</title>`);
    for (let level = 1; level <= 3; level++) {
      await page.getByRole("button", { name: `Hint ${level} — AVAILABLE`, exact: true }).click();
      await expect(page.getByRole("button", { name: `Hint ${level} — OPENED`, exact: true })).toHaveAttribute("aria-expanded", "true");
    }
    await page.getByRole("textbox", { name: "Answer", exact: true }).fill("incorrect observation");
    await page.getByRole("button", { name: "Submit Answer" }).click();
    await expect(page.getByText(/INCORRECT/)).toBeVisible();
    await expect(page.getByText("0 of 5 challenges completed")).toBeVisible();
    for (const [index, answer] of observations.entries()) {
      await page.getByRole("textbox", { name: "Answer", exact: true }).fill(answer);
      await page.getByRole("button", { name: "Submit Answer" }).click();
      await expect(page.getByText(`${index + 1} of 5 challenges completed`)).toBeVisible();
      if (index < 4) await page.getByRole("button", { name: "Next Challenge" }).click();
    }
    await expect(page.getByRole("dialog", { name: "Mission Complete", exact: true })).toBeVisible();
    await page.getByRole("button", { name: "Return to Workspace" }).click();
    const beforeProgress = await (await request.get(`${api}/progress`)).json();
    const beforeId = docker("inspect", "--format", "{{.Id}}", "target-m01").trim();
    const marker = "/tmp/offsec-phase9-e2e-marker";
    docker("exec", "target-m01", "touch", marker);
    docker("exec", "target-m01", "test", "-f", marker);
    await page.getByRole("button", { name: "Reset Lab", exact: true }).click();
    const resetResponse = page.waitForResponse(response => response.url().endsWith("/labs/1/reset") && response.request().method() === "POST");
    await page.getByRole("button", { name: "Confirm Reset" }).click();
    expect((await resetResponse).ok()).toBeTruthy();
    await expect(page.getByText("RUNNING", { exact: true })).toBeVisible({ timeout: 150_000 });
    docker("exec", "target-m01", "test", "!", "-e", marker);
    expect(docker("inspect", "--format", "{{.Id}}", "target-m01").trim()).not.toBe(beforeId);
    expect(await (await request.get(`${api}/progress`)).json()).toEqual(beforeProgress);
    await page.getByRole("button", { name: "Stop Lab", exact: true }).click();
    await expect(page.getByText("STOPPED", { exact: true })).toBeVisible();
    expect((await (await request.get(`${api}/labs/1/status`)).json()).target).toBeNull();
    await page.reload();
    await expect(page.getByRole("dialog", { name: "Mission Complete", exact: true })).toBeVisible();
    expect(errors).toEqual([]);
  } finally {
    const stopped = await request.post(`${api}/labs/1/stop`, { timeout: 150_000 });
    expect(stopped.ok()).toBeTruthy();
  }
});
