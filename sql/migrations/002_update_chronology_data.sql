-- Migration: Add chronology data for all Tamil literary works
-- Date: 2025-12-30
-- Purpose: Update chronology_start_year, chronology_end_year, chronology_confidence, and chronology_notes
--          for all works based on scholarly research (Zvelebil, Hart, and other Tamil literature experts)

-- =============================================================================
-- ANCIENT GRAMMAR
-- =============================================================================

-- Tolkappiyam (தொல்காப்பியம்)
-- Scholarly consensus: Core text 100 BCE - 250 CE (Zvelebil: 150 BCE or later for Ur-text)
-- Final redaction by 5th century CE
UPDATE works SET
    chronology_start_year = -100,
    chronology_end_year = 250,
    chronology_confidence = 'medium',
    chronology_notes = 'Ancient Tamil grammar text. Scholarly debate ranges 3rd century BCE to 8th century CE. Zvelebil dates core Ur-text to 150 BCE or later, with Books 1-2 dating to 100 BCE-250 CE period. Final manuscript version fixed by 5th century CE. Dating based on linguistic analysis, epigraphy, and comparison with Sangam literature.'
WHERE work_name = 'Tolkappiyam';

-- =============================================================================
-- SANGAM LITERATURE (200 BCE - 500 CE)
-- Eight Anthologies (Ettuthokai) + Ten Idylls (Pattupattu)
-- =============================================================================

-- Note: Sangam literature dates show scholarly variation from 200 BCE to 500 CE
-- Middle-ground consensus: ~300 BCE (Upinder Singh, Ancient India, 2009)
-- Layered composition: Earliest 2nd-3rd century CE, middle 2nd-4th CE, final 3rd-5th CE

UPDATE works SET
    chronology_start_year = -200,
    chronology_end_year = 500,
    chronology_confidence = 'medium',
    chronology_notes = 'Part of Sangam literature corpus. Scholarly consensus dates Sangam period from 200 BCE to 500 CE. Pattupattu shows layered composition: earliest layer 2nd-3rd century CE, middle layer 2nd-4th century CE, final layer 3rd-5th century CE. Dating based on linguistic features, internal references, and comparison with other Tamil and Sanskrit literature.'
WHERE work_name IN (
    'Natrinai', 'Kurunthokai', 'Ainkurunuru', 'Patirruppattu',
    'Paripatal', 'Kalithokai', 'Akananuru', 'Purananuru',
    'Thirumurugarruppadai', 'Porunaratruppadai', 'Sirupanarruppadai',
    'Perumpanarruppadai', 'Mullaippattu', 'Maduraikkanci',
    'Nedunalvadai', 'Kurincippattu', 'Pattinappalai', 'Malaipadukadam'
);

-- =============================================================================
-- EIGHTEEN LESSER TEXTS (Pathinenkilkanakku) - POST-SANGAM DIDACTIC LITERATURE
-- =============================================================================

-- Thirukkural (திருக்குறள்)
-- Scholarly consensus: 450-500 CE (Zvelebil), NOT 1st century BCE
-- Stuart Blackburn: ~500 CE is current scholarly consensus
UPDATE works SET
    chronology_start_year = 450,
    chronology_end_year = 500,
    chronology_confidence = 'high',
    chronology_notes = 'Ethical text by Thiruvalluvar. Scholarly consensus places composition around 500 CE (Stuart Blackburn). Zvelebil dates it to 450-500 CE based on language analysis, allusions to earlier works, and borrowing from Sanskrit treatises. Traditional Tamil dates (300 BCE-1 BCE) are rejected by modern scholars as unsupported by textual evidence. Tamil Nadu government ratified 31 BCE as traditional date, but this represents political/cultural decision rather than scholarly consensus.'
WHERE work_name = 'Thirukkural';

-- Other Pathinenkilkanakku texts (17 works)
-- Post-Sangam didactic literature, general range 300-700 CE
UPDATE works SET
    chronology_start_year = 300,
    chronology_end_year = 700,
    chronology_confidence = 'medium',
    chronology_notes = 'Part of Eighteen Lesser Texts (Pathinenkilkanakku), post-Sangam didactic literature. Scholarly consensus dates this corpus to 300-700 CE, representing ethical and moral teachings in the post-Sangam period. Dating based on linguistic evolution from Sangam literature and thematic similarities to contemporary Buddhist and Jain influences in South India.'
