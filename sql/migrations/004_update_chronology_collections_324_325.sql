-- Migration: Add chronology data for Collections 324 and 325
-- Date: 2026-01-01
-- Purpose: Update chronology_start_year, chronology_end_year, chronology_confidence, and chronology_notes
--          for சிற்றிலக்கியங்கள் (Minor Literary Works) and நீதிநூல்கள் (Ethical Literature)
-- Research: Based on scholarly sources, Wikipedia, Tamil literature encyclopedias, and academic databases

-- =============================================================================
-- COLLECTION 324: சிற்றிலக்கியங்கள் (MINOR LITERARY WORKS - JAIN EPICS)
-- Five Jain minor epics from post-Sangam period
-- =============================================================================

-- Udayana Kumara Kaviyam (உதயணகுமார காவியம்)
-- By Kandiyar
-- IMPORTANT: Corrected dating from 3rd century to 13th-14th century based on scholarly research
UPDATE works SET
    chronology_start_year = 1200,
    chronology_end_year = 1400,
    chronology_confidence = 'medium',
    chronology_notes = 'Tamil Jain epic by Kandiyar (a Jain nun). Scholarly consensus dates composition to 13th-14th century CE, NOT 3rd century. Based on story of Udayanan from Perun kathai (long story) of Kongu velir, which was adapted from Brihat katha written in Prakrit. One of five minor Tamil epics (Ainchirukappiyangal). Contains 6 cantos with 369 stanzas. Part of post-Sangam Jain literary tradition.'
WHERE work_name = 'Udayana Kumara Kaviyam';

-- Nagakumara Kaviyam (நாககுமார காவியம்)
-- Author unknown
-- LOST WORK - only known by references, precise dating impossible
UPDATE works SET
    chronology_start_year = 500,
    chronology_end_year = 1000,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil Jain epic, author unknown. LOST WORK - completely lost with no extant manuscripts surviving, known only by references in other Tamil literary works. One of five minor Tamil epics (Ainchirukappiyangal). Precise dating extremely difficult due to absence of text. Estimated to post-Sangam period (5th-10th century CE) based on references and classification with other minor epics, but this is highly speculative.'
WHERE work_name = 'Nagakumara Kaviyam';

-- Yasodara Kaviyam (யசோதர காவியம்)
-- By Vel of Vennaval
-- Corrected dating: 14th century, not 5th-10th century
UPDATE works SET
    chronology_start_year = 1300,
    chronology_end_year = 1400,
    chronology_confidence = 'medium',
    chronology_notes = 'Tamil Jain epic composed in 14th century CE by Jain author Vel of Vennaval. One of five minor Tamil epics (Ainchirukappiyangal). Jain influence evident through prayers invoking cycle of birth and rebirth. Traditional Jain work emphasizing humanity condemned to endless cycle of birth. Represents Jain contribution to Tamil literature before rise of Shaivite and Vaishnavite devotional movements. Part of significant Tamil Jain literary tradition.'
WHERE work_name = 'Yasodara Kaviyam';

-- Choolamani (சூளாமணி)
-- By Tholamozhithevar (Tolamoli Thevar)
-- Post-10th century, likely 11th-12th century (after Tiruttakkatēvar)
UPDATE works SET
    chronology_start_year = 1000,
    chronology_end_year = 1200,
    chronology_confidence = 'medium',
    chronology_notes = 'Tamil Jain epic by Tolamoli Thevar, composed after 10th century CE. Author probably lived after Tiruttakkatēvar (author of Cīvaka Cintāmaṇi) and was follower of Digambara tradition. Contains 2,131 quatrains across 12 cantos written in viruttam metre similar to Cīvaka Cintāmaṇi. Narrates Jain version of story of Balarama and Krishna (named Vijayan and Thivittan). Gives detailed description of countryside and customs: influence of soothsayers, practice of swayamvara, polygamy, acts of valor, wars. One of five minor epics with highest literary merit along with Neelakesi.'
WHERE work_name = 'Choolamani';

