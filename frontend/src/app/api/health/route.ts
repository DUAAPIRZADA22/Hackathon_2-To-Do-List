import { NextResponse } from 'next/server';

/**
 * Health check endpoint for Kubernetes probes
 *
 * This is a lightweight endpoint used by Kubernetes:
 * - Liveness probes: Is the container running?
 * - Readiness probes: Is the container ready to serve traffic?
 *
 * Returns a simple JSON response indicating the service is healthy.
 */
export async function GET() {
  return NextResponse.json(
    {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'ActionMindAI Frontend',
      version: '1.0.0'
    },
    { status: 200 }
  );
}