WHERE work_name IN (
    'Naladiyar', 'Nanmanikkadigai', 'Inna Narpathu', 'Iniyavai Narpathu',
    'Kar Narpathu', 'Kalavazhi Narpathu', 'Ainthinai Aimbathu',
    'Ainthinai Ezhubathu', 'Thinaymozhi Aimbathu', 'Kainnilai',
    'Thinaimalai Noorraimpathu', 'Muthumozhikkanchi', 'Elathi',
    'Thirigadugam', 'Pazhamozhi Nanuru', 'Sirupanchamoolam',
    'Asarakkovai'
);

-- =============================================================================
-- FIVE GREAT EPICS (Aimperunkappiyangal)
-- =============================================================================

-- Silapathikaram (சிலப்பதிகாரம்)
-- Zvelebil: 5th-6th century CE (cannot be earlier based on style, language, ideology)
-- Earlier scholars suggested 2nd-3rd century, but this is implausible
UPDATE works SET
    chronology_start_year = 400,
    chronology_end_year = 600,
    chronology_confidence = 'medium',
    chronology_notes = 'Tamil epic by Ilango Adigal. Zvelebil argues text cannot be earlier than 5th-6th century CE based on style, language structure, beliefs, ideologies, and customs portrayed, which differ strikingly from 100-250 CE Sangam texts. Earlier scholars (Ramachandra Dikshitar 1939) proposed 2nd century CE dating, but modern consensus favors later period. Attributed to Jain monk prince, brother of Chera king Chenkuttuvan, though authorship attribution is debated.'
WHERE work_name = 'Silapathikaram';

-- Manimegalai (மணிமேகலை)
-- Follows Silapathikaram, mid-6th century most persuasive (Zvelebil)
-- Scholarly debate ranges from 2nd-9th century
UPDATE works SET
    chronology_start_year = 500,
    chronology_end_year = 700,
    chronology_confidence = 'medium',
    chronology_notes = 'Buddhist Tamil epic, sequel to Silapathikaram. Zvelebil finds mid-6th century dating most persuasive. Scholarly debate ranges from 2nd to 9th century CE. Language and thematic content suggest composition in post-Sangam Buddhist revival period. Work reflects sophisticated Buddhist philosophy and Tamil Buddhist community presence in South India.'
WHERE work_name = 'Manimegalai';

-- Seevaka Sinthamani (சீவக சிந்தாமணி)
-- 10th century CE, authored by Tiruttakkatēvar
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1000,
    chronology_confidence = 'high',
    chronology_notes = 'Jain Tamil epic composed in 10th century CE by Tiruttakkatēvar. Well-documented dating based on literary references and Jain community records. Represents pinnacle of Tamil Jain literature and demonstrates sophisticated narrative techniques and Jain philosophical themes integrated with Tamil literary traditions.'
WHERE work_name = 'Seevaka Sinthamani';

-- Valayapathi (வளையாபதி)
-- ~10th century CE, fragmentary (only 72 stanzas survive)
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1100,
    chronology_confidence = 'medium',
    chronology_notes = 'Fragmentary Jain epic from approximately 10th century CE. Only 72 verses survive from what was originally a complete epic. Dating based on linguistic features and thematic parallels with other Tamil Jain literature. Lost epic status makes precise dating difficult, but linguistic analysis places it in medieval period contemporary with Seevaka Sinthamani.'
WHERE work_name = 'Valayapathi';

-- Kundalakesi (குண்டலகேசி)
-- ~10th century CE, fragmentary (only 19 stanzas survive)
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1100,
    chronology_confidence = 'medium',
    chronology_notes = 'Fragmentary Buddhist epic from approximately 10th century CE. Only 19 verses survive from original complete work. One of the five great Tamil epics, though largely lost. Dating based on limited textual evidence and comparison with contemporary Buddhist literature. Represents Tamil Buddhist literary tradition that declined after medieval period.'
WHERE work_name = 'Kundalakesi';

-- =============================================================================
-- TAMIL RAMAYANA
-- =============================================================================

