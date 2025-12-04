-- Sample Word Data: Demonstrating Same Word in Different Contexts
-- This shows how words like "அறம்" (aram/virtue), "அன்பு" (anbu/love), "முதல்" (mudal/first)
-- appear in multiple verses across different works

-- ============================================================================
-- ADDITIONAL SAMPLE DATA FOR THIRUKKURAL
-- ============================================================================

-- Add Kural 2 (in same adhikaram as Kural 1)
INSERT INTO verses (verse_id, work_id, section_id, verse_number, verse_type, verse_type_tamil, total_lines, sort_order) VALUES
(2, 3, 6, 2, 'kural', 'குறள்', 2, 2);

-- Lines for Kural 2: About rain and virtue
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

-- Words for Kural 11 - Note "வான்" and "உலகம்" appearing again
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

-- Words for Kural 31 - Notice "அறத்தான்" (from virtue)
INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type, sandhi_split, meaning) VALUES
(25, 7, 1, 'அறத்தான்', 'araththaan', 'அறம்', 'noun', 'அறம் + தான்', 'from virtue'),
(26, 7, 2, 'வருவதே', 'varuvadhe', 'வரு', 'verb', NULL, 'that which comes'),
(27, 7, 3, 'இன்பம்', 'inbam', 'இன்பு', 'noun', NULL, 'happiness'),
(28, 7, 4, 'மற்றெல்லாம்', 'matrellaam', 'மற்று', 'adjective', 'மற்று + எல்லாம்', 'all others');

INSERT INTO words (word_id, line_id, word_position, word_text, word_text_transliteration, word_root, word_type, meaning) VALUES
(29, 8, 1, 'புறத்த', 'puraththa', 'புறம்', 'adjective', 'external'),
(30, 8, 2, 'புகழும்', 'pugazhum', 'புகழ்', 'noun', 'fame'),
(31, 8, 3, 'இல', 'ila', 'இல்', 'negative', 'not');

-- ============================================================================
-- SAMPLE DATA FOR KAMBARAMAYANAM
-- ============================================================================

-- Add a verse from Kambaramayanam (using existing structure from schema.sql)
INSERT INTO verses (verse_id, work_id, section_id, verse_number, verse_type, verse_type_tamil, total_lines, sort_order) VALUES
(5, 5, 102, 1, 'venba', 'வெண்பா', 4, 1);

-- Lines for Kambaramayanam verse - describing Ayodhya
INSERT INTO lines (line_id, verse_id, line_number, line_text, line_text_transliteration) VALUES
(9, 5, 1, 'அறம் புரிந்த மன்னர் வாழும்', 'Aram purindha mannar vaazhum'),
(10, 5, 2, 'அரியசிங்க வேந்தன் நகரம்', 'Ariyasinga vendhan nagaram'),
(11, 5, 3, 'உலகம் போற்றும் அயோத்தி', 'Ulagam potrrum ayodhi'),
(12, 5, 4, 'முதல் நகர் அது தானே', 'Mudhal nagar athu thaanae');

-- Words for Kambaramayanam - Notice "அறம்", "உலகம்", "முதல்" appearing again
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

-- ============================================================================
-- SAMPLE DATA FOR SILAPATHIKARAM
-- ============================================================================

-- Add structure for Silapathikaram
INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order) VALUES
(200, 4, NULL, 'kandam', 'காண்டம்', 1, 'Puhaar Kandam', 'புகார் காண்டம்', 1);

INSERT INTO sections (section_id, work_id, parent_section_id, level_type, level_type_tamil, section_number, section_name, section_name_tamil, sort_order) VALUES
(201, 4, 200, 'kathai', 'கதை', 1, 'Mangala Vazhthu', 'மங்கல வாழ்த்து', 1);

-- Add a verse from Silapathikaram
INSERT INTO verses (verse_id, work_id, section_id, verse_number, verse_type, verse_type_tamil, total_lines, sort_order) VALUES
(6, 4, 201, 1, 'aasiriyappa', 'ஆசிரியப்பா', 3, 1);

INSERT INTO lines (line_id, verse_id, line_number, line_text) VALUES
(13, 6, 1, 'உலகம் உவப்ப வாழ்வோம் அறத்தொடு'),
(14, 6, 2, 'இலகு முதல் பொருள் இன்பம் தரும்'),
(15, 6, 3, 'அன்பொடு வாழும் தம்பதிகள்');

-- Words showing "உலகம்", "அறத்தொடு" (with virtue), "முதல்", "அன்பொடு" (with love)
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
-- SUMMARY OF SAMPLE DATA
-- ============================================================================