-- Nilakesi (நீலகேசி)
-- Author unknown
-- Later half of 10th century CE (Jain response to Buddhist Kundalakesi)
UPDATE works SET
    chronology_start_year = 950,
    chronology_end_year = 1000,
    chronology_confidence = 'high',
    chronology_notes = 'Tamil Jain epic dated to later half of 10th century CE. Author unknown. Contains 10 chapters (Charukkams) and 894 stanzas in Viruttam metre. Polemical work written as Jain rebuttal to Buddhist criticism in epic Kundalakesi. "Nilakesi" means "The Blue-Haired" - tells story of Jain nun who debates and defeats Buddhist rhetoricians including Arkachandra, Kundalakesi, Moggallana, and even Gautama Buddha himself. Epic and its commentary by Jain saint Vamanar quote extensively from lost Buddhist Kundalakesi text, serving as main source for reconstructing that work. One of five minor Tamil epics with highest literary merit.'
WHERE work_name = 'Nilakesi';

-- =============================================================================
-- COLLECTION 325: நீதிநூல்கள் (ETHICAL LITERATURE)
-- 21 ethical literature works spanning 3rd-20th centuries CE
-- =============================================================================

-- 1. Aathichudi (ஆத்திசூடி)
-- By Auvaiyar II
-- 10th-12th century (scholarly consensus, referenced in Yaaparunkalam 63 commentary)
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1200,
    chronology_confidence = 'medium',
    chronology_notes = 'Tamil didactic work by Auvaiyar II, composed 10th-12th century CE (scholarly consensus based on multiple references). Classical Tamil poetry consisting of 109 single-line aphorisms, each beginning with successive letter of Tamil script. Teaches discipline, humility, social conduct. Written for young children. Konraiventan cited as example for vencenturai in commentary to Yaaparunkalam verse 63, placing author no later than 12th century. Nalvali quotes Thirumular, Tevaram and Thiruvasagam, placing author not earlier than 9th century. Auvaiyar lived during period of Kambar and Ottakoothar during Chola dynasty reign.'
WHERE work_name = 'Aathichudi';

-- 2. Konrai Venthan (கொன்றைவேந்தன்)
-- By Auvaiyar II
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1200,
    chronology_confidence = 'medium',
    chronology_notes = 'Tamil didactic work by Auvaiyar II, 10th-12th century CE. Written for young children along with Aathichudi. Same author and period as Aathichudi. Part of Auvaiyar II corpus of four ethical works for children. Contemporary with Kambar and Ottakoothar during Chola dynasty. Dating based on literary references in Yaaparunkalam commentary and citations of earlier devotional literature (Thirumular, Tevaram, Thiruvasagam) in companion work Nalvali.'
WHERE work_name = 'Konrai Venthan';

-- 3. Moodhurai (Vaakkundaam) (மூதுரை)
-- By Auvaiyar II
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1200,
    chronology_confidence = 'medium',
    chronology_notes = 'Tamil didactic work by Auvaiyar II, 10th-12th century CE. Written for older children. Ilampuranar refers to Mooturai poem 4 in his commentary to Tolkapiyam Porulatikaram verse 72, establishing dating. One of four Auvaiyar II works (Aathichudi, Konraiventhan, Nalvali, Mooturai). Contemporary with Kambar and Ottakoothar during Chola dynasty reign. Dating consensus 10th-12th century based on multiple scholarly references and literary cross-references.'
WHERE work_name = 'Moodhurai (Vaakkundaam)' OR work_name = 'Moodhurai';

-- 4. Nalvazhi (நல்வழி)
-- By Auvaiyar II
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1200,
    chronology_confidence = 'medium',
    chronology_notes = 'Tamil didactic work by Auvaiyar II, 10th-12th century CE. Written for older children along with Mooturai. Poem 40 of Nalvali quotes Thirumular, Tevaram and Thiruvasagam, placing author not earlier than 9th century. Konraiventan cited in Yaaparunkalam 63 commentary, placing author no later than 12th century. One of four Auvaiyar II ethical works. Contemporary with Kambar and Ottakoothar during Chola dynasty. Dating consensus 10th-12th century based on literary references.'
WHERE work_name = 'Nalvazhi';

-- 5. Vetri Vetkai (Narunthokai) (வெற்றி வேற்கை)
-- By Athiveera Rama Pandiyar
-- CORRECTED: 16th-17th century, NOT 3rd-6th century
UPDATE works SET
    chronology_start_year = 1564,
    chronology_end_year = 1604,
    chronology_confidence = 'high',
    chronology_notes = 'Tamil ethical literature by Athiveera Rama Pandiyar, composed 16th-17th century CE (NOT 3rd-6th century as sometimes misattributed). Athiveera Rama Pandiyar reigned 1564-1604 CE. Also known as Narunthokai (நறுந்தொகை). Written with good phrases for young people to learn good principles. Part of நீதிநூல் (moral/ethical literature) tradition but from significantly later period than post-Sangam ethical works. Well-documented dating based on reign of author-king.'
