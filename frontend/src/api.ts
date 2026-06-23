import type { DashboardData } from "./types";

export async function loadDashboardData(): Promise<DashboardData> {
  const response = await fetch("/data/latest.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Unable to load dashboard data: ${response.status}`);
  }
  return (await response.json()) as DashboardData;
}

