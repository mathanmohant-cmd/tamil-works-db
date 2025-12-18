-- ============================================================================
-- COMPLETE DATABASE SETUP
-- This file combines schema.sql and sample_word_data.sql in the correct order
-- Run this file to set up the complete database with all sample data
-- ============================================================================

-- Usage:
-- psql $NEON_DB_URL -f sql/complete_setup.sql

-- ============================================================================
-- STEP 1: CREATE TABLES (from schema.sql)
-- ============================================================================

-- Literary works table
CREATE TABLE works (
    work_id INTEGER PRIMARY KEY,
    work_name VARCHAR(200) NOT NULL,
    work_name_tamil VARCHAR(200) NOT NULL,
    period VARCHAR(100),
    author VARCHAR(200),
    author_tamil VARCHAR(200),
    description TEXT,
    traditional_sort_order INTEGER,  -- Traditional chronological ordering of Tamil literature
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hierarchical sections table (flexible structure for all levels)
CREATE TABLE sections (
    section_id INTEGER PRIMARY KEY,
    work_id INTEGER NOT NULL,
    parent_section_id INTEGER,  -- NULL for top-level sections
    level_type VARCHAR(50) NOT NULL,  -- e.g., 'paal', 'kandam', 'adhikaram', 'padalam'
    level_type_tamil VARCHAR(50),
    section_number INTEGER NOT NULL,
    section_name VARCHAR(200),
    section_name_tamil VARCHAR(200),
    description TEXT,
    sort_order INTEGER NOT NULL,  -- For maintaining order within same level
    FOREIGN KEY (work_id) REFERENCES works(work_id),
    FOREIGN KEY (parent_section_id) REFERENCES sections(section_id),
    UNIQUE (work_id, parent_section_id, level_type, section_number)
);

-- Create index for hierarchical queries
CREATE INDEX idx_sections_parent ON sections(parent_section_id);
CREATE INDEX idx_sections_work ON sections(work_id);

-- Verses/Poems/Sutras table (the atomic textual unit before lines)
CREATE TABLE verses (
    verse_id INTEGER PRIMARY KEY,
    work_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,  -- Links to the most specific section (e.g., adhikaram)
    verse_number INTEGER NOT NULL,
    verse_type VARCHAR(50),  -- e.g., 'kural', 'venba', 'kalippa', 'noorpa', 'poem'
    verse_type_tamil VARCHAR(50),
    meter VARCHAR(100),  -- Poetic meter if applicable
    total_lines INTEGER NOT NULL,
    sort_order INTEGER NOT NULL,
    FOREIGN KEY (work_id) REFERENCES works(work_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    UNIQUE (work_id, section_id, verse_number)
);

CREATE INDEX idx_verses_section ON verses(section_id);
CREATE INDEX idx_verses_work ON verses(work_id);

-- Lines table
CREATE TABLE lines (
    line_id INTEGER PRIMARY KEY,
    verse_id INTEGER NOT NULL,
    line_number INTEGER NOT NULL,  -- Line number within the verse (1, 2, 3, 4...)
    line_text TEXT NOT NULL,
    line_text_transliteration TEXT,  -- Roman transliteration
    line_text_translation TEXT,  -- English/other language translation
    FOREIGN KEY (verse_id) REFERENCES verses(verse_id),
    UNIQUE (verse_id, line_number)
);

CREATE INDEX idx_lines_verse ON lines(verse_id);

-- Words table (every word with its position)
CREATE TABLE words (
    word_id INTEGER PRIMARY KEY,
    line_id INTEGER NOT NULL,
    word_position INTEGER NOT NULL,  -- Position in the line (1, 2, 3...)
    word_text VARCHAR(200) NOT NULL,
    word_text_transliteration VARCHAR(200),
    word_root VARCHAR(200),  -- Root/base form of the word
    word_type VARCHAR(50),  -- noun, verb, adjective, etc.
    sandhi_split VARCHAR(500),  -- If word is result of sandhi, show components
    meaning TEXT,
    FOREIGN KEY (line_id) REFERENCES lines(line_id),
    UNIQUE (line_id, word_position)
);

CREATE INDEX idx_words_line ON words(line_id);
CREATE INDEX idx_words_text ON words(word_text);
CREATE INDEX idx_words_root ON words(word_root);

-- Commentary/annotations on verses
CREATE TABLE commentaries (
    commentary_id INTEGER PRIMARY KEY,
    verse_id INTEGER NOT NULL,
    commentator VARCHAR(200),
    commentator_tamil VARCHAR(200),
    commentary_text TEXT NOT NULL,
    commentary_period VARCHAR(100),
    FOREIGN KEY (verse_id) REFERENCES verses(verse_id)
);

-- Cross-references between verses
CREATE TABLE cross_references (
    reference_id INTEGER PRIMARY KEY,
    source_verse_id INTEGER NOT NULL,
    target_verse_id INTEGER NOT NULL,
    reference_type VARCHAR(50),  -- 'parallel', 'quote', 'allusion', etc.
    notes TEXT,
    FOREIGN KEY (source_verse_id) REFERENCES verses(verse_id),
    FOREIGN KEY (target_verse_id) REFERENCES verses(verse_id)
);

-- ============================================================================
-- STEP 2: CREATE VIEWS (from schema.sql)
-- ============================================================================

-- Complete hierarchical path for each verse
CREATE VIEW verse_hierarchy AS
WITH RECURSIVE section_path AS (
    SELECT
        section_id,
        work_id,
        parent_section_id,
        level_type,
        section_name,
        section_name_tamil,
        section_number,
        sort_order,
        1 as depth,
        section_id::TEXT as path,
        level_type || ':' || section_name as path_names,
        COALESCE(level_type_tamil, level_type) || ':' || COALESCE(section_name_tamil, section_name) as path_names_tamil
    FROM sections
    WHERE parent_section_id IS NULL

    UNION ALL

    SELECT
        s.section_id,
        s.work_id,
        s.parent_section_id,
        s.level_type,
        s.section_name,
        s.section_name_tamil,
        s.section_number,
        s.sort_order,
        sp.depth + 1,
        sp.path || '/' || s.section_id::TEXT,
        sp.path_names || ' > ' || s.level_type || ':' || s.section_name,
        sp.path_names_tamil || ' > ' || COALESCE(s.level_type_tamil, s.level_type) || ':' || COALESCE(s.section_name_tamil, s.section_name)
    FROM sections s
    INNER JOIN section_path sp ON s.parent_section_id = sp.section_id
)
SELECT
    v.verse_id,
    v.verse_number,
    v.verse_type,
    w.work_name,
    w.work_name_tamil,
    sp.path_names as hierarchy_path,
    sp.path_names_tamil as hierarchy_path_tamil,
    sp.depth as hierarchy_depth
FROM verses v
INNER JOIN works w ON v.work_id = w.work_id
INNER JOIN section_path sp ON v.section_id = sp.section_id;

-- Complete word information with full context
CREATE VIEW word_details AS
SELECT
    w.word_id,
    w.word_text,
    w.word_text_transliteration,
    w.word_root,
    w.word_type,
    w.word_position,
    w.sandhi_split,
    w.meaning,
    l.line_id,
    l.line_number,
    l.line_text,
    v.verse_id,
    v.verse_number,
    v.verse_type,
    vh.work_name,
    vh.work_name_tamil,
    vh.hierarchy_path,
    vh.hierarchy_path_tamil
FROM words w
INNER JOIN lines l ON w.line_id = l.line_id
INNER JOIN verses v ON l.verse_id = v.verse_id
INNER JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id;

-- ============================================================================
-- STEP 3: INSERT WORKS DATA (from schema.sql)
-- This MUST come before any other data inserts due to foreign key constraints
-- ============================================================================

INSERT INTO works (work_id, work_name, work_name_tamil, period, author, author_tamil, description, traditional_sort_order) VALUES
(1, 'Tolkappiyam', 'தொல்காப்பியம்', '3rd century BCE - 5th century CE', 'Tolkappiyar', 'தொல்காப்பியர்', 'Ancient Tamil grammar and poetics text', 1),
(2, 'Sangam Literature', 'சங்க இலக்கியம்', '300 BCE - 300 CE', 'Various', 'பல்வேறு புலவர்கள்', 'Collection of classical Tamil poetry', 2),
(3, 'Thirukkural', 'திருக்குறள்', '4th - 5th century CE', 'Thiruvalluvar', 'திருவள்ளுவர்', 'Classic Tamil text on ethics, politics, and love', 3),
(4, 'Silapathikaram', 'சிலப்பதிகாரம்', '5th - 6th century CE', 'Ilango Adigal', 'இளங்கோ அடிகள்', 'Epic tale of Kannagi and Kovalan', 4),
(5, 'Kambaramayanam', 'கம்பராமாயணம்', '12th century CE', 'Kambar', 'கம்பர்', 'Tamil version of the Ramayana', 5);

-- ============================================================================
-- STEP 4: INSERT BASIC SAMPLE DATA (from schema.sql)
-- ============================================================================

-- Thirukkural structure (Level 1: Paal)
INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order) VALUES
(1, 3, NULL, 'paal', 'பால்', 1, 'Aram', 'அறத்துப்பால்', 1),
(2, 3, NULL, 'paal', 'பால்', 2, 'Porul', 'பொருட்பால்', 2),
(3, 3, NULL, 'paal', 'பால்', 3, 'Inbam', 'காமத்துப்பால்', 3);

-- Level 2: Iyal (example under Aram)
INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order) VALUES
(4, 3, 1, 'iyal', 'இயல்', 1, 'Pāyiram', 'பாயிரம்', 1),
(5, 3, 1, 'iyal', 'இயல்', 2, 'Īlaram', 'இல்லறவியல்', 2);

