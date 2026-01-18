<template>
  <div class="transliteration-guide-page">
    <div class="guide-header">
      <h1>⌨️ Tamil Transliteration Guide</h1>
      <p class="subtitle">Type English → Get Tamil (A→அ)</p>
    </div>

    <div class="stats">
      <div class="stat-card">
        <div class="stat-number">12</div>
        <div class="stat-label">Vowels</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">18</div>
        <div class="stat-label">Consonants</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">6</div>
        <div class="stat-label">Grantha</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">247</div>
        <div class="stat-label">Combos</div>
      </div>
    </div>

    <div class="content">
      <!-- Quick Reference -->
      <div class="quick-ref">
        <h3>⚡ Most Important for Tamil</h3>
        <div class="quick-ref-grid">
          <div class="quick-ref-item">
            <span class="tamil-char">ழ்</span>
            <span class="english-trans">zh</span>
            <span>→ தமிழ் (thamizh)</span>
          </div>
          <div class="quick-ref-item">
            <span class="tamil-char">ற்</span>
            <span class="english-trans">R</span>
            <span>→ அறம் (aRam)</span>
          </div>
          <div class="quick-ref-item">
            <span class="tamil-char">ன்</span>
            <span class="english-trans">n2</span>
            <span>→ மதன் (mathan2)</span>
          </div>
          <div class="quick-ref-item">
            <span class="tamil-char">ங்</span>
            <span class="english-trans">~N</span>
            <span>→ சங்கம் (sa~Ngam)</span>
          </div>
        </div>
      </div>

      <!-- Vowels Section -->
      <div class="section section-vowels" :class="{ collapsed: !sections.vowels }">
        <div class="section-header" @click="toggleSection('vowels')">
          <h2>📝 Vowels (உயிர் - 12)</h2>
          <span class="arrow">▼</span>
        </div>
        <div class="section-content">
          <div class="section-inner">
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Tamil</th>
                    <th>Type</th>
                    <th>Example</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><span class="tamil-char">அ</span> <span class="english-trans">a</span></td>
                    <td>Short</td>
                    <td class="example">அரம் (aram)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஆ</span> <span class="english-trans">aa, A</span></td>
                    <td>Long</td>
                    <td class="example">ஆனந்தம் (Aanandham)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">இ</span> <span class="english-trans">i</span></td>
                    <td>Short</td>
                    <td class="example">இயல் (iyal)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஈ</span> <span class="english-trans">ii, I</span></td>
                    <td>Long</td>
                    <td class="example">ஈசன் (Isan)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">உ</span> <span class="english-trans">u</span></td>
                    <td>Short</td>
                    <td class="example">உயிர் (uyir)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஊ</span> <span class="english-trans">uu, U</span></td>
                    <td>Long</td>
                    <td class="example">ஊர் (Ur)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">எ</span> <span class="english-trans">e</span></td>
                    <td>Short</td>
                    <td class="example">எழுத்து (ezhuthu)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஏ</span> <span class="english-trans">E</span></td>
                    <td>Long</td>
                    <td class="example">ஏது (Ethu)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஐ</span> <span class="english-trans">ai</span></td>
                    <td>Diphthong</td>
                    <td class="example">ஐயா (aiyya)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஒ</span> <span class="english-trans">o</span></td>
                    <td>Short</td>
                    <td class="example">ஒளி (oLi)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஓ</span> <span class="english-trans">O</span></td>
                    <td>Long</td>
                    <td class="example">ஓம் (Om)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஔ</span> <span class="english-trans">au</span></td>
                    <td>Diphthong</td>
                    <td class="example">ஔவையார் (auvaiyaar)</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Consonants Section -->
      <div class="section section-consonants" :class="{ collapsed: !sections.consonants }">
        <div class="section-header" @click="toggleSection('consonants')">
          <h2>🔠 Tamil Consonants (மெய் - 18)</h2>
          <span class="arrow">▼</span>
        </div>
        <div class="section-content">
          <div class="section-inner">
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Tamil</th>
                    <th>Type</th>
                    <th>Example</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><span class="tamil-char">க்</span> <span class="english-trans">k</span></td>
                    <td>Hard</td>
                    <td class="example">கல் (kal)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ச்</span> <span class="english-trans">ch, c</span></td>
                    <td>Hard</td>
                    <td class="example">செல்வம் (selvam)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ட்</span> <span class="english-trans">T</span></td>
                    <td>Hard</td>
                    <td class="example">டமிழர் (Tamilar)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">த்</span> <span class="english-trans">t</span></td>
                    <td>Hard</td>
                    <td class="example">தமிழ் (thamizh)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ப்</span> <span class="english-trans">p</span></td>
                    <td>Hard</td>
                    <td class="example">பால் (paal)</td>
                  </tr>
                  <tr class="unique-row">
                    <td><span class="tamil-char">ற்</span> <span class="english-trans">R</span></td>
                    <td>Hard ⭐</td>
                    <td class="example">அறம் (aRam)</td>
                  </tr>
                  <tr class="highlight-row">
                    <td><span class="tamil-char">ங்</span> <span class="english-trans">~N</span></td>
                    <td>Nasal</td>
                    <td class="example">சங்கம் (sa~Ngam)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஞ்</span> <span class="english-trans">~n</span></td>
                    <td>Nasal</td>
                    <td class="example">ஞானம் (~naanam)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ண்</span> <span class="english-trans">N</span></td>
                    <td>Nasal</td>
                    <td class="example">கண் (kaN)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ந்</span> <span class="english-trans">n</span></td>
                    <td>Nasal</td>
                    <td class="example">நலம் (nalam)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ம்</span> <span class="english-trans">m</span></td>
                    <td>Nasal</td>
                    <td class="example">மலர் (malar)</td>
                  </tr>
                  <tr class="unique-row">
                    <td><span class="tamil-char">ன்</span> <span class="english-trans">n2</span></td>
                    <td>Nasal ⭐</td>
                    <td class="example">மதன் (mathan2)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ய்</span> <span class="english-trans">y</span></td>
                    <td>Medium</td>
                    <td class="example">யாழ் (yaazh)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ர்</span> <span class="english-trans">r</span></td>
                    <td>Medium</td>
                    <td class="example">ரசம் (rasam)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ல்</span> <span class="english-trans">l</span></td>
                    <td>Medium</td>
                    <td class="example">லட்சுமி (lakshmi)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">வ்</span> <span class="english-trans">v</span></td>
                    <td>Medium</td>
                    <td class="example">வழி (vazhi)</td>
                  </tr>
                  <tr class="unique-row">
                    <td><span class="tamil-char">ழ்</span> <span class="english-trans">zh</span></td>
                    <td>Medium ⭐</td>
                    <td class="example">அழகு (azhagu)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ள்</span> <span class="english-trans">L</span></td>
                    <td>Medium</td>
                    <td class="example">வள்ளுவர் (vaLLuvar)</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="success-box">
              <h3>⭐ Unique Tamil Letters</h3>
              <p>Green rows are unique to Tamil: <code>zh</code> (ழ), <code>R</code> (ற), <code>n2</code> (ன)</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Grantha Letters Section -->
      <div class="section section-grantha" :class="{ collapsed: !sections.grantha }">
        <div class="section-header" @click="toggleSection('grantha')">
          <h2>🌟 Grantha Letters (6)</h2>
          <span class="arrow">▼</span>
        </div>
        <div class="section-content">
          <div class="section-inner">
            <p class="note" style="margin-bottom: 1rem;">For Sanskrit loanwords</p>
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Tamil</th>
                    <th>Usage</th>
                    <th>Example</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><span class="tamil-char">ஜ்</span> <span class="english-trans">j</span></td>
                    <td>Common</td>
                    <td class="example">ஜலம் (jalam)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஶ்</span> <span class="english-trans">sh</span></td>
                    <td>Palatal</td>
                    <td class="example">ஶிவன் (shivan)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஷ்</span> <span class="english-trans">Sh</span></td>
                    <td>Retroflex</td>
                    <td class="example">விஷ்ணு (viShNu)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஸ்</span> <span class="english-trans">s</span></td>
                    <td>Dental</td>
                    <td class="example">ஸத்யம் (satyam)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">ஹ்</span> <span class="english-trans">h</span></td>
                    <td>Aspirated</td>
                    <td class="example">ஹரி (hari)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">க்ஷ்</span> <span class="english-trans">ksh</span></td>
                    <td>Compound</td>
                    <td class="example">லக்ஷ்மி (lakshmi)</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Special Characters Section -->
      <div class="section section-special" :class="{ collapsed: !sections.special }">
        <div class="section-header" @click="toggleSection('special')">
          <h2>⚡ Special & Numbers</h2>
          <span class="arrow">▼</span>
        </div>
        <div class="section-content">
          <div class="section-inner">
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Tamil</th>
                    <th>Name</th>
                    <th>Usage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><span class="tamil-char">ஃ</span> <span class="english-trans">H</span></td>
                    <td>Aytham</td>
                    <td class="example">ஃது (hathu)</td>
                  </tr>
                  <tr>
                    <td><span class="tamil-char">்</span></td>
                    <td>Pulli</td>
                    <td class="note">Removes vowel (க் = k)</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <h3 style="margin: 1rem 0 0.5rem 0; font-size: 1rem;">Tamil Numerals</h3>
            <div class="alphabet-grid">
              <div class="alphabet-item">௦</div>
              <div class="alphabet-item">௧</div>
              <div class="alphabet-item">௨</div>
              <div class="alphabet-item">௩</div>
              <div class="alphabet-item">௪</div>
              <div class="alphabet-item">௫</div>
              <div class="alphabet-item">௬</div>
              <div class="alphabet-item">௭</div>
              <div class="alphabet-item">௮</div>
              <div class="alphabet-item">௯</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Usage Tips -->
      <div class="info-box">
        <h3>💡 Quick Tips</h3>
        <ul>
          <li><strong>Case matters!</strong> Small (t, n, l) vs Capital (T, N, L, R)</li>
          <li><strong>Unique Tamil:</strong> <code>zh</code> = ழ, <code>R</code> = ற, <code>n2</code> = ன</li>
          <li><strong>Long vowels:</strong> <code>aa</code> or <code>A</code> → ஆ</li>
          <li><strong>Three N sounds:</strong> <code>n</code> (ந), <code>N</code> (ண), <code>n2</code> (ன)</li>
          <li><strong>Examples:</strong> thirukkural → திருக்குறள், azhagu → அழகு</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const sections = reactive({
  vowels: false,
  consonants: false,
  grantha: false,
  special: false
})

