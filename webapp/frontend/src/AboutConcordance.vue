<template>
  <div class="about-page">
    <div class="about-container">
      <!-- Tab Navigation -->
      <nav class="tab-nav">
        <button
          @click="activeTab = 'qa'"
          :class="{ active: activeTab === 'qa' }"
          class="tab-button"
        >
          Understanding Concordance
        </button>
        <button
          @click="activeTab = 'principles'"
          :class="{ active: activeTab === 'principles' }"
          class="tab-button"
        >
          Word Segmentation Principles
        </button>
      </nav>

      <!-- Q&A Tab Content -->
      <article v-if="activeTab === 'qa'" class="content-section qa-content">
        <header class="page-header">
          <p class="subtitle">A Guide for First-Time Users</p>
        </header>

        <section class="accordion-section">
          <div class="accordion-header" @click="toggleSection('qa-1')" :class="{ expanded: expandedSections.has('qa-1') }" data-section="qa-1">
            <h2>What is a Concordance?</h2>
            <span class="accordion-icon">
              <span class="chevron-icon" :class="expandedSections.has('qa-1') ? 'chevron-down' : 'chevron-right'"></span>
            </span>
          </div>
          <div v-if="expandedSections.has('qa-1')" class="accordion-content">
            <p>Think of a concordance as a <strong>super-powered search engine for books</strong>.</p>

            <p>Instead of just telling you what a word means (like a dictionary does), a concordance shows you <strong>every single place that word appears</strong> in a collection of books, along with the full sentence or verse where it's used.</p>

            <div class="example-box">
              <h3>Simple Example:</h3>
              <div class="comparison">
                <div class="comparison-item">
                  <strong>Dictionary:</strong>
                  <p>"அறம்" means virtue, righteousness, duty</p>
                </div>
                <div class="comparison-item">
                  <strong>Concordance:</strong>
                  <p>Shows you all the places where "அறம்" appears in Tamil literature, with the complete line and context</p>
                </div>
              </div>
            </div>
            <div class="accordion-close" @click="toggleSection('qa-1')">
              <span class="chevron-icon chevron-up"></span>
            </div>
          </div>
        </section>

        <section class="accordion-section">
          <div class="accordion-header" @click="toggleSection('qa-2')" :class="{ expanded: expandedSections.has('qa-2') }" data-section="qa-2">
            <h2>How is Concordance Different from a Dictionary?</h2>
            <span class="accordion-icon">
              <span class="chevron-icon" :class="expandedSections.has('qa-2') ? 'chevron-down' : 'chevron-right'"></span>
            </span>
          </div>
          <div v-if="expandedSections.has('qa-2')" class="accordion-content">
            <p>Great question! Here's the key difference:</p>

            <div class="comparison-table">
            <div class="table-row header-row">
              <div class="table-cell">📖 Dictionary</div>
              <div class="table-cell">🔍 Concordance (This Tool)</div>
            </div>
            <div class="table-row">
              <div class="table-cell"><span class="icon">📖</span> Tells you what a word <strong>means</strong></div>
              <div class="table-cell"><span class="icon">🔍</span> Shows you how a word is <strong>actually used</strong></div>
            </div>
            <div class="table-row">
              <div class="table-cell"><span class="icon">📖</span> Gives one or two example sentences</div>
              <div class="table-cell"><span class="icon">🔍</span> Shows <strong>every occurrence</strong> across all literature</div>
            </div>
            <div class="table-row">
              <div class="table-cell"><span class="icon">📖</span> Definition is the same for everyone</div>
              <div class="table-cell"><span class="icon">🔍</span> You see how <strong>different authors</strong> used the same word</div>
            </div>
            <div class="table-row">
              <div class="table-cell"><span class="icon">📖</span> Useful for learning vocabulary</div>
              <div class="table-cell"><span class="icon">🔍</span> Useful for understanding <strong>context, usage patterns, and deeper meanings</strong></div>
            </div>
          </div>

          <div class="example-box">
            <h3>Real-World Example</h3>
            <p>Let's say you search for the word <strong>"காதல்" (love)</strong>:</p>
          </div>

            <div class="example-content">
              <h4>📖 What a dictionary tells you:</h4>
              <div class="dictionary-result">
                <p class="definition">காதல் = Love, affection</p>
              </div>

              <h4>🔍 What THIS tool tells you:</h4>
              <div class="concordance-result">
                <ul>
                  <li><strong>How many different works</strong> காதல் appears in</li>
                  <li><strong>How many verses</strong> across Sangam literature, Thirukkural, and devotional texts காதல் appears</li>
                  <li>Location reference and option to <strong>Export</strong> for further analysis.</li>
                  <li>Gives a sense of the context - In Sangam poetry, it appears in nature imagery and love poems. In devotional literature, it describes divine love for God</li>
                </ul>
              </div>

              <div class="key-difference">
                <strong>The difference?</strong> You're not just learning what the word means — you're learning how great Tamil poets and saints actually used it across 2,000 years of literature!
              </div>
            </div>
            <div class="accordion-close" @click="toggleSection('qa-2')">
              <span class="chevron-icon chevron-up"></span>
            </div>
          </div>
        </section>

        <section class="accordion-section">
          <div class="accordion-header" @click="toggleSection('qa-3')" :class="{ expanded: expandedSections.has('qa-3') }" data-section="qa-3">
            <h2>Why is Concordance Important?</h2>
            <span class="accordion-icon">
              <span class="chevron-icon" :class="expandedSections.has('qa-3') ? 'chevron-down' : 'chevron-right'"></span>
            </span>
          </div>
          <div v-if="expandedSections.has('qa-3')" class="accordion-content">

          <div class="importance-grid">
            <div class="importance-item">
              <div class="importance-number">1</div>
              <h3>See Words in Real Context</h3>
              <p>Words change meaning based on context. By seeing all the places a word appears, you understand its <strong>full range of meanings</strong> and how ancient authors actually used it.</p>
            </div>

            <div class="importance-item">
              <div class="importance-number">2</div>
              <h3>Discover Connections Between Works</h3>
              <p>See how the same word or concept appears across different time periods and literary traditions. For example:</p>
              <ul>
                <li>How did Sangam poets use a word?</li>
                <li>How did Thiruvalluvar use the same word years later?</li>
                <li>How did devotional poets use it differently?</li>
              </ul>
            </div>

            <div class="importance-item">
              <div class="importance-number">3</div>
              <h3>Research and Analysis</h3>
              <p>For students writing essays or researchers studying Tamil literature:</p>
              <ul>
                <li>Find all verses with a specific word</li>
                <li>Compare how different authors developed the word usage</li>
                <li>Track the evolution of word usage over time</li>
              </ul>
            </div>

            <div class="importance-item">
              <div class="importance-number">4</div>
              <h3>Deeper Literary Appreciation</h3>
              <p>Instead of reading one work in isolation, you can see the <strong>conversation between authors across centuries</strong>. Tamil literature is like a long conversation — concordance lets you see all the threads.</p>
            </div>
          </div>
            <div class="accordion-close" @click="toggleSection('qa-3')">
              <span class="chevron-icon chevron-up"></span>
            </div>
          </div>
        </section>

        <section class="accordion-section">
          <div class="accordion-header" @click="toggleSection('qa-4')" :class="{ expanded: expandedSections.has('qa-4') }" data-section="qa-4">
            <h2>How Does This Tool Search Across Literary Works?</h2>
            <span class="accordion-icon">
              <span class="chevron-icon" :class="expandedSections.has('qa-4') ? 'chevron-down' : 'chevron-right'"></span>
            </span>
          </div>
          <div v-if="expandedSections.has('qa-4')" class="accordion-content">
            <p>This tool is built like a powerful database that <strong>breaks down every verse</strong> into individual words and remembers where each word came from.</p>

            <div class="process-section">
            <h3>Here's What Happens Behind the Scenes:</h3>

            <div class="process-step">
              <div class="step-number">1</div>
              <div class="step-content">
                <h4>Data Preparation:</h4>
                <p><strong>Acknowledgment:</strong> This searchable concordance is built upon the comprehensive data compiled by <strong>Prof. Dr. P. Pandiyaraja</strong> and available at <a href="http://tamilconcordance.in/" target="_blank" rel="noopener noreferrer" class="external-link">tamilconcordance.in</a>. His meticulous work in creating concordance files for Tamil literary works forms the foundation of this database.</p>

                <p>Every literary work is carefully analyzed using Prof. Pandiyaraja's <strong>word segmentation principles</strong>:</p>
                <ul>
                  <li>Each <strong>verse</strong> is identified (like a stanza in a poem)</li>
                  <li>Each verse is broken into <strong>lines</strong></li>
                  <li>Each line is split into individual <strong>words</strong> following specific Tamil grammar rules</li>
                  <li>Every word's <strong>position and context</strong> is stored in the database</li>
                </ul>

                <p class="segmentation-link">
                  To understand how Tamil words are segmented and why this matters, see the
                  <a href="#" @click.prevent="activeTab = 'principles'" class="tab-link">Word Segmentation Principles →</a>
                </p>
              </div>
            </div>

            <div class="process-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <h4>When You Search:</h4>
                <ul>
                  <li>You type a Tamil word (like "அறம்")</li>
                  <li>The tool instantly searches through <strong>millions of stored words</strong></li>
                  <li>It finds every match across all literary works</li>
                  <li>It shows you the complete verse and context for each occurrence</li>
                </ul>
              </div>
            </div>

            <div class="process-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>Smart Features:</h4>
                <ul>
                  <li><strong>Exact Match:</strong> Find only "அறம்" (not "அறமது" or "அறங்கள்")</li>
                  <li><strong>Partial Match:</strong> Find all words containing "அற" (including அறம், அறன், அறிவு, etc.)</li>
                  <li><strong>Filter by Work:</strong> Search only in Thirukkural or only in Sangam literature</li>
                  <li><strong>Sort by Collection:</strong> See results organized by the chronological order of Tamil literature</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="database-info">
            <h3>What's Inside the Database?</h3>
            <p><strong>The database currently includes works from selected collections:</strong></p>
            <p>Please click on the <strong>Selcet from works</strong> in the Search Filter to see the complete list of works available for search</p>
            <p class="note"><em>Note: The collection continues to grow as more literary works are added to the database.</em></p>
          </div>
            <div class="accordion-close" @click="toggleSection('qa-4')">
              <span class="chevron-icon chevron-up"></span>
            </div>
          </div>
        </section>

        <section class="accordion-section">
          <div class="accordion-header" @click="toggleSection('qa-5')" :class="{ expanded: expandedSections.has('qa-5') }" data-section="qa-5">
            <h2>How to Use This Tool?</h2>
            <span class="accordion-icon">
              <span class="chevron-icon" :class="expandedSections.has('qa-5') ? 'chevron-down' : 'chevron-right'"></span>
            </span>
          </div>
          <div v-if="expandedSections.has('qa-5')" class="accordion-content">

          <div class="student-uses">
            <div class="importance-item">
              <h3>For Tamil Language Learning:</h3>
              <ul>
                <li>See how words are actually used in sentences</li>
                <li>Learn synonyms by finding different words used in similar contexts</li>
                <li>Build vocabulary by exploring word families</li>
              </ul>
            </div>

            <div class="importance-item">
              <h3>For Research Projects:</h3>
              <ul>
                <li>Gather all references to a specific topic</li>
                <li>Analyze patterns across different works</li>
                <li>Support your arguments with textual evidence</li>
              </ul>
            </div>

            <div class="importance-item">
              <h3>For Personal Exploration:</h3>
              <ul>
                <li>Discover beautiful verses you've never read</li>
                <li>Follow your curiosity about specific words or concepts</li>
                <li>Develop a deeper connection to Tamil heritage</li>
              </ul>
            </div>
          </div>
              <p><em>* Note: This tool was developed for personal use and does not gaurantee accadamic level accuracy. *</em>
              </p>
            <div class="accordion-close" @click="toggleSection('qa-5')">
              <span class="chevron-icon chevron-up"></span>
            </div>
          </div>
          
        </section>

        <section class="accordion-section">
          <div class="accordion-header" @click="toggleSection('qa-6')" :class="{ expanded: expandedSections.has('qa-6') }" data-section="qa-6">
            <h2>What other Features are possible?</h2>
            <span class="accordion-icon">
              <span class="chevron-icon" :class="expandedSections.has('qa-6') ? 'chevron-down' : 'chevron-right'"></span>
            </span>
          </div>
          <div v-if="expandedSections.has('qa-6')" class="accordion-content">
          <p>With collaboration from experts across multiple domains, there are exciting possibilities to explore together.</p>

          <div class="features-grid">
            <div class="feature-item">
              <h3>1. Word Root Analysis</h3>
              <ul>
                <li>Show all forms of a word (அறம், அறன், அறமது, அறங்கள்)</li>
                <li>Understand how Tamil grammar changes words</li>
              </ul>
            </div>

            <div class="feature-item">
              <h3>2. Translation Layer</h3>
              <ul>
                <li>Side-by-side Tamil and English translations</li>
                <li>Help non-Tamil speakers explore the literature</li>
              </ul>
            </div>

            <div class="feature-item">
              <h3>3. Thematic Search</h3>
              <ul>
                <li>Search by concept (not just words): "all verses about rain," "all verses about friendship"</li>
                <li>Group related words together automatically</li>
              </ul>
            </div>

            <div class="feature-item">
              <h3>4. Comparative Analysis</h3>
              <ul>
                <li>Compare how two different authors used the same word</li>
                <li>Visualize word usage patterns over time</li>
                <li>See which words appear together frequently</li>
              </ul>
            </div>

            <div class="feature-item">
              <h3>5. Audio Pronunciation</h3>
              <ul>
                <li>Hear classical Tamil pronounced correctly</li>
                <li>Learn proper meter and rhythm for verses</li>
              </ul>
            </div>

            <div class="feature-item">
              <h3>6. Commentary Integration</h3>
              <ul>
                <li>Show traditional scholarly commentaries alongside verses</li>
                <li>Link to explanations by famous scholars</li>
              </ul>
            </div>

            <div class="feature-item">
              <h3>7. Personal Study Tools</h3>
              <ul>
                <li>Save favorite verses</li>
                <li>Create custom collections for study</li>
                <li>Add personal notes and annotations</li>
              </ul>
            </div>

            <div class="feature-item">
              <h3>8. Advanced Filters</h3>
              <ul>
                <li>Search by time period (Sangam era vs. Medieval)</li>
                <li>Search by literary genre (love poetry vs. ethical verses)</li>
                <li>Search by meter/poetic form</li>
              </ul>
            </div>

            <div class="feature-item">
              <h3>9. Visualization Features</h3>
              <ul>
                <li>Word frequency charts</li>
                <li>Networks showing which words appear together</li>
                <li>Timeline of how word usage evolved</li>
              </ul>
            </div>

            <div class="feature-item">
              <h3>10. Educational Features</h3>
              <ul>
                <li>Quiz yourself on word meanings from context</li>
                <li>Interactive lessons on Tamil literary history</li>
                <li>Guided tours through related verses</li>
              </ul>
            </div>
          </div>
            <div class="accordion-close" @click="toggleSection('qa-6')">
              <span class="chevron-icon chevron-up"></span>
            </div>
          </div>
        </section>


        <section class="accordion-section">
          <div class="accordion-header" @click="toggleSection('qa-7')" :class="{ expanded: expandedSections.has('qa-7') }" data-section="qa-7">
            <h2>Final Thoughts</h2>
            <span class="accordion-icon">
              <span class="chevron-icon" :class="expandedSections.has('qa-7') ? 'chevron-down' : 'chevron-right'"></span>
            </span>
          </div>
          <div v-if="expandedSections.has('qa-7')" class="accordion-content">
          <div class="highlight-box">
            <p class="big-text"><strong>A dictionary tells you what words mean.</strong></p>
            <p class="big-text"><strong>A concordance shows you how words LIVE in the real world of literature.</strong></p>
          </div>

          <p>This tool is your gateway to exploring 2,000+ years of Tamil literary genius. Every search is an adventure — you never know what beautiful verse or profound insight you'll discover next.</p>

          <p>Think of it as having a <strong>super-smart librarian</strong> who has read every Tamil book ever written and can instantly show you every page where your favorite word appears. That's the power of concordance!</p>
            <div class="accordion-close" @click="toggleSection('qa-7')">
              <span class="chevron-icon chevron-up"></span>
            </div>
          </div>
        </section>

        <footer class="page-footer">
          <p>If you have questions about how to use this tool or suggestions for new features, <a href="mailto:thamizh.words@gmail.com?subject=Thamizh%20Literature%20Search%20—%20Ideas%20and%20Feedback">we'd love to hear from you</a>. This is a living project designed to help everyone — from students to scholars — explore the beauty of Tamil literature.</p>
          <p><strong>Happy searching!</strong></p>
        </footer>
      </article>

      <!-- Principles Tab Content (complete content from Principles.vue) -->
      <article v-if="activeTab === 'principles'" class="content-section principles-content">
        <header class="page-header">
          <p class="subtitle">Summary of word segmentation principles (சொற்பிரிப்பு நெறிகள்) used in <a href="http://tamilconcordance.in/Principles.html" target="_blank" rel="noopener noreferrer">tamilconcordance.in/Principles.html</a> by Prof. P. Pandiyaraja</p>
        </header>

        <main>
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('principles-intro')" :class="{ expanded: expandedSections.has('principles-intro') }" data-section="principles-intro">
              <h2>சொற்பிரிப்பு நெறிகள்</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('principles-intro') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('principles-intro')" class="accordion-content">
            <p>தமிழ் மொழியில் உள்ள புணர்ச்சி விதிகளால், தமிழ் இலக்கியங்களின் மரபு வழி மூலங்களைப் படித்துப் புரிந்துகொள்வது மிகவும் கடினமாக அமைகின்றது.</p>

            <div class="verse" align="center">
              கூருகிர் ஞமலிக் கொடுந்தா ளேற்றை <br>
              யேழகத் தகரோ டுகளு முன்றிற்<br>
              <span class="commentary">— பட்டினப்பாலை 140, 141</span>
            </div>

            <p>என்ற வரிகளில் பெரும்பாலும் இயல்புப் புணர்ச்சிகளே இருப்பினும், மனத்திற்குள்ளேனும் இந்தப் புணர்ச்சிகளைப் பிரித்த பின்னரே சொற்பொருள் காண்பது எளிதாக அமையும். சொல்லாய்வாளர்கள், குறிப்பாக, சொற்கணக்கீட்டாளர்கள் செய்யும் முதற் பணியே இவ்விலக்கிய வரிகளைத் தனித்தனிச் சொற்களாகப் பிரித்துக்கொள்வது தான்.</p>

            <p>இத்தகைய ஆய்வுகளுக்குத் துணைபுரியும் வண்ணமாக சொற்பிரிப்புப் பதிப்புகள் பல வந்திருக்கின்றன. அவற்றில் முதன்மையானது மர்ரே எஸ்.ராஜம் நிறுவனத்தாரின் பதிப்புக்களே. எனினும், இப்பதிப்புக்களில் உள்ள குறைபாடுகளை முத்துச்சண்முகன், மாதையன் போன்றோர் சுட்டிக் காண்பித்துள்ளனர்.</p>

            <p>சங்க இலக்கியங்களின் சொல்லடைவை உருவாக்கியிருக்கும் Thomas Lehmann and Thomas Malten (ஆசியவியல் நிறுவன வெளியீடு) மற்றும் மாதையன் (தமிழ்ப் பல்கலைக் கழக வெளியீடு) ஆகியோர் தங்கள் நூற்களில், சொற்பிரிப்புக்காகத் தாங்கள் கையாண்டுள்ள நெறிகளைக் குறிப்பிட்டுள்ளனர். ஆனால் இந்த நெறிகள் ஆசிரியருக்குத் தகுந்தவாறு, தேவைக்குத் தகுந்தவாறு வேறுபடலாம்.</p>

            <p>ஒரு குறிப்பிட்ட நூலாசிரியரின் சொல்வளம் (vocabulary) பற்றிய ஆய்வில் சொற்களைப் பிரிப்பதிலும் அல்லது பிரிக்காமல் இருப்பதிலும் பலவித மயக்கங்கள் (ambiguities) வரலாம். 'கண்' என்பதற்குப் பதிலாக 'விழி' என்றும் ஆசிரியர் அழைக்கலாம். எனவே 'கண்', 'விழி' என்ற சொற்களின் எண்ணிக்கை ஆசிரியரின் நடையை விளக்கவும் புரிந்துகொள்ளவும் உதவும்.</p>

            <P>வேற்றுமை உருபுகள், கால இடைநிலைகள், விகுதிகள் போன்றவற்றை வேர்ச்சொல்லோடு சேர்த்துப் பயன்படுத்துவதில் ஆசிரியருக்கு உரிமையில்லை. காட்டாக, கண்ணை, கண்ணோடு, கண்ணால், கண்ணுக்கு என்பவை தனிச்சொற்களாகவே கொள்ளப்பட்டாலும், இவை 'கண்' என்ற ஒரு சொல்லின் இலக்கண வேறுபாடுகளே (grammatical variations).</p>
            <div class="accordion-close" @click="toggleSection('principles-intro')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 1 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-1')" :class="{ expanded: expandedSections.has('neri-1') }" data-section="neri-1">
              <h2>நெறி 1 - புணர்ச்சி விதிகளைக் களைதல்</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-1') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-1')" class="accordion-content">

            <p>தமிழ் இலக்கண விதிகளின்படி சொற்சேர்க்கையின் போது நிகழும் மாற்றங்கள் இலக்கணம் சார்ந்தவை. எனவே, இவற்றை முற்றும் களைவது அவசியம்.</p>

            <div class="example-block">
              <p><strong>எடுத்துக்காட்டு:</strong></p>
              <p><em>குழலினி தியாழினி தென்பதம் மக்கண் மழலைச்சொற் கேளா தவர்</em> — குறள் - புதல்வரைப்பெறுதல் - 6</p>
              <p>பிரிப்பு: குழல் இனிது யாழ் இனிது என்ப தம் மக்கள் மழலை சொல் கேளாதவர்</p>
            </div>

            <p>சொற்கள் புணரும்போது ஏற்படும் 'இயல்பான' மாற்றங்கள் இங்கு களையப்படுகின்றன:</p>

            <div class="example-block">
              <div class="transformation">
                <code>மழலைச் சொல்</code> <span class="arrow">→</span> <code>மழலை சொல்</code>
              </div>
              <div class="transformation">
                <code>பொற்சிலம்பு</code> <span class="arrow">→</span> <code>பொன் சிலம்பு</code>
              </div>
              <div class="transformation">
                <code>கட்புலன்</code> <span class="arrow">→</span> <code>கண் புலன்</code>
              </div>
              <div class="transformation">
                <code>பெருஞ்சிறப்பு</code> <span class="arrow">→</span> <code>பெரும் சிறப்பு</code>
              </div>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-1')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 2 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-2')" :class="{ expanded: expandedSections.has('neri-2') }" data-section="neri-2">
              <h2>நெறி 2 - வேற்றுமை உருபுகள்</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-2') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-2')" class="accordion-content">

            <p>வேற்றுமை உருபுகள் பெயர்ச்சொல்லின் பயன்பாட்டை விளக்கிநிற்பன. எனவே எந்தவொரு வேற்றுமை உருபும் பெயர்ச்சொல்லிலிருந்து பிரிக்கப்படவில்லை.</p>

            <p>சில வேற்றுமை உருபுகள் தனிச் சொற்களாக (free forms) வரும் வாய்ப்புக்களும் உண்டு. இருப்பினும், அவை பெயர்சொற்களோடு சேர்த்தே கொள்ளப்பட்டுள்ளன.</p>

            <div class="example-block">
              <p><strong>எடுத்துக்காட்டு:</strong> 'கண்' என்ற ஏழன் உருபு 'அதன்கண்' என்பது போன்று வருமிடங்களில் 'அதன்-கண்' என்று எடுக்கப்பட்டுள்ளது.</p>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-2')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 3 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-3')" :class="{ expanded: expandedSections.has('neri-3') }" data-section="neri-3">
              <h2>நெறி 3 - கூட்டுச்சொற்கள் (Compound words)</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-3') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-3')" class="accordion-content">

            <h3>அ. நேர்ப்பொருள் கூட்டுச்சொற்கள்</h3>
            <p>சொற்பிரிப்பில் மிகப் பெரும்பாலான சிக்கல்கள் கூட்டுச்சொற்களின் போது தான் ஏற்படுகின்றன. பொதுவாக, சொற்கள் சேரும்போது, அச்சேர்க்கை ஒரு புதிய பொருளை உணர்த்துவதாக அமையும். ஆனால், சில சேர்க்கைகள், அச்சொற்களின் கூட்டுப்பொருளையே உணர்த்திநிற்கும்.</p>

            <div class="word-list">
              <div class="word-item">தலைநாள்</div>
              <div class="word-item">வழிநாள்</div>
              <div class="word-item">முன்நாள்</div>
              <div class="word-item">நாள்மலர்</div>
              <div class="word-item">நாள்மீன்</div>
              <div class="word-item">கோள்மீன்</div>
              <div class="word-item">நாளங்காடி</div>
              <div class="word-item">அல்லங்காடி</div>
              <div class="word-item">முழுமுதல்</div>
              <div class="word-item">கடிமரம்</div>
            </div>

            <h3>ஆ. விரிவுப்பொருள் கூட்டுச்சொற்கள்</h3>
            <p>தாம் உணர்த்தும் நேர்ப்பொருளோடு, கூடுதல் பொருளும் (extended meaning) தருபவை. ஆகுபெயர்கள், அன்மொழித்தொகை போன்றவை இதிலடங்கும்.</p>

            <div class="word-list">
              <div class="word-item">நன்னுதல்</div>
              <div class="word-item">ஒண்ணுதல்</div>
              <div class="word-item">ஆயிழை</div>
              <div class="word-item">ஆர்பதம்</div>
            </div>

            <div class="example-block">
              <p><strong>எடுத்துக்காட்டு:</strong></p>
              <p><em>வாரிருங் கூந்தல் வயங்கிழை ஒழிய</em> — பட் 300</p>
              <p class="commentary">'வயங்கிழை' என்பது ஒளிரும் அணிகலன்களை அணிந்த பெண்ணைக் குறிப்பதால், அன்மொழித்தொகையாகி, ஒரே சொல்லாகும்.</p>

              <p><em>அழல் அவிர் வயங்கு இழை பொலிந்த மேனி</em> — புறம் 222/1</p>
              <p class="commentary">'வயங்கிழை' என்பது ஒளிரும் அணிகலன்களை மட்டும் குறிப்பதால், பிரிக்கப்படும்.</p>
            </div>

            <h3>இ. சிறப்புப்பொருள் கூட்டுச்சொற்கள்</h3>
            <p>தாம் உணர்த்தும் நேர்ப்பொருளுக்கும் கூடுதலான ஒரு பொருளை (special meaning) உணர்த்திநிற்பன.</p>

            <div class="word-list">
              <div class="word-item">விழுப்புண்</div>
              <div class="word-item">முந்நீர்</div>
              <div class="word-item">தன்னையர்</div>
              <div class="word-item">என்னையர்</div>
              <div class="word-item">கார்கோள்</div>
              <div class="word-item">கால்கழுவு</div>
              <div class="word-item">வெண்கொற்றக்குடை</div>
              <div class="word-item">குடைநிழல்</div>
              <div class="word-item">கடிமரம்</div>
              <div class="word-item">கழுநீர்</div>
              <div class="word-item">வெய்துயிர்த்து</div>
              <div class="word-item">வடமலை</div>
              <div class="word-item">வடமீன்</div>
              <div class="word-item">வடமொழி</div>
              <div class="word-item">சுடுமண்</div>
            </div>

            <h3>ஈ. மாறுபொருள் கூட்டுச்சொற்கள்</h3>
            <p>தாம் உணர்த்தும் நேர்ப்பொருளினும் மாறான ஒரு பொருளை (different meaning) உணர்த்திநிற்பன.</p>

            <div class="word-list">
              <div class="word-item">பெரும்பிறிது</div>
              <div class="word-item">கண்படை</div>
              <div class="word-item">கடுங்கண்</div>
              <div class="word-item">வன்கண்</div>
              <div class="word-item">பருவரல்</div>
              <div class="word-item">செவ்வழி (ஒருவகைப் பண்)</div>
            </div>

            <h3>உ. கலைச்சொல்லாகும் கூட்டுச்சொற்கள்</h3>
            <p>ஒரு குறிப்பிட்ட பொருளை மட்டுமே உணர்த்துவதாக வரையறுக்கப்பெறும். தற்காலத்திய வழக்கில், பல்கலைக்கழகம், பேருந்து, கால்நடை, மென்பொருள், திசைவேகம், நீர்வீழ்ச்சி போன்றவை இத்தகையன.</p>

            <div class="example-block">
              <p><strong>'இறுவரை' - cliff என்ற சொல்லுக்குரிய அழகான கலைச்சொல்:</strong></p>
              <p><em>இரும் கல் இகுப்பத்து இறுவரை சேராது</em> — மலை 367</p>
              <p><em>குன்ற இறுவரை கோண்மா இவர்ந்தாங்கு</em> — கலி 86-32</p>
              <p class="commentary">(இறு - அறு, முறி, முடிவு பெறு; வரை - மலை) = செங்குத்தான மலைப்பகுதி</p>
            </div>

            <h3>ஊ. உருமாறிய கூட்டுச்சொற்கள்</h3>
            <p>புணர்ச்சி விதிகளாலோ அல்லது சில மரபுகளாலோ சொற்கள் புணரும்போது ஏற்படும் உருமாற்றம் அச்சொற்களையே 'பெருமளவு' மாற்றினால், அத்தகைய சொற்கள் பிரிக்கப்படவில்லை.</p>

            <div class="word-list">
              <div class="word-item">சீறடி</div>
              <div class="word-item">சீறிதழ்</div>
              <div class="word-item">சீறியாழ்</div>
              <div class="word-item">சீறிலை</div>
              <div class="word-item">சீறுரல்</div>
              <div class="word-item">சேவடி</div>
              <div class="word-item">பச்சூன்</div>
              <div class="word-item">பரியரை</div>
              <div class="word-item">பரேர்</div>
              <div class="word-item">பாசடை</div>
              <div class="word-item">பாசிலை</div>
              <div class="word-item">பேரியாறு</div>
              <div class="word-item">பேரியாழ்</div>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-3')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 4 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-4')" :class="{ expanded: expandedSections.has('neri-4') }" data-section="neri-4">
              <h2>நெறி 4 - துணைவினைகள் (Auxiliary verbs)</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-4') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-4')" class="accordion-content">

            <h3>(அ) வினையாக்கிகள் - verbalisers</h3>
            <p>வினையாக்கிகள் மூன்று வகைப்படும்:</p>

            <ol>
              <li>
                <p>ஒரு பெயர்ச்சொல்லுக்குரிய வினைச்சொல் இல்லாத போது அப்பெயர்ச் சொல்லை வினைச்சொல்லாக ஆக்குவதற்கு வரும் உருபு:</p>
                <div class="example-block">
                  <div class="transformation"><code>நசை</code> <span class="arrow">→</span> <code>நசை_உறு</code></div>
                  <div class="transformation"><code>செவி</code> <span class="arrow">→</span> <code>செவி_உறு</code></div>
                  <div class="transformation"><code>விதுப்பு</code> <span class="arrow">→</span> <code>விதுப்பு_உறு</code></div>
                </div>
              </li>
              <li>வினைச்சொல் வடிவம் இருந்த போதிலும், அதனைப் பெயர்ச்சொல்லாக்கிப் பின்னர் வினையாக்குதல்.</li>
              <li>தன்வினை போல் தோன்றி, பிறவினையாக்கும் (passiviser) வினையாக்கிகள்.</li>
            </ol>

            <h3>'உறு' என்ற சொல்லின் பயன்பாடு</h3>

            <p><strong>1. உரிச்சொல்லாக</strong> - 'மிகுதி' என்ற பொருளில்:</p>
            <div class="example-block">
              <p><em>உறு வினைக்கு அசாவா உலைவு இல் கம்மியன்</em> — நற் 363/4</p>
              <p><em>உறு துயர் அவலமொடு உயிர் செல சாஅய்</em> — ஐங் 313/2</p>
              <p><em>உறு முரண் கடந்த ஆற்றல்</em> — புறம் 135/21</p>
            </div>

            <p><strong>2. தனிவினையாக:</strong></p>
            <div class="example-block">
              <p><em>ஏ உறு மஞ்ஞையின் நடுங்கி இழை நெகிழ்ந்து</em> — முல் 84</p>
              <p><em>புலி உற வெறுத்த தன் வீழ் துணை உள்ளி</em> — மலை 404</p>
              <p class="commentary">பொருள்கள்: அனுபவி (experience), நிலையை அடை, ஏற்படு, ஒன்றினால் பாதிக்கப்படு, படு, தொடு, அடை, பெறு, நிகழ், சம்பவி, போன்றிரு, எதிர்ப்படு, மிகு, பொருந்து, இணை</p>
            </div>

            <p><strong>3. துணைவினையாக:</strong></p>
            <p>பிரிக்கப்படாமல் ஒரே சொல்லாக எடுக்கப்பட்ட சொற்கள்:</p>
            <div class="word-list">
              <div class="word-item">அறிவுறாலின்</div>
              <div class="word-item">இடையுறாஅது</div>
              <div class="word-item">இன்புறு</div>
              <div class="word-item">ஏமுறு</div>
              <div class="word-item">கண்ணுறு</div>
              <div class="word-item">காமுறு</div>
              <div class="word-item">துன்புறு</div>
              <div class="word-item">பண்புறு</div>
              <div class="word-item">முந்துறு</div>
              <div class="word-item">மெய்யுறு</div>
              <div class="word-item">வலியுறுத்தனை</div>
              <div class="word-item">வைகுறு</div>
            </div>

            <h3>(ஆ) 'வர', 'வரு', 'வரும்' - வகைத் துணைவினைகள்</h3>
            <div class="example-block">
              <p><em>அழல் திகழ்ந்து இமைக்கும் அஞ்சுவரு நெடு வேல்</em> — சிறு 94</p>
              <p class="commentary">நச். உரை - அச்சந்தோன்றும் நெடிய வேல்</p>
            </div>

            <p>இவ்வகையில் அடங்குபவை: காண்வர, மேவர, நல்குவர, வெருவர, அமைவர, அசைவர போன்றவையும் இவற்றின் வேற்று வடிவங்களும்.</p>

            <h3>(இ) 'தர', 'தரு', 'தரும்' - வகைத் துணைவினைகள்</h3>
            <div class="example-block">
              <p><em>சிலரொடு திரிதரும் வேந்தன்</em> — நெடு 187</p>
              <p><em>கிளை கவின்று எழுதரு கீழ் நீர் செ அரும்பு</em> — திரு 29</p>
              <p><em>நெடு வரை இழிதரு நீத்தம் சால் அருவி</em> — மலை 554</p>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-4')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 5 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-5')" :class="{ expanded: expandedSections.has('neri-5') }" data-section="neri-5">
              <h2>நெறி 5 - 'அன்ன' என்ற உவம உருபு</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-5') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-5')" class="accordion-content">

            <p>பெயர்ச்சொல்லோடு வரும்போது எளிதில் பிரிக்கக்கூடியது:</p>
            <div class="example-block">
              <p><em>குளப்பு வழி அன்ன கவடு படு பத்தல்</em> — பொரு 4</p>
              <p><em>அரவு உரி அன்ன அறுவை நல்கி</em> — பொரு 83</p>
            </div>

            <p>வினையோடு வரும்போது:</p>
            <div class="example-block">
              <p><em>வளி கிளர்ந்தன்ன செலவினர்</em> — திரு 170</p>
              <p class="commentary">பிரிப்பு: கிளர்ந்து அன்ன (மொழியியலார் நெறி)</p>

              <p><em>குன்று குயின்றன்ன அந்தணர் பள்ளியும்</em> — மது 474</p>
              <p class="commentary">பிரிப்பு: குயின்று அன்ன</p>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-5')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 6 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-6')" :class="{ expanded: expandedSections.has('neri-6') }" data-section="neri-6">
              <h2>நெறி 6 - 'தொறு/தொறும், தோறு/தோறும்' என்ற கட்டுருபன்</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-6') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-6')" class="accordion-content">

            <p>இவை கட்டுருபன்கள் என்ற முறையில், இந்நூலில் பிரிக்கப்படவில்லை. இரு வகை உண்டு:</p>

            <ol>
              <li><strong>வினைச்சொல்லோடு:</strong> எறிதொறும், நுழைதொறும், வருதோறும் — கூட்டுவினையெச்சங்கள்</li>
              <li><strong>பெயர்ச்சொல்லோடு:</strong> ஆலைதொறும், மனைதொறும், வைகல்தொறும், நாள்தொறும் — கூட்டுவினையடைகள்</li>
            </ol>

            <div class="example-block">
              <p>குறியீடு: எறி_தொறும், நுழை_தொறும், வைகல்_தொறும், நாள்_தொறும்</p>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-6')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 7 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-7')" :class="{ expanded: expandedSections.has('neri-7') }" data-section="neri-7">
              <h2>நெறி 7 - அசைச்சொற்கள்</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-7') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-7')" class="accordion-content">

            <p>மன், மதி, கொல், மின் போன்ற சொற்கள் தனித்து வரும்போது வேறு பொருள் தருவதால் இவ்வகை அசைச்சொற்கள் அவற்றிற்கு முன்னர் வரும் சொற்களோடு அடிக்கோட்டுடன் சேர்த்துக் கொள்ளப்படும்.</p>

            <div class="example-block">
              <p><em>செல்க என விடுநள்_மன்_கொல்லோ எல் உமிழ்ந்து</em> — நற் 68/7</p>
              <p><em>நிறுக்கல் ஆற்றினோ நன்று_மன்_தில்ல</em> — குறு 58/2</p>
              <p><em>அறிந்தனை ஒழுகு_மதி அறனும்_ஆர் அதுவே</em> — ஐங் 44/4</p>
              <p><em>உண்_மின் கள்ளே அடு_மின் சோறே</em> — பதி 18/1</p>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-7')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 8 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-8')" :class="{ expanded: expandedSections.has('neri-8') }" data-section="neri-8">
              <h2>நெறி 8 - 'என்', 'என' என்னும் சொற்கள்</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-8') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-8')" class="accordion-content">

            <p>விரைவுக்குறிப்பு, ஒலிக்குறிப்பு போன்ற சொற்களோடு வருமிடங்களில் பிரிக்கப்படவில்லை:</p>

            <div class="example-block">
              <p><em>இழுமென இழிதரும் அருவி</em> — திரு 316</p>
              <p><em>கதுமென கரைந்து வம் என கூஉய்</em> — பொரு 101</p>
              <p><em>கல்லென் சுற்றமொடு கால் கிளர்ந்து திரிதரும்</em> — பெரும் 21</p>
              <p><em>புல்லென் யாக்கை புலவு வாய் பாண</em> — பெரும் 22</p>
              <p><em>நள்ளென் யாமத்தும் பள்ளி கொள்ளான்</em> — நெடு 186</p>
            </div>

            <p>தனிச் சொல்லுக்குப் பின்னரோ அல்லது உவம உருபாகவோ வருமிடங்களில் பிரிக்கப்பட்டுள்ளன:</p>

            <div class="example-block">
              <p><em>இருவேம் ஆய்ந்த மன்றல் இது என</em> — குறி 21</p>
              <p><em>அணங்கு என உருத்த சுணங்கு அணி ஆகத்து</em> — பொரு 35</p>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-8')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 9 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-9')" :class="{ expanded: expandedSections.has('neri-9') }" data-section="neri-9">
              <h2>நெறி 9 - 'உழி' என்னும் சொல்</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-9') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-9')" class="accordion-content">

            <p>'உழி' என்ற சொல் அலைந்து திரி என்ற தனி வினையாகவோ, இடம், பக்கம் என்ற தனிப் பெயராகவோ வரும்போது சிக்கலில்லை. ஆனால் அச்சொல் (அந்த) நேரத்தில் என்ற பொருளில் ஒரு வினையுடனோ அல்லது ஒரு பெயரின் ஏழன் உருபாகவோ வரும்போது அதனைக் கணக்கிடுவதில் சிக்கலுண்டு.</p>

            <div class="example-block">
              <p><em>செல்வுழி செல்வுழி மெய் நிழல் போல</em> — அகம் 49/15</p>
              <p class="commentary">'செல்வுழி' = 'செல்லும் இடம்'</p>
              <p>குறியீடு: செல்வு_உழி, கேட்பு_உழி</p>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-9')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 10 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-10')" :class="{ expanded: expandedSections.has('neri-10') }" data-section="neri-10">
              <h2>நெறி 10 - அடுக்குத்தொடர் அல்லது சொல் இரட்டிப்பு (Repetitions)</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-10') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-10')" class="accordion-content">

            <p>ஒரு சொல் அடுத்தடுத்து இரண்டு முறை வரும்போது அச்சொல்லின் பொருளில் சற்றேனும் மாறுதல் ஏற்படும். எனவே இரட்டையாக வரும் அச்சொல் பொருள் அடிப்படையில் ஒரே சொல்லாகவே எடுத்துக்கொள்ளப்படவேண்டும்.</p>

            <div class="example-block">
              <p><em>ஊரூர் கொண்ட சீர் கெழு விழவினும்</em> — திரு 220</p>
              <p><em>வைகல்வைகல் கை கவி பருகி</em> — பொரு 158</p>
              <p><em>வழிவழி சிறக்க நின் வலம் படு கொற்றம்</em> — மது 194</p>
              <p><em>கொளக்கொள குறையாது தரத்தர மிகாது</em> — மது 426</p>
              <p><em>பொன் போல் பீரமொடு புதல்புதல் மலர</em> — நெடு 14</p>
              <p class="commentary">'புதல்புதல் மலர' = புதல்தொறும் (மலர)</p>
            </div>

            <p>மேலும் சிக்கலான வழக்காறுகள்:</p>
            <div class="example-block">
              <p><em>துறைதுறைதோறும் பொறை உயிர்த்து ஒழுகி</em> — பொரு 239</p>
              <p><em>முயங்குதொறும்முயங்குதொறும் உயங்க முகந்து கொண்டு</em> — அகம் 328/10</p>
              <p class="commentary">இவை தனித்தனிச் சொற்களாகவே கொள்ளப்பட்டுள்ளன.</p>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-10')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- நெறி 11 -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('neri-11')" :class="{ expanded: expandedSections.has('neri-11') }" data-section="neri-11">
              <h2>நெறி 11 - 'ஆங்கு' எனும் சொல்</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('neri-11') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('neri-11')" class="accordion-content">

            <p><strong>வினை அடையாக</strong> (அந்த இடத்தில், அந்த நேரத்தில்) வரும்போது தனிச்சொல்:</p>
            <div class="example-block">
              <p><em>ஆங்கு வியம் கொண்மின் அது அதன் பண்பே</em> — மலை 427</p>
              <p><em>ஆங்கு அவர் வதி வயின் நீங்கப்படினே</em> — குறு 395/8</p>
            </div>

            <p><strong>உவம உருபு போல்</strong> வரும்போதும் தனிச்சொல்:</p>
            <div class="example-block">
              <p>கண்டாங்கு, படர்ந்தாங்கு, தூங்கியாங்கு → கண்டு ஆங்கு, படர்ந்து ஆங்கு, தூங்கி ஆங்கு</p>
            </div>

            <p><strong>பெயரெச்ச விகுதியாக</strong> (அவ்வாறு, அப்படி) வரும்போது பிரிக்கப்படவில்லை:</p>
            <div class="example-block">
              <p><em>வேண்டுநர் வேண்டியாங்கு எய்தினர் வழிபட</em> — திரு 248</p>
              <p><em>பெறல் அரும் கலத்தில் பெட்டாங்கு உண்க என</em> — பொரு 156</p>
              <p class="commentary">வேண்டியவாறு/வேண்டியபடி, விரும்பியவாறு/விரும்பியபடி</p>
            </div>
            <div class="accordion-close" @click="toggleSection('neri-11')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- சொற்குறியீட்டு முறை -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('notation')" :class="{ expanded: expandedSections.has('notation') }" data-section="notation">
              <h2>சொற்குறியீட்டு முறை</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('notation') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('notation')" class="accordion-content">

            <h3>1. கூட்டுச்சொற்கள்</h3>
            <p>மயிர்குறைகருவி, சில்பதஉணவு, அறுகால்பறவை போன்ற சொற்கள் ஒன்றுக்கு மேற்பட்ட சொற்களைக்கொண்டு உருவாக்கப்பட்ட தனிச்சொற்கள். இவற்றின் உறுப்புச் சொற்கள் கீழ்க்கோட்டால் (underscore '_') இணைக்கப்பட்டுள்ளன.</p>

            <div class="example-block">
              <p><strong>எடுத்துக்காட்டு:</strong></p>
              <p><code>மயிர்_குறை_கருவி</code>, <code>சில்_பத_உணவு</code>, <code>அறு_கால்_பறவை</code></p>
              <p class="commentary">மயிர்_குறை_கருவி என்ற சொல் வழங்குமிடம், மயிர், குறை, கருவி, மயிர்_குறை_கருவி ஆகிய நான்கு சொற்களின் வழங்கிடங்களிலும் காணப்படும்.</p>
            </div>

            <h3>2. கட்டுருபன் கொண்ட சொற்கள்</h3>
            <p>கட்டுருபன்கள் '-' என்ற சிறுகோட்டால் இணைக்கப்பட்டுள்ளன.</p>

            <div class="example-block">
              <p><strong>எடுத்துக்காட்டு:</strong></p>
              <p><code>ஆற்றலர்-மன்னே</code>, <code>நாள்-தொறும்</code>, <code>விடுநள்-மன்-கொல்லோ</code></p>
            </div>
            <div class="accordion-close" @click="toggleSection('notation')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>

          <!-- பார்வை (References) -->
          <section class="accordion-section">
            <div class="accordion-header" @click="toggleSection('references')" :class="{ expanded: expandedSections.has('references') }" data-section="references">
              <h2>பார்வை நூல்கள்</h2>
              <span class="accordion-icon">
                <span class="chevron-icon" :class="expandedSections.has('references') ? 'chevron-down' : 'chevron-right'"></span>
              </span>
            </div>
            <div v-if="expandedSections.has('references')" class="accordion-content">

            <ol>
              <li><strong>சங்க இலக்கியச் சொல்லடைவு</strong> — முனைவர் பெ.மாதையன், தமிழ்ப் பல்கலைக்கழகம், தஞ்சாவூர் - 2007</li>
              <li><strong>A Word Index for Cankam Literature</strong> — Thomas Lehmann and Thomas Malten, Institute of Asian Studies, Chennai, Second Edition 2007 (முன்னுரை - முனைவர்.முத்துச்சண்முகன்)</li>
              <li><strong>சங்க இலக்கியங்கள்</strong> — பன்னிரண்டு பாகங்கள், பதிப்பு - ஆசிரியர் குழு, மர்ரே எஸ்.ராஜம் பதிப்பு, வெளியிட்டோர் - நியூ செஞ்சுரி புக் ஹவுஸ் பிரைவேட் லிமிடெட், சென்னை, இரண்டாம் பதிப்பு - 1981</li>
            </ol>
            <div class="accordion-close" @click="toggleSection('references')">
              <span class="chevron-icon chevron-up"></span>
            </div>
            </div>
          </section>
        </main>

        <footer class="principles-footer">
          <p class="footer-source">Source: <a href="http://tamilconcordance.in/Principles.html" target="_blank" rel="noopener noreferrer">tamilconcordance.in/Principles.html</a></p>
        </footer>
      </article>
    </div>
  </div>
