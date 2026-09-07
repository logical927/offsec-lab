import { existsSync } from "node:fs";
const frontendRoot = process.cwd();

const requiredRouteFiles = [
  "app/dashboard/page.tsx",
  "app/learning-path/page.tsx",
  "app/missions/[missionId]/page.tsx",
  "app/missions/[missionId]/lab/page.tsx",
  "app/progress/page.tsx",
];

describe("required routes", () => {
  it.each(requiredRouteFiles)("provides %s", (routeFile) => {
    expect(existsSync(`${frontendRoot}/${routeFile}`)).toBe(true);
  });
});
