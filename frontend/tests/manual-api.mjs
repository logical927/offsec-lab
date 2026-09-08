// Isolated in-memory browser fixture. Never connects to PostgreSQL or Docker.
// Run: node tests/manual-api.mjs
import { createServer } from "node:http";
const mission = { id: 1, slug: "browser-fixture", title: "Browser verification mission", description: "Practice observing the provided training target. This is test-only fixture content.", sort_order: 1 };
const challenges = [
  { id: 10, slug: "first", title: "First observation", description: "Enter fixture-pass to exercise the correct-answer UI.", sort_order: 1 },
  { id: 20, slug: "second", title: "Second observation", description: "Enter fixture-pass to finish this test-only mission.", sort_order: 2 },
];
let completed = 0;
let lab = "STOPPED";
const server = createServer(async (request, response) => {
  const path = request.url;
  let body = "";
  for await (const chunk of request) body += chunk;
  let status = 200;
  let data;
  if (path === "/api/v1/missions") data = [mission];
  else if (path === "/api/v1/missions/1") data = { ...mission, challenges };
  else if (path === "/api/v1/progress") data = { missions: [{ mission_id: 1, status: completed === 2 ? "COMPLETED" : completed ? "IN_PROGRESS" : "NOT_STARTED", challenges: challenges.map((c, index) => ({ challenge_id: c.id, status: index < completed ? "COMPLETED" : index === completed ? "AVAILABLE" : "LOCKED" })) }] };
  else if (path === "/api/v1/labs/1/status") data = { mission_id: 1, status: lab, target: lab === "RUNNING" ? { hostname: "fixture-target", ip: "192.0.2.10" } : null };
  else if (/^\/api\/v1\/labs\/1\/(start|stop|reset)$/.test(path) && request.method === "POST") {
    await new Promise(resolve => setTimeout(resolve, 350));
    lab = path.endsWith("/stop") ? "STOPPED" : "RUNNING";
    data = { mission_id: 1, status: lab.toLowerCase() };
  } else if (/^\/api\/v1\/challenges\/(10|20)\/answers$/.test(path) && request.method === "POST") {
    await new Promise(resolve => setTimeout(resolve, 350));
    const index = path.includes("/10/") ? 0 : 1;
    const correct = JSON.parse(body).answer === "fixture-pass";
    if (index > completed) { status = 409; data = { error: { code: "CHALLENGE_LOCKED" } }; }
    else {
      if (correct && index === completed) completed++;
      data = { correct, status: correct ? "COMPLETED" : "AVAILABLE", next_challenge_id: completed < 2 ? challenges[completed].id : null, mission_status: completed === 2 ? "COMPLETED" : "IN_PROGRESS" };
    }
  } else { status = 404; data = { error: { code: "NOT_FOUND" } }; }
  response.writeHead(status, { "Content-Type": "application/json" });
  response.end(JSON.stringify(data));
});
server.listen(8001, "127.0.0.1", () => console.log("Isolated browser fixture API: http://127.0.0.1:8001"));