function toggleSection(section) {
  sections[section] = !sections[section]
}
</script>

<style scoped>
.transliteration-guide-page {
  min-height: calc(100vh - 200px);
  background: #f8f9fa;
}

/* Header */
.guide-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 1rem;
  text-align: center;
}

.guide-header h1 {
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
  color: white;
}

.subtitle {
  font-size: 1rem;
  opacity: 0.95;
  margin: 0;
}

/* Stats */
.stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.25rem;
  border-radius: 8px;
  text-align: center;
}

.stat-number {
  font-size: 2.25rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.95;
}

/* Content */
.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

/* Collapsible Sections */
.section {
  margin-bottom: 1.25rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.section-header {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: 1rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.section-header h2 {
  font-size: 1.15rem;
  margin: 0;
  color: white;
}

.section-header .arrow {
  font-size: 1rem;
  transition: transform 0.3s ease;
}

.section.collapsed .arrow {
  transform: rotate(-90deg);
}

.section-content {
  max-height: 5000px;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.section.collapsed .section-content {
  max-height: 0;
}

.section-inner {
  padding: 1.25rem;
}

/* Color themes for sections */
.section-vowels .section-header {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.section-consonants .section-header {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.section-grantha .section-header {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.section-special .section-header {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

/* Compact Tables */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

th {
  background: #f3f4f6;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.85rem;
  border-bottom: 2px solid #d1d5db;
}

td {
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: top;
}

tr:last-child td {
  border-bottom: none;
}

/* Tamil characters */
.tamil-char {
  font-size: 1.4rem;
  font-weight: bold;
  color: #dc2626;
}

.english-trans {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
  white-space: nowrap;
}

.example {
  color: #2563eb;
  font-size: 0.9rem;
}

.note {
  color: #6b7280;
  font-size: 0.85rem;
}

/* Highlighted rows */
.highlight-row {
  background: #fef3c7 !important;
}

.unique-row {
  background: #d1fae5 !important;
}

/* Info boxes */
.info-box {
  background: #dbeafe;
  border-left: 4px solid #2563eb;
  padding: 1.25rem;
  margin: 1.5rem 0;
  border-radius: 4px;
  font-size: 0.95rem;
}

.info-box h3 {
  margin: 0 0 0.75rem 0;
  font-size: 1.05rem;
  color: #1e40af;
}

.info-box ul {
  margin: 0.5rem 0 0 1.5rem;
}

.info-box li {
  margin: 0.5rem 0;
}

.success-box {
  background: #d1fae5;
  border-left: 4px solid #10b981;
  padding: 1.25rem;
  margin: 1.5rem 0;
  border-radius: 4px;
}

.success-box h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.05rem;
  color: #047857;
}

.success-box p {
  font-size: 0.9rem;
  margin: 0;
}

code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #dc2626;
  font-size: 0.85rem;
}

/* Alphabet Grid */
.alphabet-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.75rem;
  margin: 1rem 0;
}

.alphabet-item {
  background: #f8f9fa;
  border: 2px solid #e5e7eb;
  padding: 0.75rem;
  text-align: center;
  border-radius: 6px;
  font-size: 1.5rem;
  font-weight: bold;
  color: #dc2626;
}

/* Quick reference card */
.quick-ref {
  background: #fff7ed;
  border: 2px solid #fb923c;
  border-radius: 8px;
  padding: 1.25rem;
  margin: 0 0 1.5rem 0;
}

.quick-ref h3 {
  margin: 0 0 1rem 0;
  color: #ea580c;
  font-size: 1.05rem;
}

.quick-ref-grid {
  display: grid;
  gap: 0.75rem;
}

.quick-ref-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
}

.quick-ref-item .tamil-char {
  font-size: 1.2rem;
  min-width: 45px;
}

.quick-ref-item .english-trans {
  min-width: 55px;
}

/* Desktop adjustments */
@media (min-width: 768px) {
  .guide-header {
    padding: 2.5rem;
  }

  .guide-header h1 {
    font-size: 2.25rem;
  }

  .subtitle {
    font-size: 1.1rem;
  }

  .stats {
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
    padding: 2rem;
  }

  .stat-number {
    font-size: 2.75rem;
  }

  .content {
    padding: 2.5rem;
  }

  .section {
    margin-bottom: 2rem;
  }

  .section-header {
    padding: 1.5rem;
  }

  .section-header h2 {
    font-size: 1.4rem;
  }

  .section-inner {
    padding: 2rem;
  }

  table {
    font-size: 1rem;
  }

  .alphabet-grid {
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  }

  .quick-ref-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Mobile adjustments */
@media (max-width: 767px) {
  .guide-header h1 {
    font-size: 1.5rem;
  }

  .stats {
    padding: 1rem;
  }

  .content {
    padding: 1rem;
  }

  .section-header {
    padding: 0.875rem;
  }

  .section-header h2 {
    font-size: 1rem;
  }

  .section-inner {
    padding: 1rem;
  }
}
</style>