-- This sample data demonstrates:
-- 1. Word "முதல்" (first/primary) appears in:
--    - Thirukkural Kural 1 (word_id=2)
--    - Kambaramayanam verse (word_id=42)
--    - Silapathikaram verse (word_id=51)
--
-- 2. Word "உலகம்"/"உலகு" (world) appears in:
--    - Thirukkural Kural 1 (word_id=7) as "உலகு"
--    - Thirukkural Kural 11 (word_id=18) as "உலகம்"
--    - Kambaramayanam verse (word_id=39) as "உலகம்"
--    - Silapathikaram verse (word_id=46) as "உலகம்"
--
-- 3. Word "அறம்" (virtue) with variations appears in:
--    - Thirukkural Kural 31 (word_id=25) as "அறத்தான்"
--    - Kambaramayanam verse (word_id=32) as "அறம்"
--    - Silapathikaram verse (word_id=49) as "அறத்தொடு"
--
-- 4. Word "இன்பம்" (happiness) appears in:
--    - Thirukkural Kural 31 (word_id=27)
--    - Silapathikaram verse (word_id=53)

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Query 1: Find all occurrences of root word "முதல்" across all works
SELECT
    w.work_name,
    vh.hierarchy_path,
    v.verse_number,
    l.line_text,
    wd.word_text,
    wd.word_position,
    wd.meaning
FROM word_details wd
JOIN works w ON wd.work_name = w.work_name
JOIN verses v ON wd.verse_id = v.verse_id
JOIN verse_hierarchy vh ON v.verse_id = vh.verse_id
JOIN lines l ON wd.line_id = l.line_id
WHERE wd.word_root = 'முதல்'
ORDER BY w.work_name, v.verse_number, wd.word_position;

-- Query 2: Find all occurrences of root word "உலகு" (world) across all works
SELECT
    wd.work_name,
    wd.hierarchy_path,
    wd.word_text,
    wd.line_text,
    wd.meaning
FROM word_details wd
WHERE wd.word_root = 'உலகு'
ORDER BY wd.work_name, wd.verse_id;

-- Query 3: Find all occurrences of root word "அறம்" (virtue) with different forms
SELECT
    wd.work_name,
    wd.hierarchy_path,
    wd.word_text,
    wd.sandhi_split,
    wd.line_text,
    wd.meaning
FROM word_details wd
WHERE wd.word_root = 'அறம்'
ORDER BY wd.work_name, wd.verse_id;

-- Query 4: Compare usage of "இன்பம்" (happiness) across works
SELECT
    wd.work_name,
    COUNT(*) as occurrences,
    GROUP_CONCAT(DISTINCT wd.hierarchy_path) as found_in_sections
FROM word_details wd
WHERE wd.word_text = 'இன்பம்' OR wd.word_root = 'இன்பு'
GROUP BY wd.work_name;

-- Query 5: Find words that appear in multiple works
SELECT
    wd.word_root,
    wd.word_type,
    COUNT(DISTINCT wd.work_name) as num_works,
    COUNT(*) as total_occurrences,
    GROUP_CONCAT(DISTINCT wd.work_name) as appears_in_works
FROM word_details wd
WHERE wd.word_root IS NOT NULL
GROUP BY wd.word_root, wd.word_type
HAVING COUNT(DISTINCT wd.work_name) > 1
ORDER BY num_works DESC, total_occurrences DESC;

-- Query 6: Find same word appearing in different verses within Thirukkural
SELECT
    wd.word_root,
    wd.word_text,
    COUNT(DISTINCT wd.verse_id) as num_verses,
    GROUP_CONCAT(DISTINCT wd.hierarchy_path SEPARATOR ' | ') as locations
FROM word_details wd
WHERE wd.work_name = 'Thirukkural'
  AND wd.word_root IS NOT NULL
GROUP BY wd.word_root, wd.word_text
HAVING COUNT(DISTINCT wd.verse_id) > 1
ORDER BY num_verses DESC;

-- Query 7: Detailed word usage matrix (same root, different forms)
SELECT
    w.word_root,
    w.word_text as form,
    w.word_type,
    GROUP_CONCAT(DISTINCT wk.work_name) as works,
    COUNT(*) as frequency
FROM words w
JOIN lines l ON w.line_id = l.line_id
JOIN verses v ON l.verse_id = v.verse_id
JOIN works wk ON v.work_id = wk.work_id
WHERE w.word_root IN ('முதல்', 'உலகு', 'அறம்', 'இன்பு', 'அன்பு', 'வாழ்')
GROUP BY w.word_root, w.word_text, w.word_type
ORDER BY w.word_root, frequency DESC;