-- Level 3: Adhikaram (example under Pāyiram)
INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order) VALUES
(6, 3, 4, 'adhikaram', 'அதிகாரம்', 1, 'Kadavul Vazhthu', 'கடவுள் வாழ்த்து', 1),
(7, 3, 4, 'adhikaram', 'அதிகாரம்', 2, 'Vaan Sirappu', 'வான் சிறப்பு', 2);

-- Example verse (Kural 1)
INSERT INTO verses (verse_id, work_id, section_id, verse_number, verse_type, verse_type_tamil, total_lines, sort_order) VALUES
(1, 3, 6, 1, 'kural', 'குறள்', 2, 1);

-- Lines for Kural 1
INSERT INTO lines (line_id, verse_id, line_number, line_text, line_text_transliteration, line_text_translation) VALUES
(1, 1, 1, 'அகர முதல எழுத்தெல்லாம் ஆதி', 'Akara mudala ezhutthellām ādhi', 'As the letter A is first of all letters'),
(2, 1, 2, 'பகவன் முதற்றே உலகு', 'Bhagavan mudhatre ulagu', 'So God is first of all the world');

-- Words for Line 1 of Kural 1
INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type) VALUES
(1, 1, 1, 'அகர', 'akara', 'அ', 'noun'),
(2, 1, 2, 'முதல', 'mudala', 'முதல்', 'adjective'),
(3, 1, 3, 'எழுத்தெல்லாம்', 'ezhutthellām', 'எழுத்து + எல்லாம்', 'noun'),
(4, 1, 4, 'ஆதி', 'ādhi', 'ஆதி', 'noun');

