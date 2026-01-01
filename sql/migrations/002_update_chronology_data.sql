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

-- File 9: Thiruvisaippa (திருவிசைப்பா) and Ninth Thirumurai (ஒன்பதாம் திருமுறை)
-- Multiple authors, 10th century CE
UPDATE works SET
    chronology_start_year = 900,
    chronology_end_year = 1000,
    chronology_confidence = 'medium',
    chronology_notes = 'Part of 9th Thirumurai (Thiruvisaippa), Shaivite devotional poetry by eight authors from 10th century. Authors include Thirumaligai Thevar, Senthanar, Karuvur Thevar, Ponnthuruthi Nambi, Kandarathithar, Puruttothaman Nambi, Venattadikal, and Thiruvaliya Mudhanar. Kandarathithar was prince descended from Chola king Parantaka I. Collection discovered in Chidambaram temple during Rajaraja Chola I reign (10th century) and compiled by Nambi Andar Nambi.'
WHERE chronology_start_year IS NULL
  AND (work_name LIKE '%திருவிசைப்பா%' OR work_name LIKE '%Thiruvisaippa%'
      OR work_id IN (SELECT wc.work_id FROM work_collections wc WHERE wc.collection_id IN (3219, 32191))
      OR author_tamil IN (
          'திருமாளிகைத் தேவர்', 'சேந்தனார்', 'கருவூர்த் தேவர்',
          'பூந்துருத்தி நம்பி காடநம்பி', 'கண்டராதித்தர்', 'வேணாட்டடிகள்',
          'திருவாலியமுதனார்', 'புருடோத்தம நம்பி', 'சேதிராயர்'
      ));

-- File 10: Thirumanthiram (திருமந்திரம்)
-- By Tirumular, highly disputed dating (5th-12th century CE)
-- Extremely wide range due to scholarly disagreement
UPDATE works SET
    chronology_start_year = 200,
    chronology_end_year = 1200,
    chronology_confidence = 'low',
    chronology_notes = 'Shaivite philosophical text by Tirumular. Dating extremely controversial among scholars, ranging from pre-Common Era to 12th century CE. S. Vaiyapuripillai suggests early 8th century based on references to Tevaram hymns, late words, and weekday mentions. Dominic Goodall suggests 11th-12th century based on religious concepts with datable Tamil labels. Some scholars propose ancient core with later interpolations. Over 3,000 verses. Wide dating range reflects fundamental scholarly disagreement and likely layered composition over centuries.'
WHERE work_name LIKE '%திருமந்திரம்%' OR work_name LIKE '%Thirumanthiram%';

-- File 11: Saiva Prabandha Malai (Eleventh Thirumurai)
-- Individual works composed 6th-9th century, compiled 11th-12th century by Nambi Andar Nambi
-- IMPORTANT: Using composition dates, not compilation dates

-- Karaikkal Ammaiyar (காரைக்கால் அம்மையார்) - 6th century, earliest Nayanar
UPDATE works SET
    chronology_start_year = 500,
    chronology_end_year = 600,
    chronology_confidence = 'medium',
    chronology_notes = 'Shaivite devotional poetry by Karaikkal Ammaiyar (காரைக்கால் அம்மையார்), one of earliest Nayanar saints. Composed approximately 6th century CE (~550 CE). One of few female Tamil saint-poets. Pre-dates Tevaram poets (Sambandar, Appar, Sundarar). Part of Eleventh Thirumurai (Saiva Prabandha Malai) collection compiled in 11th-12th century. Dating based on hagiographical records and literary analysis.'
WHERE author_tamil LIKE '%காரைக்கால் அம்மையார்%';

-- Other Eleventh Thirumurai works - 6th-9th century composition
-- By various Nayanars and saints (Nakkiradevar, Cheraman Perumal, etc.)
UPDATE works SET
    chronology_start_year = 600,
    chronology_end_year = 900,
    chronology_confidence = 'medium',
    chronology_notes = 'Part of Eleventh Thirumurai (Saiva Prabandha Malai - சைவப் பிரபந்த மாலை), Shaivite devotional poetry. Individual works composed 6th-9th centuries CE during Tamil Shaiva Bhakti movement by various Nayanar saints and devotees (Nakkiradevar, Cheraman Perumal, Pattinatthadiyar, Thirumaligai Thevar, and others). Collection compiled in 11th-12th century by Nambi Andar Nambi as part of Panniru Thirumurai (Twelve Thirumurai). Dating based on hagiographical records in Periya Puranam (12th century), historical inscriptions, and literary analysis. Note: Dates reflect original composition period, not later compilation period.'
