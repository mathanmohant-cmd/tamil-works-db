-- Update canonical_order for all works
-- Traditional Tamil literary canon ordering

-- Tolkappiyam (oldest grammar text)
UPDATE works SET canonical_order = 100 WHERE work_name = 'Tolkappiyam';

-- Sangam Literature (200-217)
UPDATE works SET canonical_order = 200 WHERE work_name = 'Kurunthokai';
UPDATE works SET canonical_order = 201 WHERE work_name = 'Natrrinai';
UPDATE works SET canonical_order = 202 WHERE work_name = 'Ainkurunuru';
UPDATE works SET canonical_order = 203 WHERE work_name = 'Pathitrupathu';
UPDATE works SET canonical_order = 204 WHERE work_name = 'Paripaadal';
UPDATE works SET canonical_order = 205 WHERE work_name = 'Kalithokai';
UPDATE works SET canonical_order = 206 WHERE work_name = 'Aganaanuru';
UPDATE works SET canonical_order = 207 WHERE work_name = 'Puranaanuru';
UPDATE works SET canonical_order = 208 WHERE work_name = 'Pattinappaalai';
UPDATE works SET canonical_order = 209 WHERE work_name = 'Perumpanaatruppadai';
UPDATE works SET canonical_order = 210 WHERE work_name = 'Mullaippaattu';
UPDATE works SET canonical_order = 211 WHERE work_name = 'Madurai kanchi';
UPDATE works SET canonical_order = 212 WHERE work_name = 'Nedunalvaadai';
UPDATE works SET canonical_order = 213 WHERE work_name = 'Kurinchippaattu';
UPDATE works SET canonical_order = 214 WHERE work_name = 'Porunararruppadai';
UPDATE works SET canonical_order = 215 WHERE work_name = 'Sirupaanaatruppadai';
UPDATE works SET canonical_order = 216 WHERE work_name = 'Malaipadukataam';
UPDATE works SET canonical_order = 217 WHERE work_name = 'Thirumurugatruppadai';

-- Post-Sangam works
UPDATE works SET canonical_order = 260 WHERE work_name = 'Thirukkural';
UPDATE works SET canonical_order = 280 WHERE work_name = 'Silapathikaram';

-- Medieval epic
UPDATE works SET canonical_order = 400 WHERE work_name = 'Kambaramayanam';

-- Verify update
SELECT work_name, canonical_order
FROM works
WHERE canonical_order IS NOT NULL
ORDER BY canonical_order;