-- Words for Line 2 of Kural 1
INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type) VALUES
(5, 2, 1, 'பகவன்', 'bhagavan', 'பகவன்', 'noun'),
(6, 2, 2, 'முதற்றே', 'mudhatre', 'முதல்', 'adverb'),
(7, 2, 3, 'உலகு', 'ulagu', 'உலகு', 'noun');

-- Kambaramayanam structure (Level 1: Kandam)
INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order) VALUES
(100, 5, NULL, 'kandam', 'காண்டம்', 1, 'Bala Kandam', 'பால காண்டம்', 1),
(101, 5, NULL, 'kandam', 'காண்டம்', 2, 'Ayodhya Kandam', 'அயோத்திய காண்டம்', 2);

-- Level 2: Padalam (example under Bala Kandam)
INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order) VALUES
(102, 5, 100, 'padalam', 'படலம்', 1, 'Nagar Padalam', 'நகர படலம்', 1);

-- ============================================================================
-- STEP 5: INSERT EXTENDED SAMPLE DATA (from sample_word_data.sql)
-- ============================================================================

-- Add Kural 2 (in same adhikaram as Kural 1)
INSERT INTO verses (verse_id, work_id, section_id, verse_number, verse_type, verse_type_tamil, total_lines, sort_order) VALUES
(2, 3, 6, 2, 'kural', 'குறள்', 2, 2);