WHERE work_name = 'Vetri Vetkai (Narunthokai)' OR work_name = 'Vetri Vetkai';

-- 6. Ulaga Neethi (உலக நீதி)
-- By Ulaganathar
-- CORRECTED: 18th century, NOT 6th-10th century
UPDATE works SET
    chronology_start_year = 1700,
    chronology_end_year = 1800,
    chronology_confidence = 'high',
    chronology_notes = 'Tamil legal treatise by Pandit Ulaganathar, 18th century CE (NOT 6th-10th century). Contains 13 verses explaining codes of conduct and universal moral principles. Commonly taught to children in Tamil Nadu until a few generations ago to impart moral and ethical lessons. Considered one of first moral texts children would learn from. Well-documented 18th century composition, representing later ethical literature tradition rather than ancient post-Sangam period.'
WHERE work_name = 'Ulaga Neethi';

-- 7. Neethineeri Vilakkam (நீதிநெறி விளக்கம்)
-- By Kumaraguruparar (Kumarakuruparar)
-- 17th century (author: 1625-1688)
UPDATE works SET
    chronology_start_year = 1625,
    chronology_end_year = 1688,
    chronology_confidence = 'high',
    chronology_notes = 'Tamil didactic work by Kumaragurupara Swamigal (1625-1688 CE), 17th century. Author was Saivite ascetic-poet who lived in 17th century, NOT 6th-10th century. Niti venba style book that preaches values. Well-documented authorship and dating based on historical records of Kumarakuruparar, who also wrote other devotional and philosophical works. Represents Tamil ethical literature from Saivite ascetic tradition.'
WHERE work_name = 'Neethineeri Vilakkam';

-- 8. Araneri Chaaram (அறநெறிச்சாரம்)
-- By Samana Munivar Munaippadiyaar (Jain monk)
-- Dating uncertain, likely medieval period (8th-12th century)
UPDATE works SET
    chronology_start_year = 700,
    chronology_end_year = 1200,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil ethical text by Samana Munivar Munaippadiyaar, a Jain monk. Dating uncertain but likely medieval period (8th-12th century CE) based on classification with other Jain Tamil ethical literature. Part of Jain contribution to Tamil moral literature tradition. Specific dating difficult due to limited historical records, but thematic and linguistic analysis suggests post-Sangam medieval period when Jainism still had significant presence in Tamil Nadu before decline of Jain community.'
WHERE work_name = 'Araneri Chaaram';

-- 9. Neethi Nool (நீதி நூல்)
-- By Munusep Vedhanayagam Pillai (Samuel Vedanayagam Pillai)
-- Published 1858, author 1826-1889
UPDATE works SET
    chronology_start_year = 1858,
    chronology_end_year = 1858,
    chronology_confidence = 'high',
    chronology_notes = 'Tamil ethical book by Samuel Vedanayagam Pillai (Tamil Christian, 1826-1889), published 1858 CE. Author served as district Munsiff (judicial position) of Mayuram (Mayiladuthurai) for 13 years. Published while stationed in Tharangambadi. Consists of verses promoting virtues such as justice, integrity, and ethical behavior. Written in Thirukkural style with couplets on moral behaviour. Well accepted during period. Author was first novelist of Tamil language and remarkable 19th century poet of South India. Precisely dated work.'
WHERE work_name = 'Neethi Nool';

-- 10. Nanneri (நன்னெறி)
-- By Siva Prakasar
-- Late 17th century (author born ~1650, died ~1680)
UPDATE works SET
    chronology_start_year = 1650,
    chronology_end_year = 1690,
    chronology_confidence = 'high',
    chronology_notes = 'Tamil ethical poetry by Siva Prakasar, late 17th to early 18th century CE. Author born in Kanchipuram around middle of 17th century and died at age 32 (approximately 1680-1690). Contains 40 stanzas (Venpaas) dealing with moral instruction. Most well-known of author more than 34 Tamil books. Represents ethical literature from Tamil Saivite philosophical tradition. Well-documented authorship and dating based on biographical records.'
WHERE work_name = 'Nanneri';