WHERE chronology_start_year IS NULL
  AND (work_id IN (
      SELECT wc.work_id
      FROM work_collections wc
      WHERE wc.collection_id = 32118  -- Eleventh Thirumurai collection
  ) OR work_name LIKE '%சைவ பிரபந்த மாலை%' OR work_name LIKE '%Saiva Prabandha Malai%'
  OR author_tamil IN (
      'நக்கீரதேவ நாயனார்', 'நம்பியாண்டார் நம்பி', 'நம்பியாண்டார் நம்பிகள்', 'பட்டினத்து அடிகள்',
      'கபில தேவ நாயனார்', 'கபிலதேவ நாயனார்', 'சேரமான் பெருமாள் நாயனார்', 'சேரமான் பெருமாள்',
      'அதிரா அடிகள்', 'இளம் பெருமாள் அடிகள்', 'ஐயடிகள் காடவர் கோன் நாயனார்',
      'கல்லாட தேவ நாயனார்', 'சிவபெருமான் திருஅந்தாதி', 'திருஆலவாய் உடையார்'
  ));

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
-- Composed by 12 Alvars (6th-9th century), compiled 9th-10th century by Nathamuni
-- =============================================================================

-- FIRST THREE ALVARS (Mudhal Alvars) - 7th century CE
-- Poigai Alvar (பொய்கை ஆழ்வார்) - 7th century
UPDATE works SET
    chronology_start_year = 600,
    chronology_end_year = 700,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Poigai Alvar (பொய்கை ஆழ்வார்), one of first three Alvars (Mudhal Alvars). Composed in 7th century CE during Tamil Bhakti movement. Part of Naalayira Divya Prabandham compiled by Nathamuni in 9th-10th century. Dating established through historical records, temple inscriptions, and literary cross-references. Contemporary with Bhoothathalvar and Pey Alvar.'
WHERE author_tamil = 'பொய்கை ஆழ்வார்';

-- Bhoothathalvar (பூதத்தாழ்வார்) - 7th century
UPDATE works SET
    chronology_start_year = 600,
    chronology_end_year = 700,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Bhoothathalvar (பூதத்தாழ்வார்), one of first three Alvars (Mudhal Alvars). Composed in 7th century CE during Tamil Bhakti movement. Part of Naalayira Divya Prabandham. Contemporary with Poigai Alvar and Pey Alvar.'
WHERE author_tamil = 'பூதத்தாழ்வார்';

-- Pey Alvar (பேயாழ்வார்) - 7th century
UPDATE works SET
    chronology_start_year = 600,
    chronology_end_year = 700,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Pey Alvar (பேயாழ்வார்), one of first three Alvars (Mudhal Alvars). Composed in 7th century CE during Tamil Bhakti movement. Part of Naalayira Divya Prabandham. Contemporary with Poigai Alvar and Bhoothathalvar.'
WHERE author_tamil = 'பேயாழ்வார்';

-- MIDDLE PERIOD ALVARS
-- Thirumalisai Alvar (திருமழிசை ஆழ்வார்) - 7th-8th century
UPDATE works SET
    chronology_start_year = 650,
    chronology_end_year = 750,
    chronology_confidence = 'medium',
    chronology_notes = 'Vaishnavite devotional poetry by Thirumalisai Alvar (திருமழிசை ஆழ்வார்). Composed in late 7th - early 8th century CE. Part of Naalayira Divya Prabandham. Known for Nanmugan Thiruvandhadhi and Thiruchchanda Viruttam. Dating based on literary references and position in Alvar chronology.'
WHERE author_tamil LIKE '%திருமழிசை%';

-- LATER ALVARS - 8th-9th century CE
-- Nammalvar (நம்மாழ்வார்) - 8th-9th century, most prolific Alvar
UPDATE works SET
    chronology_start_year = 750,
    chronology_end_year = 900,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Nammalvar (நம்மாழ்வார்), most prolific and revered Alvar. Composed in 8th-9th century CE. Contributed 1,102 verses to Naalayira Divya Prabandham, including Thiruvaimozhi (1,000 verses), Thiruviruttam, Thiruvasiriyam, and Periya Thiruvandhadhi. Dating well-established through historical records and commentary traditions. Considered supreme among Alvars in Sri Vaishnava tradition.'
WHERE author_tamil LIKE '%நம்மாழ்%';

-- Periyalvar (பெரியாழ்வார்) - 9th century
UPDATE works SET
    chronology_start_year = 800,
    chronology_end_year = 900,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Periyalvar (பெரியாழ்வார்). Composed in 9th century CE. Part of Naalayira Divya Prabandham. Father/guru of Andal. Contributed Periyalvar Thirumozhi (Thiruppallandu) and other works celebrating child Krishna.'
WHERE author_tamil LIKE '%பெரியாழ்%' OR author = 'Periyalvar';

-- Andal (ஆண்டாள்) - 9th century, only female Alvar
UPDATE works SET
    chronology_start_year = 800,
    chronology_end_year = 900,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Andal (ஆண்டாள்), only female Alvar. Composed in 9th century CE. Daughter/disciple of Periyalvar. Famous for Thiruppavai (30 verses) and Nachiar Thirumozhi (143 verses). Revered as incarnation of Bhudevi in Sri Vaishnava tradition. Her works emphasize intimate devotion to Vishnu/Krishna.'