-- Lines for Kural 2
INSERT INTO lines (line_id, verse_id, line_number, line_text, line_text_transliteration, line_text_translation) VALUES
(3, 2, 1, 'கற்றதனால் ஆய பயனென்கொல் வாலறிவன்', 'Katrathanaal aaya payanenkol vaalarinan', 'What is the benefit of learning'),
(4, 2, 2, 'நற்றாள் தொழாஅர் எனின்', 'Natraal thozhaaar enin', 'If one does not worship the good feet');

-- Words for Kural 2, Line 1
INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type, sandhi_split, meaning) VALUES
(8, 3, 1, 'கற்றதனால்', 'katrathanaal', 'கல்', 'verb', 'கற்று + அதனால்', 'by learning'),
(9, 3, 2, 'ஆய', 'aaya', 'ஆகு', 'verb', NULL, 'that which has become'),
(10, 3, 3, 'பயன்', 'payan', 'பயன்', 'noun', NULL, 'benefit/use'),
(11, 3, 4, 'என்கொல்', 'enkol', 'என்', 'particle', NULL, 'what is it'),
(12, 3, 5, 'வாலறிவன்', 'vaalarinan', 'வாலறிவன்', 'noun', NULL, 'the wise one');

-- Words for Kural 2, Line 2
INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type, meaning) VALUES
(13, 4, 1, 'நற்றாள்', 'natraal', 'நல்', 'adjective', 'good feet (of God)'),
(14, 4, 2, 'தொழாஅர்', 'thozhaaar', 'தொழு', 'verb', 'do not worship'),
(15, 4, 3, 'எனின்', 'enin', 'என்', 'conditional', 'if');

-- Add a Kural from Adhikaram 2 (Vaan Sirappu - Glory of Rain)
INSERT INTO verses (verse_id, work_id, section_id, verse_number, verse_type, verse_type_tamil, total_lines, sort_order) VALUES
(3, 3, 7, 11, 'kural', 'குறள்', 2, 1);

-- Lines for Kural 11
INSERT INTO lines (line_id, verse_id, line_number, line_text, line_text_transliteration) VALUES
(5, 3, 1, 'வான் நின்று உலகம் வழங்கி வருதலால்', 'Vaan nindru ulagam vazhanghi varudhaal'),
(6, 3, 2, 'தான் அமிழ்தம் என்று உணரப் படும்', 'Thaan amizhdam endru unarap padum');

-- Words for Kural 11
INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type, meaning) VALUES
(16, 5, 1, 'வான்', 'vaan', 'வான்', 'noun', 'sky/rain'),
(17, 5, 2, 'நின்று', 'nindru', 'நில்', 'verb', 'standing/being'),
(18, 5, 3, 'உலகம்', 'ulagam', 'உலகு', 'noun', 'world'),
(19, 5, 4, 'வழங்கி', 'vazhanghi', 'வழங்கு', 'verb', 'providing'),
(20, 5, 5, 'வருதலால்', 'varudhaal', 'வரு', 'verb', 'because it comes');

INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type, meaning) VALUES
(21, 6, 1, 'தான்', 'thaan', 'தான்', 'pronoun', 'itself'),
(22, 6, 2, 'அமிழ்தம்', 'amizhdham', 'அமிழ்து', 'noun', 'nectar/ambrosia'),
(23, 6, 3, 'என்று', 'endru', 'என்', 'particle', 'as'),
(24, 6, 4, 'உணரப்படும்', 'unarappadum', 'உணர்', 'verb', 'is understood');

-- Add sample Kural about "அறம்" (virtue) - Kural 31
INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order) VALUES
(8, 3, 5, 'adhikaram', 'அதிகாரம்', 4, 'Aran Valiyurudhal', 'அறன் வலியுறுத்தல்', 4);

INSERT INTO verses (verse_id, work_id, section_id, verse_number, verse_type, verse_type_tamil, total_lines, sort_order) VALUES
(4, 3, 8, 31, 'kural', 'குறள்', 2, 1);

INSERT INTO lines (line_id, verse_id, line_number, line_text) VALUES
(7, 4, 1, 'அறத்தான் வருவதே இன்பம் மற்றெல்லாம்'),
(8, 4, 2, 'புறத்த புகழும் இல');

-- Words for Kural 31
INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type, sandhi_split, meaning) VALUES
(25, 7, 1, 'அறத்தான்', 'araththaan', 'அறம்', 'noun', 'அறம் + தான்', 'from virtue'),
(26, 7, 2, 'வருவதே', 'varuvadhe', 'வரு', 'verb', NULL, 'that which comes'),
(27, 7, 3, 'இன்பம்', 'inbam', 'இன்பு', 'noun', NULL, 'happiness'),
(28, 7, 4, 'மற்றெல்லாம்', 'matrellaam', 'மற்று', 'adjective', 'மற்று + எல்லாம்', 'all others');

INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type, meaning) VALUES
(29, 8, 1, 'புறத்த', 'puraththa', 'புறம்', 'adjective', 'external'),
(30, 8, 2, 'புகழும்', 'pugazhum', 'புகழ்', 'noun', 'fame'),
(31, 8, 3, 'இல', 'ila', 'இல்', 'negative', 'not');

-- Kambaramayanam sample verse
INSERT INTO verses (verse_id, work_id, section_id, verse_number, verse_type, verse_type_tamil, total_lines, sort_order) VALUES
(5, 5, 102, 1, 'poem', 'பாடல்', 4, 1);

-- Lines for Kambaramayanam verse
INSERT INTO lines (line_id, verse_id, line_number, line_text, line_text_transliteration) VALUES
(9, 5, 1, 'அறம் புரிந்த மன்னர் வாழும்', 'Aram purindha mannar vaazhum'),
(10, 5, 2, 'அரியசிங்க வேந்தன் நகரம்', 'Ariyasinga vendhan nagaram'),
(11, 5, 3, 'உலகம் போற்றும் அயோத்தி', 'Ulagam potrrum ayodhi'),
(12, 5, 4, 'முதல் நகர் அது தானே', 'Mudhal nagar athu thaanae');

-- Words for Kambaramayanam
INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type, meaning) VALUES
(32, 9, 1, 'அறம்', 'aram', 'அறம்', 'noun', 'virtue/righteousness'),
(33, 9, 2, 'புரிந்த', 'purindha', 'புரி', 'verb', 'performed'),
(34, 9, 3, 'மன்னர்', 'mannar', 'மன்னன்', 'noun', 'kings'),
(35, 9, 4, 'வாழும்', 'vaazhum', 'வாழ்', 'verb', 'live');

INSERT INTO words (word_id, line_id, word_position, word_text, word_root, word_type, meaning) VALUES
(36, 10, 1, 'அரியசிங்க', 'ariyasinga', 'அரி', 'noun', 'lion-like'),
(37, 10, 2, 'வேந்தன்', 'vendhan', 'வேந்து', 'noun', 'king'),
(38, 10, 3, 'நகரம்', 'nagaram', 'நகர்', 'noun', 'city');