-- 11. Neethi Chudamani (நீதி சூடாமணி)
-- Author unknown
-- Estimated 10th-15th century (medieval period, uncertain)
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1500,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil ethical poetry, author unknown. Dating estimated to 10th-15th century CE (medieval period) based on classification with other medieval Tamil ethical literature. "Chudamani" term used in medieval Tamil literary works (Chudamani-nighantu written by Vira-mandalavar around end of 9th century indicates term usage). Limited documentation makes precise dating difficult. Part of broader Tamil ethical literature tradition from post-Sangam through medieval periods.'
WHERE work_name = 'Neethi Chudamani';

-- 12. Somesar (சோமேசர்)
-- Author unknown
-- Estimated 10th-15th century (medieval period, no clear documentation found)
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1500,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil ethical poetry, author unknown. Dating estimated to 10th-15th century CE (medieval period) based on general classification with other medieval Tamil ethical literature. No clear scholarly documentation found for this specific work. May be obscure or lost work, or known by alternative transliteration. Dating highly uncertain - requires further research in specialized Tamil literature sources. Included in நீதிநூல்கள் collection but limited historical information available.'
WHERE work_name = 'Somesar';

-- 13. Viveka Chinthamani (விவேக சிந்தாமணி)
-- Author unknown (Tamil version, distinct from Sanskrit Viveka Chudamani)
-- Estimated 10th-15th century
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1500,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil ethical work, author unknown. Estimated 10th-15th century CE. NOT a religious scripture but secular work modeled on Bhartruhari Neeti Satakam. Distinct from Sanskrit Viveka Chudamani by Adi Shankaracharya (8th century). Tamil version likely composed during medieval period as part of ethical literature tradition. Dating uncertain - requires specialized Tamil literature sources for precise chronology. Part of broader Tamil ethical poetry tradition influenced by Sanskrit didactic works.'
WHERE work_name = 'Viveka Chinthamani';

-- 14. Aathichudi Venpa (ஆத்திசூடி வெண்பா)
-- Author unknown
-- Estimated 12th-17th century (venpa style commentaries period)
UPDATE works SET
    chronology_start_year = 1100,
    chronology_end_year = 1700,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil ethical poetry in venpa (venba) metre, author unknown. Estimated 12th-17th century CE based on venpa style ethical works from this period. Venpa is classical Tamil poetic form consisting of 2-12 lines. Ethical venpa works flourished during medieval period alongside other didactic literature. May be commentary or elaboration on Auvaiyar Aathichudi in venpa form. Dating uncertain without specific scholarly references - requires further research.'
WHERE work_name = 'Aathichudi Venpa';

-- 15. Neethi Venpa (நீதி வெண்பா)
-- Author unknown
-- Estimated 12th-17th century (venpa style ethical works period)
UPDATE works SET
    chronology_start_year = 1100,
    chronology_end_year = 1700,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil ethical poetry in venpa (venba) metre, author unknown. Estimated 12th-17th century CE. Venpa is classical Tamil poetic form used for didactic purposes. Niti venba style book preaching moral values. Part of broader tradition of Tamil ethical venpa poetry from medieval period. Similar to other venpa ethical works like Neethi Neri Vilakkam (17th century). Dating uncertain without specific authorship - requires specialized Tamil literature sources.'
WHERE work_name = 'Neethi Venpa';

-- 16. Nanmadhi Venpa (நன்மதி வெண்பா)
-- Author unknown
-- Estimated 12th-17th century (venpa style ethical works period)
UPDATE works SET
    chronology_start_year = 1100,
    chronology_end_year = 1700,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil ethical poetry in venpa (venba) metre, author unknown. Estimated 12th-17th century CE. Part of Tamil ethical literature tradition using classical venpa poetic form for moral instruction. "Nanmadhi" means good character/wisdom. Represents didactic poetry tradition from medieval Tamil Nadu. Dating uncertain without specific scholarly references or authorship documentation. Requires further research in specialized Tamil literature archives for precise chronology.'
WHERE work_name = 'Nanmadhi Venpa';

