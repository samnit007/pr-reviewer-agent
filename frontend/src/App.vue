<template>
  <div class="min-h-full bg-gray-50">

    <!-- Header -->
    <header class="bg-white border-b border-gray-200 px-6 py-4">
      <h1 class="text-lg font-semibold text-gray-900">PR Reviewer Agent</h1>
      <p class="text-xs text-gray-400 mt-0.5">LangGraph · human-in-the-loop · Claude</p>
    </header>

    <main class="max-w-3xl mx-auto px-6 py-8 space-y-6">

      <!-- Input -->
      <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <label class="block text-sm font-medium text-gray-700 mb-2">GitHub PR URL</label>
        <div class="flex gap-3">
          <input
            v-model="prUrl"
            :disabled="status === 'running'"
            type="text"
            placeholder="https://github.com/owner/repo/pull/123"
            class="flex-1 rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
            @keydown.enter="run"
          />
          <button
            @click="run"
            :disabled="!prUrl.trim() || status === 'running'"
            class="bg-indigo-600 text-white rounded-lg px-5 py-2.5 text-sm font-medium hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {{ status === 'running' ? 'Reviewing…' : 'Review' }}
          </button>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
        {{ error }}
      </div>

      <!-- Running state -->
      <div v-if="status === 'running'" class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <p class="text-sm font-medium text-gray-700 mb-3">Running agent…</p>
        <NodePipeline :visited="[]" :running="true" :is-large="false" />
        <div class="mt-4 flex gap-1.5">
          <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay:0ms" />
          <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay:150ms" />
          <span class="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style="animation-delay:300ms" />
        </div>
      </div>

      <!-- Results -->
      <template v-if="result">

        <!-- PR metadata -->
        <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div class="flex items-start justify-between gap-4 mb-4">
            <div>
              <h2 class="font-semibold text-gray-900">{{ result.title }}</h2>
              <p class="text-xs text-gray-400 mt-1">
                {{ result.files_changed.length }} file{{ result.files_changed.length !== 1 ? 's' : '' }} ·
                +{{ result.additions }} -{{ result.deletions }} lines
                <span v-if="result.is_large_pr" class="ml-2 text-amber-600 font-medium">large PR</span>
              </p>
            </div>
            <span class="text-xs text-gray-400 whitespace-nowrap">${{ result.token_cost_usd.toFixed(5) }}</span>
          </div>

          <!-- Node pipeline -->
          <NodePipeline
            :visited="result.nodes_visited"
            :running="false"
            :is-large="result.is_large_pr"
          />

          <!-- Files -->
          <div class="mt-4 flex flex-wrap gap-1.5">
            <span
              v-for="f in result.files_changed"
              :key="f"
              class="bg-gray-100 text-gray-600 text-xs font-mono px-2 py-0.5 rounded"
            >{{ f }}</span>
          </div>
        </div>

        <!-- Draft review -->
        <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h3 class="font-medium text-gray-800 mb-3">Draft Review</h3>
          <div class="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap font-sans text-sm leading-relaxed">{{ currentDraft }}</div>
        </div>

        <!-- Human checkpoint -->
        <HumanCheckpoint
          v-if="status === 'awaiting_approval'"
          :loading="deciding"
          @decide="onDecide"
        />

        <!-- Posted -->
        <div v-if="status === 'posted'" class="bg-green-50 border border-green-200 rounded-xl p-5 text-center">
          <p class="text-green-700 font-semibold text-lg">✓ Review posted to GitHub</p>
          <p class="text-green-600 text-sm mt-1">The review comment is now live on the PR.</p>
        </div>

        <!-- Abandoned -->
        <div v-if="status === 'abandoned'" class="bg-gray-100 rounded-xl p-5 text-center">
          <p class="text-gray-500 font-medium">Review abandoned.</p>
        </div>

      </template>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ReviewStatus, StartResponse } from './types'
import { startReview, decide } from './api/review'
import NodePipeline from './components/NodePipeline.vue'
import HumanCheckpoint from './components/HumanCheckpoint.vue'

const prUrl = ref('')
const status = ref<ReviewStatus>('idle')
const result = ref<StartResponse | null>(null)
const currentDraft = ref('')
const runId = ref('')
const deciding = ref(false)
const error = ref('')

async function run() {
  if (!prUrl.value.trim() || status.value === 'running') return
  error.value = ''
  result.value = null
  status.value = 'running'

  try {
    const data = await startReview(prUrl.value.trim())
    result.value = data
    runId.value = data.run_id
    currentDraft.value = data.draft_review
    status.value = 'awaiting_approval'
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Something went wrong'
    status.value = 'error'
  }
}

async function onDecide(decision: 'approved' | 'rejected' | 'abandoned', feedback?: string) {
  deciding.value = true
  try {
    const data = await decide(runId.value, decision, feedback)
    if (decision === 'rejected') {
      currentDraft.value = data.draft_review
      status.value = 'awaiting_approval'
    } else if (decision === 'approved') {
      status.value = 'posted'
    } else {
      status.value = 'abandoned'
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Decision failed'
  } finally {
    deciding.value = false
  }
}
</script>