WHERE author_tamil = 'ஆண்டாள்' OR author = 'Andal';

-- Kulasekara Alvar (குலசேகர ஆழ்வார்) - 9th century
UPDATE works SET
    chronology_start_year = 800,
    chronology_end_year = 900,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Kulasekara Alvar (குலசேகர ஆழ்வார்). Composed in 9th century CE. Chera king who became Alvar. Part of Naalayira Divya Prabandham. Known for Perumal Thirumozhi expressing royal devotion to Vishnu.'
WHERE author_tamil LIKE '%குலசேகர%' OR author LIKE '%Kulasekara%';

-- Thondaradippodi Alvar (தொண்டரடிப்பொடி ஆழ்வார்) - 9th century
UPDATE works SET
    chronology_start_year = 800,
    chronology_end_year = 900,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Thondaradippodi Alvar (தொண்டரடிப்பொடி ஆழ்வார்). Composed in 9th century CE. Part of Naalayira Divya Prabandham. Known for Thirumalai and Thiruppalliyezhuchi expressing intimate devotional style.'
WHERE author_tamil LIKE '%தொண்டரடிப்%' OR author LIKE '%Thondaradippodi%';

-- Thiruppan Alvar (திருப்பாணாழ்வார்) - 9th century
UPDATE works SET
    chronology_start_year = 800,
    chronology_end_year = 900,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Thiruppan Alvar (திருப்பாணாழ்வார்). Composed in 9th century CE. Part of Naalayira Divya Prabandham. Famous for Amalanadipiran (10 verses) expressing intense devotional experience.'
WHERE author_tamil LIKE '%திருப்பாண%' OR author LIKE '%Thiruppan%';

-- Madhurakavi Alvar (மதுரகவி ஆழ்வார்) - 9th century
UPDATE works SET
    chronology_start_year = 800,
    chronology_end_year = 900,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Madhurakavi Alvar (மதுரகவி ஆழ்வார்). Composed in 9th century CE. Only Alvar who sang exclusively about another Alvar (Nammalvar). Part of Naalayira Divya Prabandham. Known for Kanni Nun Siruthambu (11 verses) celebrating his guru Nammalvar.'
WHERE author_tamil LIKE '%மதுரகவி%' OR author LIKE '%Madhurakavi%';

-- Thirumangai Alvar (திருமங்கை ஆழ்வார்) - 7th-9th century (disputed)
UPDATE works SET
    chronology_start_year = 700,
    chronology_end_year = 900,
    chronology_confidence = 'medium',
    chronology_notes = 'Vaishnavite devotional poetry by Thirumangai Alvar (திருமங்கை ஆழ்வார்). Dating disputed, ranging from 7th to 9th century CE. Contributed significant portions to Naalayira Divya Prabandham including Periya Thirumozhi (1,084 verses), Thirukurunthandagam, and Thirunedunthandagam. Commander-general who became Alvar. Scholarly debate on precise dating continues.'
WHERE author_tamil LIKE '%திருமங்கை%' OR author LIKE '%Thirumangai%';

-- Thiruvrangatthu Amudhanar (திருவரங்கத்து அமுதனார்) - 12th century, disciple of Ramanuja
UPDATE works SET
    chronology_start_year = 1100,
    chronology_end_year = 1200,
    chronology_confidence = 'high',
    chronology_notes = 'Vaishnavite devotional poetry by Thiruvrangatthu Amudhanar (திருவரங்கத்து அமுதனார்), disciple of Ramanuja. Composed in 12th century CE. Latest contributor to Naalayira Divya Prabandham tradition. Known for Ramanuja Nootrandhadhi (108 verses praising Ramanuja). Well-documented dating through connection to Ramanuja (1017-1137 CE).'
WHERE author_tamil LIKE '%அமுதனார்%' OR author LIKE '%Amudhanar%';

-- CATCH-ALL: Remaining Naalayira Divya Prabandham works (if any missed by author-specific updates)
-- Composed by Alvars (6th-9th century), compiled 9th-10th century by Nathamuni
UPDATE works SET
    chronology_start_year = 600,
    chronology_end_year = 900,
    chronology_confidence = 'high',
    chronology_notes = 'Part of Naalayira Divya Prabandham (4,000 Divine Verses), Vaishnavite devotional poetry. Composed by 12 Alvars (Vaishnavite saint-poets) between 6th-9th centuries CE. Collection compiled in 9th-10th century by Nathamuni. Alvars were contemporary with Nayanars (Shaivite poets) during Tamil Bhakti movement. Well-documented dating through historical records, temple inscriptions, and literary cross-references. Represents Tamil Vaishnavite parallel to Shaivite Tevaram tradition.'
WHERE chronology_start_year IS NULL
  AND (work_name_tamil LIKE '%திவ்ய பிரபந்தம்%'
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
       ));

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
