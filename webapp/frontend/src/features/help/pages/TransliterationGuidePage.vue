<template>
  <div class="help-page">
    <div class="help-container">
      <!-- Breadcrumb Navigation -->
      <nav class="breadcrumb">
        <router-link :to="{ name: 'Help' }">Help</router-link>
        <span class="separator">›</span>
        <span>Transliteration Guide</span>
      </nav>

      <!-- Page Header -->
      <header class="page-header">
        <h1>தமிழ் எழுத்துப்பெயர்ப்பு வழிகாட்டி</h1>
        <h1>Tamil Transliteration Guide</h1>
        <p class="subtitle">Type English characters to get Tamil letters using ITRANS Dravidian scheme (A→அ, zh→ழ)</p>
      </header>

      <!-- Table of Contents -->
      <nav class="table-of-contents">
        <h3>Contents</h3>
        <ul>
          <li><a href="#tips">💡 Quick Tips</a></li>
          <!--<li><a href="#quick-ref">⚡ Most Important for Tamil</a></li>-->
          <li><a href="#vowels">📝 Vowels (உயிர் - 12)</a></li>
          <li><a href="#consonants">🔠 Tamil Consonants (மெய் - 18)</a></li>
          <li><a href="#grantha">🌟 Grantha Letters (6)</a></li>
          <li><a href="#special">⚡ Special & Numbers</a></li>

        </ul>
      </nav>

      <!-- Main Content -->
      <main class="help-content">
        <!-- Quick Reference
        <section id="quick-ref" class="content-section">
          <h2>⚡ Most Important for Tamil</h2>
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
              <span class="english-trans">nn, n2</span>
              <span>→ மகன் (makann)</span>
            </div>
            <div class="quick-ref-item">
              <span class="tamil-char">ங்</span>
              <span class="english-trans">~N</span>
              <span>→ சங்கம் (sa~Ngam)</span>
            </div>
          </div>
        </section>
         -->
        
        <!-- Usage Tips -->
        <section id="tips" class="content-section">
          <h2>💡 Quick Tips</h2>
          <div class="example-block">
            <ul>
              <li><strong>Case matters!</strong> Small (t, n, l) vs Capital (T, N, L, R)</li>
              <li><strong>Unique Tamil:</strong> <code>zh</code> = ழ, <code>R</code> = ற, <code>nn</code> or <code>n2</code> = ன</li>
              <li><strong>Long vowels:</strong> <code>aa</code> or <code>A</code> → ஆ</li>
              <li><strong>Three N sounds:</strong> <code>n</code> (ந), <code>N</code> (ண), <code>nn</code> or <code>n2</code> (ன)</li>
              <li><strong>Examples:</strong> thirukkural → திருக்குறள், azhagu → அழகு, makann → மகன்</li>
            </ul>
          </div>
        </section>

        <!-- Vowels Section -->
        <section id="vowels" class="content-section">
          <h2>📝 Vowels (உயிர் - 12)</h2>
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
                  <td class="example">அறம் (aRam)</td>
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
        </section>

        <!-- Consonants Section -->
        <section id="consonants" class="content-section">
          <h2>🔠 Tamil Consonants (மெய் - 18)</h2>
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
                  <td class="example">தமிழர் (thamizhar)</td>
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
                  <td><span class="tamil-char">ன்</span> <span class="english-trans">nn, n2</span></td>
                  <td>Nasal ⭐</td>
                  <td class="example">மகன் (makann)</td>
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
                  <td class="example">கல்வி (kalvi)</td>
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

          <div class="example-block">
            <p><strong>⭐ Unique Tamil Letters</strong></p>
            <p>Green-highlighted rows are unique to Tamil: <code>zh</code> (ழ), <code>R</code> (ற), <code>nn</code> or <code>n2</code> (ன)</p>
          </div>
        </section>

        <!-- Grantha Letters Section -->
        <section id="grantha" class="content-section">
          <h2>🌟 Grantha Letters (6)</h2>
          <p>For Sanskrit loanwords</p>
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
        </section>

        <!-- Special Characters Section -->
        <section id="special" class="content-section">
          <h2>⚡ Special & Numbers</h2>

          <h3>Special Characters</h3>
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

          <h3>Tamil Numerals</h3>
          <div class="word-list">
            <div class="word-item">௦</div>
            <div class="word-item">௧</div>
            <div class="word-item">௨</div>
            <div class="word-item">௩</div>
            <div class="word-item">௪</div>
            <div class="word-item">௫</div>
            <div class="word-item">௬</div>
            <div class="word-item">௭</div>
            <div class="word-item">௮</div>
            <div class="word-item">௯</div>
          </div>
        </section>
      </main>

      <!-- Footer -->
      <footer class="help-footer">
        <p><router-link :to="{ name: 'Help' }">← Back to Help</router-link></p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { useAnchorScroll } from '../../../composables/useAnchorScroll'

// Enable smooth scrolling for anchor links
useAnchorScroll()
</script>

<style scoped>
/* Import shared help page styles */
@import '../../../assets/styles/help-pages.css';

/* Custom styles for transliteration guide */

/* Quick Reference Grid */
.quick-ref-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.quick-ref-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #fff7ed 0%, #ffe4e6 100%);
  border: 2px solid #fb923c;
  border-radius: 8px;
  font-size: 0.95rem;
}

.quick-ref-item .tamil-char {
  font-size: 1.5rem;
  font-weight: bold;
  color: #dc2626;
  min-width: 40px;
}

.quick-ref-item .english-trans {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  min-width: 55px;
  text-align: center;
}

/* Table styling */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin: 1rem 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 1rem;
}

th {
  background: #f3f4f6;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
  border-bottom: 2px solid #d1d5db;
}

td {
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

tr:last-child td {
  border-bottom: none;
}

/* Tamil characters */
.tamil-char {
  font-size: 1.5rem;
  font-weight: bold;
  color: #dc2626;
  margin-right: 0.5rem;
}

.english-trans {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 3px 7px;
  border-radius: 3px;
  font-weight: 600;
  white-space: nowrap;
  font-size: 0.9rem;
}

.example {
  color: #2563eb;
  font-size: 0.95rem;
}

.note {
  color: #6b7280;
  font-size: 0.9rem;
  font-style: italic;
}

/* Highlighted rows */
.highlight-row {
  background: #fef3c7 !important;
}

.unique-row {
  background: #d1fae5 !important;
}

code {
  background: #f3f4f6;
  padding: 3px 7px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #dc2626;
  font-size: 0.9rem;
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .quick-ref-grid {
    grid-template-columns: 1fr;
  }

  .quick-ref-item {
    font-size: 0.9rem;
  }

  .tamil-char {
    font-size: 1.3rem;
  }

  table {
    font-size: 0.9rem;
  }

  th, td {
    padding: 0.6rem 0.5rem;
  }
}
</style>
