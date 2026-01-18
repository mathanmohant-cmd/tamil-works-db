<template>
  <div class="search-page">
    <!-- Welcome Message & QuickStart Guide -->
    <div class="welcome">
        <nav class="breadcrumb">
      <router-link :to="{ name: 'Help' }">Help</router-link>
      <span class="separator">›</span>
      <span>Quick Start</span>
    </nav>
    <header class="page-header">
      <h1>Quick Start</h1>
    </header>
      <!-- Try Examples Section -->
      <div class="try-examples">
        <h3>Quick Try: Click These Words</h3>
        <div class="example-buttons">
          <button @click="tryExampleSearch('அறம்')" class="example-btn">அறம்</button>
          <button @click="tryExampleSearch('தமிழ்நாடு')" class="example-btn">தமிழ்நாடு</button>
          <button @click="tryExampleSearch('எஃகு')" class="example-btn">எஃகு</button>
          <button @click="tryExampleSearch('அடிசில்')" class="example-btn">அடிசில்</button>
          <button @click="tryExampleSearch('ஈனில்')" class="example-btn">ஈனில்</button>
        </div>
      </div>

      <!-- Quick Start Guide -->
      <div class="quick-start">
        <h3>To explore more</h3>
        <ul class="tips-list">
          <li><strong>Type a Thamizh word</strong> in the search box above</li>
          <li><strong>Choose match type:</strong> Partial (finds similar words) or Exact (precise match)</li>
          <li><strong>Set position:</strong> Beginning, End, or Anywhere in the word</li>
          <li><strong>Filter by works</strong> (optional) to search specific texts</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useSearchState } from '../composables/useSearchState.js'
import { useFilterState } from '../composables/useFilterState.js'

const router = useRouter()

// Use composables to access filter state
const { matchType, wordPosition } = useSearchState()
const { filterMode, selectedWorks } = useFilterState()

// Try example search
const tryExampleSearch = (word) => {
  // Reset search filters to defaults
  matchType.value = 'partial'
  wordPosition.value = 'anywhere'

  // Clear work filters
  filterMode.value = 'all'
  selectedWorks.value = []

  // Navigate to search results with query
  router.push({
    name: 'SearchResults',
    query: {
      q: word,
      type: 'partial',
      pos: 'anywhere'
    }
  })
}
</script>

<style scoped>
.search-page {
  position: relative;
}

/* Welcome Message */
.welcome {
  max-width: 800px;
  margin: 1rem auto;
  padding: 2rem 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.welcome h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.4 rem;
  color: #2c3e50;
  text-align: center;
}

.welcome h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9 rem;
  color: #2c3e50;
  text-align: center;
}

.welcome-subtitle {
  text-align: center;
  font-size: 1.1rem;
  color: #6c757d;
  margin-bottom: .5rem;
  font-style: italic;
}

.quick-start {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 6px;
}

.quick-start h3 {
  margin: 0 0 1rem 0;
  font-size: 1.3rem;
  color: #2c3e50;
}

.tips-list {
  margin: 0 0 1rem 1.5rem;
  padding: 0;
}

.tips-list li {
  margin-bottom: 0.75rem;
  line-height: 1.6;
  color: #495057;
}

.learn-more {
  margin: 1rem 0 0 0;
  text-align: center;
}

.try-examples {
  text-align: center;
  margin-bottom: 2rem;
}

.try-examples h3 {
  margin: 0 0 1rem 0;
  font-size: .9rem;
  color: #2c3e50;
}

.example-buttons {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.example-btn {
  padding: 0.6rem 1.2rem;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 600;
  transition: all 0.2s;
}

.example-btn:hover {
  background: #357abd;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(74, 144, 226, 0.3);
}

.acknowledgement {
  color: #0f4c81;
  text-decoration: none;
  border-bottom: 1px dotted var(--life-pulse);
  font-weight: 400;
}

.acknowledgement:hover {
  border-bottom: 1px dotted var(--life-pulse);
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  color: var(--text-secondary);
}

.breadcrumb a {
  color: var(--secondary-color);
  text-decoration: none;
  transition: color 0.2s ease;
}

.breadcrumb a:hover {
  color: var(--primary-color);
  text-decoration: underline;
}

.breadcrumb .separator {
  color: var(--text-secondary);
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--primary-color);
}

.page-header h1 {
  font-size: 2rem;
  margin: 0 0 0.5rem 0;
  color: var(--primary-color);
  font-weight: 700;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .welcome {
    padding: .25rem;
    margin: 0 0rem;
  }

  .welcome h2 {
    font-size: 1.2rem;
    margin: 0 0rem;
  }
  
  .welcome h3 {
    font-size: .9rem;
    margin: 0 0rem;
  }
  

  .welcome-subtitle {
    font-size: 1rem;
  }

  .quick-start {
    padding: .5rem;
  }

  .quick-start h3 {
    font-size: .9rem;
  }

  .tips-list {
    margin-left: 1rem;
  }

  .tips-list li {
    font-size: 0.95rem;
  }

  .example-buttons {
    gap: 0.5rem;
  }

  .example-btn {
    padding: 0.5rem 1rem;
    font-size: 1rem;
  }

  .try-examples {
    padding: .5rem;
  }
}
</style>
