<template>
  <div class="transliteration-comparison">
    <div class="header">
      <h1>🧪 Transliteration Comparison Test</h1>
      <p>Compare Sanscript (current) vs AI4Bharat (AI-powered)</p>
    </div>

    <!-- Model Status -->
    <div class="model-status">
      <div class="status-card">
        <h3>📚 Sanscript (Current)</h3>
        <div class="status-badge ready">✓ Ready</div>
        <p>Rule-based ITRANS Dravidian</p>
      </div>
      <div class="status-card">
        <h3>🤖 AI4Bharat (Testing)</h3>
        <div v-if="ai4bharat.modelLoading.value" class="status-badge loading">⏳ Loading...</div>
        <div v-else-if="ai4bharat.modelLoaded.value" class="status-badge ready">✓ Ready</div>
        <div v-else-if="ai4bharat.modelError.value" class="status-badge error">✗ Error</div>
        <div v-else class="status-badge pending">⚪ Not Loaded</div>
        <p v-if="ai4bharat.modelLoaded.value">
          Loaded in {{ ai4bharat.modelLoadTime.value.toFixed(0) }}ms
        </p>
        <p v-if="ai4bharat.modelError.value" class="error-text">
          {{ ai4bharat.modelError.value }}
        </p>
      </div>
    </div>

    <!-- Live Test Input -->
    <div class="test-section">
      <h2>🔤 Live Test</h2>
      <input
        v-model="liveInput"
        type="text"
        placeholder="Type in English (e.g., thirukkural, aram, azhagu)"
        class="test-input"
        @input="onLiveInput"
      />
      <div class="results-grid">
        <div class="result-card">
          <h4>Sanscript</h4>
          <div class="tamil-output">{{ sanscriptOutput }}</div>
          <div class="performance">{{ sanscriptTime }}ms</div>
        </div>
        <div class="result-card">
          <h4>AI4Bharat</h4>
          <div class="tamil-output">{{ ai4bharatOutput }}</div>
          <div class="performance">{{ ai4bharatTime }}ms</div>
        </div>
      </div>
    </div>

    <!-- Preset Tests -->
    <div class="test-section">
      <h2>📝 Preset Tests (Literary Tamil)</h2>
      <p class="test-description">
        Click "Run All Tests" to compare transliteration accuracy for common literary Tamil words
      </p>
      <button @click="runAllTests" class="run-tests-btn" :disabled="!ai4bharat.modelLoaded.value">
        {{ ai4bharat.modelLoaded.value ? '▶ Run All Tests' : '⏳ Waiting for AI4Bharat model...' }}
      </button>

      <div v-if="testResults.length > 0" class="test-results">
        <div class="results-summary">
          <div class="summary-stat">
            <strong>Total Tests:</strong> {{ testResults.length }}
          </div>
          <div class="summary-stat">
            <strong>Sanscript Match:</strong> {{ sanscriptMatches }} ({{ sanscriptAccuracy }}%)
          </div>
          <div class="summary-stat">
            <strong>AI4Bharat Match:</strong> {{ ai4bharatMatches }} ({{ ai4bharatAccuracy }}%)
          </div>
        </div>

        <table class="results-table">
          <thead>
            <tr>
              <th>Input</th>
              <th>Expected</th>
              <th>Sanscript</th>
              <th>AI4Bharat</th>
              <th>Winner</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(result, index) in testResults" :key="index" :class="result.winnerClass">
              <td class="input-col">{{ result.input }}</td>
              <td class="tamil-col">{{ result.expected }}</td>
              <td class="tamil-col" :class="{ match: result.sanscriptMatch }">
                {{ result.sanscriptOutput }}
                {{ result.sanscriptMatch ? '✓' : '✗' }}
              </td>
              <td class="tamil-col" :class="{ match: result.ai4bharatMatch }">
                {{ result.ai4bharatOutput }}
                {{ result.ai4bharatMatch ? '✓' : '✗' }}
              </td>
              <td>{{ result.winner }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTransliteration } from '../composables/useTransliteration'