</template>

<script>
import { ref, nextTick, watch, onMounted } from 'vue'

export default {
  name: 'AboutConcordance',
  props: {
    initialTab: {
      type: String,
      default: 'qa'
    }
  },
  setup(props) {
    const activeTab = ref(props.initialTab)
    const expandedSections = ref(new Set())

    const toggleSection = (sectionId) => {
      const newSet = new Set(expandedSections.value)
      const wasExpanded = newSet.has(sectionId)

      if (wasExpanded) {
        newSet.delete(sectionId)
        expandedSections.value = newSet

        // Scroll to the accordion header after collapse
        nextTick(() => {
          const header = document.querySelector(`[data-section="${sectionId}"]`)
          if (header) {
            header.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
          }
        })
      } else {
        newSet.add(sectionId)
        expandedSections.value = newSet
      }
    }

    // Scroll to top when component mounts
    onMounted(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    })

    // Scroll to top when tab changes
    watch(activeTab, () => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    })

    return {
      activeTab,
      expandedSections,
      toggleSection
    }
  }
}
</script>

<style scoped>
.about-page {
  padding: 2rem 1rem;
  max-width: 1000px;
  margin: 0 auto;
}

.about-container {
  background: var(--surface);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Tab Navigation */
.tab-nav {
  display: flex;
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
  border-bottom: 2px solid var(--border-color);
}

.tab-button {
  flex: 1;
  padding: 1rem 1.5rem;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.tab-button:hover {
  background: rgba(211, 47, 47, 0.05);
  color: var(--primary-color);
}

.tab-button.active {
  background: var(--surface);
  color: var(--primary-color);
  border-bottom: 3px solid var(--primary-color);
}

/* Content Sections */
.content-section {
  padding: 0 2rem 2rem 2rem;
  line-height: 1.7;
}

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

.subtitle {
  margin: 0.5rem 0;
  color: var(--text-secondary);
  font-size: 1.1rem;
  font-style: italic;
}

/* Q&A Sections */
.qa-section {
  margin: 2rem 0;
  padding: 1.5rem 0;
  border-bottom: 1px solid #e0e0e0;
}

.qa-section:last-of-type {
  border-bottom: none;
}

.qa-section h2 {
  font-size: 1.6rem;
  color: var(--primary-color);
  margin: 0 0 1rem 0;
  font-weight: 700;
  border-left: 4px solid var(--primary-color);
  padding-left: 1rem;
}

/* Accordion Styles */
.accordion-section {
  margin: 0;
  border: none;
  border-bottom: 1px solid var(--border-color);
  overflow: hidden;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.accordion-section:hover .accordion-header {
  border-left: 3px solid #c17a3a;
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: transparent;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.accordion-header:hover {
  background: linear-gradient(135deg, #fdf3ea 0%, #f5e6d3 100%);
}

.accordion-header.expanded {
  background: linear-gradient(135deg, var(--primary-color) 0%, #c62828 100%);
  border-left: 3px solid var(--primary-color);
}

.accordion-header.expanded h2 {
  color: white;
}

.accordion-header h2 {
  font-size: 1.15rem;
  color: var(--primary-color);
  margin: 0;
  font-weight: 700;
  flex: 1;
  transition: color 0.3s ease;
}

.accordion-icon {
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 1rem;
  transition: all 0.3s ease;
}

.accordion-icon .chevron-icon {
  width: 10px;
  height: 10px;
  border-color: var(--primary-color);
}

.accordion-header.expanded .accordion-icon .chevron-icon {
  border-color: white;
}

.accordion-content {
  padding: 1rem 1.5rem;
  background: white;
  animation: slideDown 0.3s ease;
}

.accordion-content p {
  line-height: 1.6;
  margin: 0.75rem 0;
}

.accordion-close {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0.5rem 1.5rem;
  margin-top: 1rem;
  border-top: 1px solid var(--border-color);
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
  color: var(--primary-color);
}

.accordion-close .chevron-icon {
  width: 10px;
  height: 10px;
  border-color: var(--primary-color);
}

.accordion-close:hover .chevron-icon {
  border-color: #c17a3a;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.qa-section h3 {
  font-size: 1.2rem;
  color: var(--secondary-color);
  margin: 1.5rem 0 1rem;
  font-weight: 600;
}

.qa-section p {
  margin: 1rem 0;
  color: var(--text-primary);
  font-size: 1.05rem;
  text-align: justify;
}

/* Example Box */
.example-box {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border: 2px solid var(--secondary-color);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin: 1rem 0;
}

/* Comparison */
.comparison {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.comparison-item {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid var(--border-color);
}

.comparison-item strong {
  color: var(--primary-color);
  display: block;
  margin-bottom: 0.5rem;
}

/* Comparison Table */
.comparison-table {
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  overflow: hidden;
  margin: 1rem 0;
}

.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
}

.header-row {
  background: linear-gradient(135deg, var(--primary-color) 0%, #c62828 100%);
  color: white;
  font-weight: 700;
}

.table-cell {
  padding: 0.6rem 1rem;
  border-bottom: 1px solid var(--border-color);
  line-height: 1.5;
  font-size: 1.0rem
}

.table-row:last-child .table-cell {
  border-bottom: none;
}

.table-row:not(.header-row):nth-child(even) {
  background: #f9f9f9;
}

/* Table Icons */
.table-cell .icon {
  display: inline-block;
  margin-right: 0.5rem;
  font-size: 1.2rem;
}

/* Example Content */
.example-content {
  margin-top: 1rem;
}

.example-content h4 {
  color: var(--primary-color);
  margin: 1.5rem 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.example-content h4:first-child {
  margin-top: 0.5rem;
}

.dictionary-result,
.concordance-result {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin: 0 0 1rem 0;
  border: 2px solid var(--border-color);
  font-size: 1.0rem;
}

.definition {
  font-style: italic;
  color: var(--text-secondary);
  padding: 0.5rem 1rem;
  background: #f5f5f5;
  border-left: 3px solid var(--secondary-color);
}

.concordance-result ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.concordance-result li {
  margin: 0.5rem 0;
  color: var(--text-primary);
}

.key-difference {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-top: 1rem;
  border-left: 4px solid #ff9800;
  font-size: 1.05rem;
}

/* Importance Grid */
.importance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.importance-item {
  background: white;
  padding: 1rem 1.25rem;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  position: relative;
  padding-top: 2.5rem;
}

.importance-number {
  position: absolute;
  top: -15px;
  left: 20px;
  background: var(--primary-color);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
  box-shadow: 0 2px 6px rgba(211, 47, 47, 0.3);
}

.importance-item h3 {
  color: var(--secondary-color);
  margin: 0 0 0.75rem 0;
  font-size: 1.15rem;
}

.importance-item p,
.importance-item ul {
  margin: 0.75rem 0;
  font-size: 1rem;
}

.importance-item ul {
  padding-left: 1.5rem;
}

.importance-item li {
  margin: 0.5rem 0;
}

/* Process Section */
.process-section {
  margin: 1rem 0;
}

.process-step {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
  background: white;
  padding: 1rem 1.25rem;
  border-radius: 10px;
  border: 2px solid var(--border-color);
}

.step-number {
  flex-shrink: 0;
  width: 50px;
  height: 50px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.5rem;
  box-shadow: 0 2px 6px rgba(211, 47, 47, 0.3);
}

.step-content {
  flex: 1;
}

.step-content h4 {
  margin: 0 0 0.75rem 0;
  color: var(--primary-color);
  font-size: 1.15rem;
}

.step-content ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.step-content li {
  margin: 0.5rem 0;
}

.segmentation-link {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border-left: 3px solid var(--primary-color);
  border-radius: 6px;
  font-size: 1rem;
}

.external-link,
.tab-link {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 2px dotted rgba(25, 118, 210, 0.3);
  transition: all 0.2s ease;
}

.external-link:hover,
.tab-link:hover {
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

/* Database Info */
.database-info {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  padding: 1.5rem;
  border-radius: 10px;
  margin: 1.5rem 0;
  border: 2px solid #4caf50;
}

.database-info h3 {
  color: #2e7d32;
  margin: 0 0 1rem 0;
}

.content-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.category {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
}

.category h4 {
  color: var(--primary-color);
  margin: 0 0 0.75rem 0;
}

.category ul {
  margin: 0;
  padding-left: 1.5rem;
}

.category li {
  margin: 0.5rem 0;
}

/* Features Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.feature-item {
  background: white;
  padding: 1rem 1.25rem;
  border: 2px solid var(--border-color);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.feature-item:hover {
  border-color: var(--primary-color);
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(211, 47, 47, 0.15);
}

.feature-item h3 {
  color: var(--primary-color);
  margin: 0 0 0.75rem 0;
  font-size: 1.1rem;
}

.feature-item ul {
  margin: 0;
  padding-left: 1.5rem;
}

.feature-item li {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

/* Student Uses */
.student-uses {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.use-case {
  background: linear-gradient(135deg, #fff5f5 0%, #fce4ec 100%);
  padding: 1rem 1.25rem;
  border-radius: 10px;
  border: 2px solid #f48fb1;
}

.use-case h3 {
  color: var(--primary-color);
  margin: 0 0 0.75rem 0;
  font-size: 1.15rem;
}

.use-case ul {
  margin: 0;
  padding-left: 1.5rem;
}

.use-case li {
  margin: 0.5rem 0;
}

/* Final Thoughts */
.final-thoughts {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  padding: 2rem;
  border-radius: 12px;
  border: 3px solid var(--primary-color);
}

.highlight-box {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  text-align: center;
  margin: 1rem 0;
  border: 2px solid var(--primary-color);
}

.big-text {
  font-size: 1.2rem;
  margin: 0.75rem 0;
  color: var(--primary-color);
}

/* Footer */
.page-footer {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid var(--border-color);
  text-align: center;
  color: var(--text-secondary);
  font-size: .9rem;
}

.page-footer p {
  margin: 0.75rem 0;
}

/* Principles Content Styles (from Principles.vue) */
.principles-content {
  /* Copy styles from Principles.vue */
}

.principles-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--primary-color);
}

.principles-header h1 {
  font-family: var(--tamil-font), var(--english-font);
  font-size: 1.8rem;
  margin: 0 0 0.5rem 0;
  color: var(--primary-color);
  font-weight: 700;
}

.lead {
  margin: 0.5rem 0;
  color: var(--text-secondary);
  font-size: 1rem;
}

.source-link {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.source-link a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px dotted rgba(25, 118, 210, 0.25);
}

.source-link a:hover {
  border-bottom: 1px solid var(--secondary-color);
}

.verse {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border-left: 4px solid var(--secondary-color);
  padding: 1rem 1.5rem;
  margin: 1.5rem 0;
  font-style: italic;
  border-radius: 8px;
  font-family: var(--tamil-font), var(--english-font);
}

.commentary {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-left: 1.5rem;
  font-style: italic;
}

.reference-section {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border: 2px solid var(--primary-color);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 2rem;
}

.reference-section h2 {
  margin-top: 0;
  border-left: none;
  padding-left: 0;
  text-align: center;
}

.principles-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 2px solid var(--border-color);
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.footer-source {
  font-size: 0.9rem;
  margin-top: 0.75rem;
}

.footer-source a {
  color: var(--secondary-color);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px dotted rgba(25, 118, 210, 0.25);
}

.footer-source a:hover {
  border-bottom: 1px solid var(--secondary-color);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .about-page {
    padding: 1rem 0.5rem;
  }

  .content-section {
    padding: 0 1rem 1.5rem 1rem;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .accordion-header h2 {
    font-size: 1rem;
  }

  .accordion-content p,
  .accordion-content li {
    font-size: 1.05rem;
    line-height: 1.6;
  }

  .comparison {
    grid-template-columns: 1fr;
  }

  .table-row {
    grid-template-columns: 1fr;
  }

  .table-cell {
    padding: 0.6rem 0.75rem;
    font-size: 0.95rem;
  }

  .importance-grid,
  .features-grid,
  .student-uses {
    grid-template-columns: 1fr;
  }

  .process-step {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .step-content {
    text-align: left;
  }

  .step-content p,
  .step-content li {
    font-size: 1.05rem;
  }

  .tab-button {
    font-size: 0.9rem;
    padding: 0.75rem 1rem;
  }

  .content-categories {
    grid-template-columns: 1fr;
  }
}
</style>