-- Kambaramayanam (கம்பராமாயணம்)
-- Composed 1178-1185 CE by Kambar (b. 1120, d. 1197 per R. Ragava Aiyangar)
UPDATE works SET
    chronology_start_year = 1178,
    chronology_end_year = 1185,
    chronology_confidence = 'high',
    chronology_notes = 'Tamil retelling of Ramayana by Kambar (1120-1197 CE). Ragava Aiyangar research indicates composition began 1178 and completed 1185 (seven-year period). Composed during Chola Empire under Kulothunga III with patronage of Thiruvennai Nallur Sadayappa Vallal. Kambar refers to Ramanuja in his work Sadagopar Antati, establishing post-Ramanuja dating. Well-documented 12th century dating makes this one of the most precisely dated Tamil classics.'
WHERE work_name = 'Kambaramayanam';

-- =============================================================================
-- THIRUMURAI (திருமுறை) - SHAIVITE DEVOTIONAL LITERATURE
-- 12-volume canonical collection compiled by Nambi Andar Nambi (10th-12th century)
-- =============================================================================

-- Files 1-3: Devaram by Sambandar (திருஞானசம்பந்தர்)
-- 7th century CE, one of three Tevaram composers
UPDATE works SET
    chronology_start_year = 600,
    chronology_end_year = 700,
    chronology_confidence = 'high',
    chronology_notes = 'Part of Devaram (Tevaram), Shaivite devotional hymns. Composed by Thirugnana Sambandar in 7th century CE. One of three great Tevaram poets (Sambandar, Appar, Sundarar) of Tamil Shaiva Bhakti movement. Dating well-established through historical records and literary references. Devaram collection discovered abandoned in Chidambaram temple during Rajaraja Chola I reign (10th century) and compiled by Nambi Andar Nambi.'
WHERE work_name LIKE '%சம்பந்தர்%' OR work_name LIKE '%Sambandar%';

-- Files 4-6: Devaram by Appar (திருநாவுக்கரசர்)
-- 7th century CE
UPDATE works SET
    chronology_start_year = 600,
    chronology_end_year = 700,
    chronology_confidence = 'high',
    chronology_notes = 'Part of Devaram (Tevaram), Shaivite devotional hymns. Composed by Appar (Thirunavukkarasar) in 7th century CE. Contemporary of Sambandar. Appar converted from Jainism to Shaivism and composed passionate devotional poetry. Well-documented dating through historical records and cross-references with other Tevaram poets.'
WHERE work_name LIKE '%நாவுக்கரசர்%' OR work_name LIKE '%Appar%';

-- File 7: Devaram by Sundarar (சுந்தரர்)
-- 8th century CE
UPDATE works SET
    chronology_start_year = 700,
    chronology_end_year = 800,
    chronology_confidence = 'high',
    chronology_notes = 'Part of Devaram (Tevaram), Shaivite devotional hymns. Composed by Sundarar in 8th century CE. Third of the three great Tevaram poets, slightly later than Sambandar and Appar. Known for personal, intimate style of addressing Shiva. Dating established through literary references and Periya Puranam hagiography.'
WHERE work_name LIKE '%சுந்தரர்%' OR work_name LIKE '%Sundarar%';

-- File 8: Thiruvasagam (திருவாசகம்)
-- By Manikkavasagar, 9th century CE (S. Vaiyapuripillai)
-- Some scholars suggest 3rd century, but 9th century more widely accepted
UPDATE works SET
    chronology_start_year = 800,
    chronology_end_year = 900,
    chronology_confidence = 'medium',
    chronology_notes = 'Shaivite devotional poetry by Manikkavasagar. S. Vaiyapuripillai dates to early 9th century CE, noting references to Tevaram hymns of Sambandar, Appar, and Sundarar, use of "very late words," and mention of weekdays. Some scholars suggest earlier dating (3rd century), but 9th century is more widely accepted. Contains 658 poems full of visionary experience and divine love. Forms 8th Thirumurai along with Thirukovayar.'
WHERE work_name LIKE '%திருவாசகம்%' OR work_name LIKE '%Thiruvasagam%';