import { useAI4BharatTransliteration } from '../composables/useAI4BharatTransliteration'

// Initialize both transliteration systems
const sanscript = useTransliteration()
const ai4bharat = useAI4BharatTransliteration()

// Live test
const liveInput = ref('')
const sanscriptOutput = ref('')
const ai4bharatOutput = ref('')
const sanscriptTime = ref(0)
const ai4bharatTime = ref(0)

// Test results
const testResults = ref([])

// Test cases (literary Tamil words)
const testCases = [
  { input: 'thirukkural', expected: 'திருக்குறள்', category: 'Work Names' },
  { input: 'thirumuRai', expected: 'திருமுறை', category: 'Work Names' },
  { input: 'kambaramayanam', expected: 'கம்பராமாயணம்', category: 'Work Names' },
  { input: 'silappathikaram', expected: 'சிலப்பதிகாரம்', category: 'Work Names' },
  { input: 'manimegalai', expected: 'மணிமேகலை', category: 'Work Names' },
  { input: 'tolkappiyam', expected: 'தொல்காப்பியம்', category: 'Work Names' },
  { input: 'naalaayira', expected: 'நாலாயிர', category: 'Work Names' },
  { input: 'sangam', expected: 'சங்கம்', category: 'Work Names' },
  { input: 'thiruvasagam', expected: 'திருவாசகம்', category: 'Work Names' },
  { input: 'thiruppugazh', expected: 'திருப்புகழ்', category: 'Work Names' },

  { input: 'aRam', expected: 'அறம்', category: 'Concepts' },
  { input: 'poruL', expected: 'பொருள்', category: 'Concepts' },
  { input: 'inbam', expected: 'இன்பம்', category: 'Concepts' },
  { input: 'veedu', expected: 'வீடு', category: 'Concepts' },
  { input: 'azhagu', expected: 'அழகு', category: 'Concepts' },
  { input: 'kaadhal', expected: 'காதல்', category: 'Concepts' },
  { input: 'aNangu', expected: 'அணங்கு', category: 'Concepts' },
  { input: 'vazhkai', expected: 'வாழ்கை', category: 'Concepts' },

  { input: 'vaLLuvar', expected: 'வள்ளுவர்', category: 'Names' },
  { input: 'kambar', expected: 'கம்பர்', category: 'Names' },
  { input: 'iLangu', expected: 'இளங்கு', category: 'Names' },
  { input: 'seethalaik kaadhanar', expected: 'சீத்தலைக் காதனார்', category: 'Names' },

  { input: 'thozhi', expected: 'தொழி', category: 'Words' },
  { input: 'thaazh', expected: 'தாழ்', category: 'Words' },
  { input: 'kuzhal', expected: 'குழல்', category: 'Words' },
  { input: 'vazhuthunai', expected: 'வழுத்துணை', category: 'Words' },
  { input: 'maN', expected: 'மண்', category: 'Words' },
  { input: 'neer', expected: 'நீர்', category: 'Words' },
  { input: 'theeyoor', expected: 'தீயூர்', category: 'Words' },
  { input: 'kaRRu', expected: 'கற்று', category: 'Words' }
]

// Live input handler
const onLiveInput = async () => {
  if (!liveInput.value) {
    sanscriptOutput.value = ''
    ai4bharatOutput.value = ''
    sanscriptTime.value = 0
    ai4bharatTime.value = 0
    return
  }

  // Test Sanscript
  const sanscriptStart = performance.now()
  sanscriptOutput.value = sanscript.transliterate(liveInput.value)
  sanscriptTime.value = Math.round(performance.now() - sanscriptStart)

  // Test AI4Bharat
  const ai4bharatStart = performance.now()
  ai4bharatOutput.value = await ai4bharat.transliterate(liveInput.value)
  ai4bharatTime.value = Math.round(performance.now() - ai4bharatStart)
}