INSERT INTO words (word_id, line_id, word_position, word_text, word_root, word_type, meaning) VALUES
(39, 11, 1, 'உலகம்', 'ulagam', 'உலகு', 'noun', 'world'),
(40, 11, 2, 'போற்றும்', 'potrrum', 'போற்று', 'verb', 'praises'),
(41, 11, 3, 'அயோத்தி', 'ayodhi', 'அயோத்தி', 'proper noun', 'Ayodhya');

INSERT INTO words (word_id, line_id, word_position, word_text, word_root, word_type, meaning) VALUES
(42, 12, 1, 'முதல்', 'mudhal', 'முதல்', 'adjective', 'first/primary'),
(43, 12, 2, 'நகர்', 'nagar', 'நகர்', 'noun', 'city'),
(44, 12, 3, 'அது', 'athu', 'அது', 'pronoun', 'that'),
(45, 12, 4, 'தானே', 'thaanae', 'தான்', 'emphatic', 'indeed');

-- Silapathikaram structure
INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order) VALUES
(200, 4, NULL, 'kandam', 'காண்டம்', 1, 'Puhaar Kandam', 'புகார் காண்டம்', 1);

INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order) VALUES
(201, 4, 200, 'kathai', 'கதை', 1, 'Mangala Vazhthu', 'மங்கல வாழ்த்து', 1);

-- Silapathikaram sample verse
INSERT INTO verses (verse_id, work_id, section_id, verse_number, verse_type, verse_type_tamil, total_lines, sort_order) VALUES
(6, 4, 201, 1, 'poem', 'பாடல்', 3, 1);

INSERT INTO lines (line_id, verse_id, line_number, line_text) VALUES
(13, 6, 1, 'உலகம் உவப்ப வாழ்வோம் அறத்தொடு'),
(14, 6, 2, 'இலகு முதல் பொருள் இன்பம் தரும்'),
(15, 6, 3, 'அன்பொடு வாழும் தம்பதிகள்');

-- Words for Silapathikaram
INSERT INTO words (word_id, line_id, word_position, word_text, word_root, word_type, sandhi_split, meaning) VALUES
(46, 13, 1, 'உலகம்', 'ulagam', 'உலகு', 'noun', NULL, 'world'),
(47, 13, 2, 'உவப்ப', 'uvappa', 'உவ', 'verb', NULL, 'to rejoice'),
(48, 13, 3, 'வாழ்வோம்', 'vaazhvom', 'வாழ்', 'verb', NULL, 'we shall live'),
(49, 13, 4, 'அறத்தொடு', 'araththodu', 'அறம்', 'noun', 'அறம் + ஒடு', 'with virtue');

INSERT INTO words (word_id, line_id, word_position, word_text, word_root, word_type, meaning) VALUES
(50, 14, 1, 'இலகு', 'ilagu', 'இலகு', 'verb', 'shining'),
(51, 14, 2, 'முதல்', 'mudhal', 'முதல்', 'adjective', 'first/primary'),
(52, 14, 3, 'பொருள்', 'porul', 'பொருள்', 'noun', 'wealth'),
(53, 14, 4, 'இன்பம்', 'inbam', 'இன்பு', 'noun', 'happiness'),
(54, 14, 5, 'தரும்', 'tharum', 'தரு', 'verb', 'gives');

INSERT INTO words (word_id, line_id, word_position, word_text, word_root, word_type, sandhi_split, meaning) VALUES
(55, 15, 1, 'அன்பொடு', 'anbodu', 'அன்பு', 'noun', 'அன்பு + ஒடு', 'with love'),
(56, 15, 2, 'வாழும்', 'vaazhum', 'வாழ்', 'verb', NULL, 'living'),
(57, 15, 3, 'தம்பதிகள்', 'thambadhigal', 'தம்பதி', 'noun', NULL, 'married couples');

-- ============================================================================
-- SETUP COMPLETE
-- ============================================================================