-- File 8: Thirukovayar (திருக்கோவையார்)
-- By Manikkavasagar, 9th century CE
UPDATE works SET
    chronology_start_year = 800,
    chronology_end_year = 900,
    chronology_confidence = 'medium',
    chronology_notes = 'Shaivite devotional poetry by Manikkavasagar, 9th century CE. Contains 400 poems. Compiled with Thiruvasagam as 8th Thirumurai. Same author and period as Thiruvasagam. Dating based on attribution to Manikkavasagar and inclusion in Thirumurai canonical collection compiled in 10th-12th century.'
WHERE work_name LIKE '%திருக்கோவையார்%' OR work_name LIKE '%Thirukovayar%';

-- File 9: Thiruvisaippa (திருவிசைப்பா)
-- Multiple authors, 10th century CE
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1000,
    chronology_confidence = 'medium',
    chronology_notes = 'Part of 9th Thirumurai, Shaivite devotional poetry by eight authors from 10th century. Authors include Thirumaligai Thevar, Senthanar, Karuvur Thevar, Ponnthuruthi Nambi, and others. Kandarathithar, one contributor, was prince descended from Chola king Parantaka I. Collection discovered in Chidambaram temple during Rajaraja Chola I reign (10th century) and compiled by Nambi Andar Nambi.'
WHERE work_name LIKE '%திருவிசைப்பா%' OR work_name LIKE '%Thiruvisaippa%';

-- File 10: Thirumanthiram (திருமந்திரம்)
-- By Tirumular, highly disputed dating (5th-12th century CE)
-- Extremely wide range due to scholarly disagreement
UPDATE works SET
    chronology_start_year = 200,
    chronology_end_year = 1200,
    chronology_confidence = 'low',
    chronology_notes = 'Shaivite philosophical text by Tirumular. Dating extremely controversial among scholars, ranging from pre-Common Era to 12th century CE. S. Vaiyapuripillai suggests early 8th century based on references to Tevaram hymns, late words, and weekday mentions. Dominic Goodall suggests 11th-12th century based on religious concepts with datable Tamil labels. Some scholars propose ancient core with later interpolations. Over 3,000 verses. Wide dating range reflects fundamental scholarly disagreement and likely layered composition over centuries.'
WHERE work_name LIKE '%திருமந்திரம்%' OR work_name LIKE '%Thirumanthiram%';

-- File 11: Saiva Prabandha Malai
-- 11th-12th century compilation of various Shaivite texts
UPDATE works SET
    chronology_start_year = 1000,
    chronology_end_year = 1200,
    chronology_confidence = 'low',
    chronology_notes = 'Collection of Shaivite devotional texts forming 11th Thirumurai. Compilation dates to 11th-12th century during Chola period. Contains works by multiple authors. Part of Panniru Thirumurai (Twelve Thirumurai) canonical collection compiled by Nambi Andar Nambi. Dating based on compilation period rather than original composition dates of individual texts, which may vary.'
WHERE work_name LIKE '%சைவ பிரபந்த மாலை%' OR work_name LIKE '%Saiva Prabandha Malai%';

-- File 12: Periya Puranam (பெரியபுராணம்)
-- By Sekkizhar, 1133-1150 CE under Kulottunga II
UPDATE works SET
    chronology_start_year = 1133,
    chronology_end_year = 1150,
    chronology_confidence = 'high',
    chronology_notes = 'Hagiography of 63 Nayanar (Shaivite) saints by Sekkizhar, composed 12th century CE (1133-1150) during reign of Chola king Kulottunga II. Contains 4,286 verses. Forms 12th and final Thirumurai. Well-documented composition under royal patronage. One of the great classics of Tamil literature, providing invaluable historical information about Tamil Shaiva Bhakti movement and its saint-poets.'
WHERE work_name LIKE '%பெரியபுராணம்%' OR work_name LIKE '%Periya Puranam%';

-- =============================================================================
-- NAALAYIRA DIVYA PRABANDHAM - VAISHNAVITE DEVOTIONAL LITERATURE
-- =============================================================================