// Run all test cases
const runAllTests = async () => {
  testResults.value = []

  for (const testCase of testCases) {
    // Run Sanscript
    const sanscriptResult = sanscript.transliterate(testCase.input)
    const sanscriptMatch = sanscriptResult === testCase.expected

    // Run AI4Bharat
    const ai4bharatResult = await ai4bharat.transliterate(testCase.input)
    const ai4bharatMatch = ai4bharatResult === testCase.expected

    // Determine winner
    let winner = 'Tie'
    let winnerClass = 'tie'
    if (sanscriptMatch && !ai4bharatMatch) {
      winner = 'Sanscript'
      winnerClass = 'sanscript-win'
    } else if (ai4bharatMatch && !sanscriptMatch) {
      winner = 'AI4Bharat'
      winnerClass = 'ai4bharat-win'
    } else if (sanscriptMatch && ai4bharatMatch) {
      winner = 'Both ✓'
      winnerClass = 'both-win'
    } else {
      winner = 'Both ✗'
      winnerClass = 'both-lose'
    }

    testResults.value.push({
      input: testCase.input,
      expected: testCase.expected,
      sanscriptOutput: sanscriptResult,
      ai4bharatOutput: ai4bharatResult,
      sanscriptMatch,
      ai4bharatMatch,
      winner,
      winnerClass
    })
  }
}

// Computed statistics
const sanscriptMatches = computed(() =>
  testResults.value.filter(r => r.sanscriptMatch).length
)

const ai4bharatMatches = computed(() =>
  testResults.value.filter(r => r.ai4bharatMatch).length
)

const sanscriptAccuracy = computed(() =>
  testResults.value.length > 0
    ? Math.round((sanscriptMatches.value / testResults.value.length) * 100)
    : 0
)

const ai4bharatAccuracy = computed(() =>
  testResults.value.length > 0
    ? Math.round((ai4bharatMatches.value / testResults.value.length) * 100)
    : 0
)

// Initialize AI4Bharat model on mount
onMounted(() => {
  ai4bharat.initializeModel()
})
</script>

<style scoped>
.transliteration-comparison {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: system-ui, -apple-system, sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.header p {
  color: #666;
  font-size: 1.1rem;
}

.model-status {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.status-card {
  padding: 1.5rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  text-align: center;
}

.status-card h3 {
  margin-bottom: 0.5rem;
}

.status-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  margin: 0.5rem 0;
}

.status-badge.ready {
  background: #4caf50;
  color: white;
}

.status-badge.loading {
  background: #ff9800;
  color: white;
}

.status-badge.error {
  background: #f44336;
  color: white;
}

.status-badge.pending {
  background: #9e9e9e;
  color: white;
}

.error-text {
  color: #f44336;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.test-section {
  margin-bottom: 3rem;
  padding: 2rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.test-section h2 {
  margin-bottom: 1rem;
}

.test-description {
  color: #666;
  margin-bottom: 1rem;
}

.test-input {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.results-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.result-card {
  padding: 1.5rem;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
}

.result-card h4 {
  margin-bottom: 1rem;
  color: #333;
}

.tamil-output {
  font-size: 2rem;
  font-weight: bold;
  min-height: 3rem;
  margin-bottom: 0.5rem;
  color: #2196f3;
}

.performance {
  font-size: 0.9rem;
  color: #666;
}

.run-tests-btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  margin-bottom: 2rem;
}

.run-tests-btn:hover:not(:disabled) {
  background: #1976d2;
}

.run-tests-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.results-summary {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  justify-content: center;
}

.summary-stat {
  font-size: 1.1rem;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.results-table th {
  background: #333;
  color: white;
  padding: 1rem;
  text-align: left;
}

.results-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.input-col {
  font-family: monospace;
  color: #666;
}

.tamil-col {
  font-size: 1.2rem;
  font-weight: bold;
}

.tamil-col.match {
  color: #4caf50;
}

.both-win {
  background: #e8f5e9;
}

.sanscript-win {
  background: #fff9c4;
}

.ai4bharat-win {
  background: #e3f2fd;
}

.both-lose {
  background: #ffebee;
}
</style>
