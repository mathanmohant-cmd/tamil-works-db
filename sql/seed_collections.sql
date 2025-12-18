-- ============================================================================
-- SEED DATA FOR COLLECTIONS
-- Pre-defined literary periods, canons, traditions, and genres
-- ============================================================================
-- Run this after complete_setup.sql to populate collections
-- Usage: psql $DATABASE_URL -f sql/seed_collections.sql
-- ============================================================================

-- ============================================================================
-- TOP-LEVEL: LITERARY PERIODS
-- ============================================================================

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(1, 'Sangam Literature', 'சங்க இலக்கியம்', 'period', 'Classical Tamil literature from 300 BCE - 300 CE, representing the earliest extant Tamil literary tradition', NULL, 1),
(2, 'Post-Sangam Literature', 'சங்கத்துக்கு பிந்தைய இலக்கியம்', 'period', 'Tamil literature from 300 CE - 600 CE, including ethical texts and early epics', NULL, 2),
(3, 'Medieval Literature', 'இடைக்கால இலக்கியம்', 'period', 'Tamil literature from 600 CE - 1800 CE, including Bhakti movement and medieval epics', NULL, 3),
(4, 'Modern Literature', 'நவீன இலக்கியம்', 'period', 'Tamil literature from 1800 CE onwards, including Tamil Renaissance and contemporary works', NULL, 4);

-- ============================================================================
-- LEVEL 2: SANGAM → Pathinenmēlkaṇakku (பதினெண்மேல்கணக்கு)
-- ============================================================================
-- The "Eighteen Major Works" - the core Sangam literature canon

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(5, 'Pathinenmelkanakku', 'பதினெண்மேல்கணக்கு', 'canon', 'Eighteen Major Works - The core canon of Sangam literature (Ettuthokai + Pathupaattu)', 1, 1);

-- ============================================================================
-- LEVEL 3: Pathinenmēlkaṇakku → Ettuthokai & Pathupaattu
-- ============================================================================

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(10, 'Ettuthokai', 'எட்டுத்தொகை', 'canon', 'Eight Anthologies - Classical Sangam poetry collections of love and valor', 5, 1),
(11, 'Pathupaattu', 'பத்துப்பாட்டு', 'canon', 'Ten Idylls - Long poems of Sangam period describing landscapes, kings, and deities', 5, 2);

-- ============================================================================
-- POST-SANGAM SUB-COLLECTIONS (Children of Post-Sangam Literature)
-- ============================================================================

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(20, 'Eighteen Minor Classics', 'பதினெண்கீழ்க்கணக்கு', 'canon', 'Eighteen didactic works on ethics, morals, and conduct, including Thirukkural', 2, 1),
(21, 'Five Great Epics', 'ஐம்பெரும்காப்பியங்கள்', 'canon', 'Five major Tamil epics of the post-Sangam period', 2, 2);

-- ============================================================================
-- MEDIEVAL SUB-COLLECTIONS (Children of Medieval Literature)
-- ============================================================================

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(30, 'Shaiva Literature', 'சைவ இலக்கியம்', 'tradition', 'Shaiva devotional literature including Thevaram, Thiruvachakam, and canonical texts', 3, 1),
(31, 'Vaishnava Literature', 'வைணவ இலக்கியம்', 'tradition', 'Vaishnava devotional literature including Divya Prabandham and Alwar hymns', 3, 2),
(32, 'Jaina Literature', 'சமண இலக்கியம்', 'tradition', 'Jaina literature including epics and ethical texts', 3, 3),
(33, 'Buddhist Literature', 'பௌத்த இலக்கியம்', 'tradition', 'Buddhist Tamil literature', 3, 4),
(34, 'Medieval Epics', 'இடைக்கால காப்பியங்கள்', 'canon', 'Medieval Tamil epics including Kambaramayanam and Periya Puranam', 3, 5);

-- ============================================================================
-- SHAIVA SUB-COLLECTIONS (Granular breakdown)
-- ============================================================================

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(301, 'Thevaram', 'தேவாரம்', 'canon', 'Hymns of the three Nayanmars: Appar, Sambandar, Sundarar', 30, 1),
(302, 'Thirumurai', 'திருமுறை', 'canon', 'Twelve sacred books of Tamil Shaiva Siddhanta', 30, 2);

-- ============================================================================
-- GENRE COLLECTIONS (Cross-period thematic groupings)
-- ============================================================================

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(50, 'Epic Poetry', 'காப்பியம்', 'genre', 'Tamil epic literature across all periods - narrative poems of heroic deeds', NULL, 10),
(51, 'Devotional Literature', 'பக்தி இலக்கியம்', 'genre', 'Devotional works across all traditions - hymns and prayers to deities', NULL, 11),
(52, 'Ethical Literature', 'அற இலக்கியம்', 'genre', 'Works on ethics, morals, dharma, and virtuous living', NULL, 12),
(53, 'Grammar & Linguistics', 'இலக்கணம்', 'genre', 'Grammatical treatises and linguistic works on Tamil language', NULL, 13),
(54, 'Love Poetry', 'காதல் இலக்கியம்', 'genre', 'Poetry focused on love, romance, and human relationships (Akam)', NULL, 14),
(55, 'Heroic Poetry', 'வீரம் இலக்கியம்', 'genre', 'Poetry focused on valor, war, kings, and public life (Puram)', NULL, 15);

-- ============================================================================
-- SPECIAL/CUSTOM COLLECTIONS
-- ============================================================================
-- Note: Traditional Canon (ID=100) is kept as an empty collection for
-- manually curated ordering. Works are NOT pre-assigned - you can add them
-- via parsers or collection management utility as needed.

INSERT INTO collections (collection_id, collection_name, collection_name_tamil, collection_type, description, parent_collection_id, sort_order) VALUES
(100, 'Traditional Canon', 'பாரம்பரிய நூல்கள்', 'custom', 'Manually curated canonical ordering of major Tamil literary works. Use collection management utility to assign works and positions.', NULL, 100),
(101, 'Tolkappiyam Tradition', 'தொல்காப்பியம் மரபு', 'custom', 'Works that follow the grammatical rules established in Tolkappiyam', NULL, 101);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- View all collections hierarchically
-- SELECT * FROM collection_hierarchy;

-- Count collections by type
-- SELECT collection_type, COUNT(*) as count
-- FROM collections
-- GROUP BY collection_type
-- ORDER BY count DESC;

-- View parent-child relationships
-- SELECT
--     c.collection_name,
--     pc.collection_name AS parent_name,
--     c.collection_type
-- FROM collections c
-- LEFT JOIN collections pc ON c.parent_collection_id = pc.collection_id
-- ORDER BY c.sort_order;

COMMIT;
