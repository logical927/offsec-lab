import { execFileSync, spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
const root = fileURLToPath(new URL("../../", import.meta.url));
const frontend = fileURLToPath(new URL("../", import.meta.url));
const name = "offsec-phase9-e2e-backend";
const docker = (...args) => execFileSync("docker", args, { cwd: root, encoding: "utf8", timeout: 180_000 });
let started = false;
try {
  docker("compose", "run", "-d", "--no-deps", "--name", name,
    "-p", "127.0.0.1:8001:8000", "-w", "/workspace/backend",
    "-e", "PYTHONPATH=/workspace/backend", "backend", "python", "/workspace/scripts/e2e_backend.py");
  started = true;
  let ready = false;
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    try { ready = (await fetch("http://127.0.0.1:8001/ready", { signal: AbortSignal.timeout(2000) })).ok; } catch {}
    if (ready) break;
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  if (!ready) throw new Error("Isolated E2E backend did not become ready");
  const child = spawn(process.execPath, ["node_modules/@playwright/test/cli.js", "test"], { cwd: frontend, stdio: "inherit" });
  process.exitCode = await new Promise((resolve, reject) => { child.on("error", reject); child.on("exit", code => resolve(code ?? 1)); });
} finally {
  if (started) {
    try {
      docker("stop", "--time", "30", name);
      const logs = docker("logs", name);
      if (!logs.includes("E2E schema removed")) throw new Error("E2E schema cleanup was not confirmed");
    } finally {
      docker("rm", name);
      docker("compose", "-f", "challenges/m01-recon/compose.lab.yml", "-p", "offsec-m01", "down", "--volumes");
      if (docker("ps", "-aq", "--filter", "label=com.docker.compose.project=offsec-m01").trim()) throw new Error("Lab containers remain");
      if (docker("network", "ls", "-q", "--filter", "name=^offsec-m01-net$").trim()) throw new Error("Lab network remains");
    }
  }
}
