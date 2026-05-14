export type ReviewStatus = 'idle' | 'running' | 'awaiting_approval' | 'posted' | 'revised' | 'abandoned' | 'error'

export interface StartResponse {
  run_id: string
  status: string
  title: string
  files_changed: string[]
  additions: number
  deletions: number
  is_large_pr: boolean
  draft_review: string
  comment_count: number
  token_cost_usd: number
  nodes_visited: string[]
}

export interface DecideResponse {
  run_id: string
  decision: string
  status: string
  draft_review: string
  token_cost_usd: number
  error: string | null
}