-- 17. Arungalach Cheppu (அருங்கலச்செப்பு)
-- Author unknown
-- Estimated 10th-15th century (general medieval period estimate)
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1500,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil ethical literature, author unknown. Dating estimated to 10th-15th century CE (medieval period) based on general classification with நீதிநூல்கள் collection. No clear online scholarly documentation found. May be obscure work with limited modern accessibility. "Arungalach Cheppu" meaning relates to precious vessel/repository of wisdom. Dating highly uncertain - requires access to specialized Tamil manuscript collections and academic sources. Further research needed for accurate chronology.'
WHERE work_name = 'Arungalach Cheppu';

-- 18. Mudhumozhimael Vaippu (முதுமொழிமேல் வைப்பு)
-- Author unknown
-- Estimated 10th-15th century (general medieval period estimate)
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1500,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil ethical poetry, author unknown. Dating estimated to 10th-15th century CE (medieval period) based on general classification with நீதிநூல்கள் collection. "Mudhumozhimael Vaippu" meaning relates to elaboration on ancient proverbs/sayings. No clear scholarly documentation found in online sources. May be commentary or expansion on traditional Tamil proverbs. Dating highly uncertain - requires specialized Tamil literature archives. Further research needed for precise chronology and authorship.'
WHERE work_name = 'Mudhumozhimael Vaippu';

-- 19. Pudhiya Aathichudi (புதிய ஆத்திசூடி)
-- By Bharathiyar (Subramania Bharati)
-- Early 20th century (author: 1882-1921)
UPDATE works SET
    chronology_start_year = 1900,
    chronology_end_year = 1921,
    chronology_confidence = 'high',
    chronology_notes = 'Tamil ethical poetry for children by Subramania Bharati (Mahakavi Bharathiyar), early 20th century CE. Author lived 1882-1921. "Pudhiya Aathichudi" (New Aathichudi) modernizes traditional Auvaiyar Aathichudi. Songs for children in Paappa Paattu and Pudhiya Aathichoodi evoke sense of equality, love towards all living beings, casteless society, courage. Part of Bharathiyar comprehensive literary output including devotional songs, patriotic songs, women empowerment, national integration. Well-documented authorship and period. Indian independence activist, social reformer, journalist, teacher, polyglot.'
WHERE work_name = 'Pudhiya Aathichudi';

-- 20. Ilaiyaar Aathichudi (இளையார் ஆத்திசூடி)
-- Author unknown
-- Estimated 15th-19th century (no clear documentation found)
UPDATE works SET
    chronology_start_year = 1400,
    chronology_end_year = 1900,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil ethical literature for children, author unknown. Dating estimated to 15th-19th century CE based on general classification. "Ilaiyaar" means youth/young people. Likely adaptation or variant of traditional Aathichudi format for younger audience. No clear scholarly documentation found in online sources. May be regional or less widely circulated work. Dating highly uncertain - requires specialized Tamil children literature archives. Further research needed for accurate chronology and authorship information.'
WHERE work_name = 'Ilaiyaar Aathichudi';

-- 21. Thirukkural Kumaresa Venpa (திருக்குறள் குமரேச வெண்பா)
-- By Kumaresa Guruparar (attribution uncertain)
-- Estimated 17th-19th century (Kumaragurupara lived 1625-1688, but this commentary may be by different author)
UPDATE works SET
    chronology_start_year = 1600,
    chronology_end_year = 1900,
    chronology_confidence = 'low',
    chronology_notes = 'Tamil commentary on Thirukkural in venpa metre. Attribution to Kumaresa Guruparar uncertain. Kumaragurupara Desikar (1625-1688 CE) was 17th century Saivite poet, but unclear if THIS specific Thirukkural commentary is his work or by different author with similar name. At least 21 venpa commentaries exist for Thirukkural including Somesar Mudumoli Venba, Murugesar Muduneri Venba, Sivasiva Venba, Irangesa Venba, Vadamalai Venba, Dhinakara Venba, Jinendra Venba. Contains 1,331 verses (one per Thirukkural verse plus invocation). Dating uncertain - 17th-19th century estimate. Requires specialized Thirukkural commentary research for precise attribution and chronology.'
WHERE work_name = 'Thirukkural Kumaresa Venpa';

-- Verification query to check updates
-- Uncomment to run verification:
-- SELECT work_name, work_name_tamil, chronology_start_year, chronology_end_year,
--        chronology_confidence, LEFT(chronology_notes, 100) as notes_preview
-- FROM works
-- WHERE work_id IN (
--     SELECT work_id FROM work_collections WHERE collection_id IN (324, 325)
-- )
-- ORDER BY chronology_start_year, work_id;
