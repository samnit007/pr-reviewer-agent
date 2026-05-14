<template>
  <div class="border-2 border-amber-300 bg-amber-50 rounded-xl p-5">
    <div class="flex items-center gap-2 mb-4">
      <span class="text-lg">⏸</span>
      <h3 class="font-semibold text-amber-800">Human Approval Required</h3>
    </div>

    <p class="text-sm text-amber-700 mb-4">
      Review the draft below. Approve to post it to GitHub, reject to revise, or abandon to discard.
    </p>

    <!-- Reject feedback -->
    <div v-if="showFeedback" class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-1">Feedback for revision</label>
      <textarea
        v-model="feedback"
        rows="3"
        placeholder="What should be changed? e.g. 'Too long, be more concise' or 'Focus only on logic issues'"
        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
    </div>

    <div class="flex gap-3">
      <button
        v-if="!showFeedback"
        @click="emit('decide', 'approved')"
        :disabled="loading"
        class="flex-1 bg-green-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-green-700 disabled:opacity-40 transition-colors"
      >
        ✓ Approve &amp; Post
      </button>

      <button
        v-if="!showFeedback"
        @click="showFeedback = true"
        :disabled="loading"
        class="flex-1 bg-amber-500 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-amber-600 disabled:opacity-40 transition-colors"
      >
        ↩ Reject &amp; Revise
      </button>

      <template v-if="showFeedback">
        <button
          @click="submitReject"
          :disabled="loading || !feedback.trim()"
          class="flex-1 bg-amber-500 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-amber-600 disabled:opacity-40 transition-colors"
        >
          {{ loading ? 'Revising…' : 'Submit Feedback' }}
        </button>
        <button
          @click="showFeedback = false; feedback = ''"
          :disabled="loading"
          class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
        >
          Cancel
        </button>
      </template>

      <button
        v-if="!showFeedback"
        @click="emit('decide', 'abandoned')"
        :disabled="loading"
        class="px-4 py-2 text-sm text-gray-500 hover:text-red-600 disabled:opacity-40 transition-colors"
      >
        Abandon
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ loading: boolean }>()
const emit = defineEmits<{
  decide: [decision: 'approved' | 'rejected' | 'abandoned', feedback?: string]
}>()

const showFeedback = ref(false)
const feedback = ref('')

function submitReject() {
  emit('decide', 'rejected', feedback.value)
  showFeedback.value = false
  feedback.value = ''
}
</script>