-- All 24 works of Naalayira Divya Prabandham
-- Composed by Alvars (6th-9th century), compiled 9th-10th century by Nathamuni
UPDATE works SET
    chronology_start_year = 600,
    chronology_end_year = 900,
    chronology_confidence = 'high',
    chronology_notes = 'Part of Naalayira Divya Prabandham (4,000 Divine Verses), Vaishnavite devotional poetry. Composed by 12 Alvars (Vaishnavite saint-poets) between 6th-9th centuries CE. Collection compiled in 9th-10th century by Nathamuni. Alvars were contemporary with Nayanars (Shaivite poets) during Tamil Bhakti movement. Well-documented dating through historical records, temple inscriptions, and literary cross-references. Represents Tamil Vaishnavite parallel to Shaivite Tevaram tradition.'
WHERE work_name_tamil LIKE '%திவ்ய பிரபந்தம்%'
   OR work_name LIKE '%Divya Prabandham%'
   OR work_name IN (
       'Periyalvar Thirumozhi', 'Thiruppavai', 'Nachiar Thirumozhi',
       'Perumal Thirumozhi', 'Thiruchanda Viruttam', 'Thirumalai',
       'Thiruppallandu', 'Amalanadipiran', 'Kanni Nun Siruthambu',
       'Peria Thirumozhi', 'Thirukurunthandagam', 'Thirunedunthandagam',
       'Thiruviruttam', 'Periya Thirumadal', 'Siriya Thirumadal',
       'Ramanuja Nootrandhadhi', 'Thiruvoymozhi', 'Peria Thiruvandhadhi',
       'Iyarpa', 'Thiruviruththam', 'Thiruvaimozhi',
       'Thiruvachiriyam', 'Periya Thiruvandhadhi', 'Mummanikkovai'
   );

-- =============================================================================
-- OTHER DEVOTIONAL LITERATURE
-- =============================================================================

-- Thiruppugazh (திருப்புகழ்)
-- By Arunagirinathar, 15th century CE (1370-1450 CE)
-- Murugan devotional poetry
UPDATE works SET
    chronology_start_year = 1370,
    chronology_end_year = 1450,
    chronology_confidence = 'high',
    chronology_notes = 'Devotional poetry to Murugan by Arunagirinathar, 15th century CE (1370-1450). Major work of Tamil Murugan worship tradition. Well-documented authorship and period. Represents later medieval Tamil devotional literature with complex metrical patterns and sophisticated Tamil literary techniques. Important pilgrimage site connections documented in the work.'
WHERE work_name = 'Thiruppugazh';

-- Thembavani (தேம்பாவணி)
-- By Constantine Joseph Beschi (Veeramamunivar), 1726 CE
-- Christian epic in Tamil
UPDATE works SET
    chronology_start_year = 1726,
    chronology_end_year = 1726,
    chronology_confidence = 'high',
    chronology_notes = 'Christian epic in Tamil by Italian Jesuit Constantine Joseph Beschi (Tamil name: Veeramamunivar), composed 1726 CE in 18th century. Adapts Tamil epic conventions to tell life of St. Joseph. Precisely dated work demonstrating Christian adaptation of Tamil literary forms. Important example of Tamil Christian literature and cross-cultural religious expression in colonial period.'
WHERE work_name = 'Thembavani';

-- Seerapuranam (சீறாப்புராணம்)
-- By Umaru Pulavar, 17th century CE (1642-1703 CE)
-- Islamic literature narrating life of Prophet Muhammad
UPDATE works SET
    chronology_start_year = 1642,
    chronology_end_year = 1703,
    chronology_confidence = 'high',
    chronology_notes = 'Islamic Tamil literature by Umaru Pulavar (4 Dec 1642 - 28 July 1703), narrating life and teachings of Prophet Muhammad. Commissioned by Seethakathi Vallal (1650-1713). Precisely dated to 17th century based on documented lifespan of author and patron. Most significant contribution to Tamil Islamic literature. Demonstrates adaptation of Tamil literary forms to Islamic religious narrative. Note: Britannica mistakenly dates to late 18th-early 19th century, contradicting better-documented 17th century evidence.'
WHERE work_name = 'Seerapuranam';

-- Verification query to check updates
-- SELECT work_name, work_name_tamil, chronology_start_year, chronology_end_year,
--        chronology_confidence, chronology_notes
-- FROM works
-- ORDER BY chronology_start_year;
