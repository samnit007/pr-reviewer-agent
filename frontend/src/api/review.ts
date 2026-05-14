import type { StartResponse, DecideResponse } from '../types'

const BASE = import.meta.env.VITE_API_BASE ?? '/api'

export async function startReview(prUrl: string): Promise<StartResponse> {
  const res = await fetch(`${BASE}/review/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pr_url: prUrl }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail ?? 'Request failed')
  }
  return res.json()
}

export async function decide(
  runId: string,
  decision: 'approved' | 'rejected' | 'abandoned',
  feedback?: string,
): Promise<DecideResponse> {
  const res = await fetch(`${BASE}/review/decide`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ run_id: runId, decision, feedback }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail ?? 'Request failed')
  }
  return res.json()
}
