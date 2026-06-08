import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const body = await request.json();
  const records = Array.isArray(body.records) ? body.records : [];

  await new Promise((resolve) => setTimeout(resolve, 700));

  return NextResponse.json({
    ok: true,
    synced: records.length,
    target: "local-fastapi-placeholder"
  });
}
