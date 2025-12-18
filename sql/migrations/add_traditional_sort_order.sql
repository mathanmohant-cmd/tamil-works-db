-- Migration: Add traditional_sort_order column to works table
-- Date: 2025-12-17
-- Description: Adds a traditional_sort_order column to maintain chronological ordering of Tamil literary works

-- Add the column
ALTER TABLE works ADD COLUMN traditional_sort_order INTEGER;

-- Update existing works with traditional chronological order
-- 1. Tolkappiyam (தொல்காப்பியம்) - BCE 300-200, earliest Tamil grammar
-- 2. Sangam Literature (சங்க இலக்கியம்) - BCE 300 - CE 300
-- 3. Thirukkural (திருக்குறள்) - CE 200-400, ethical text
-- 4. Silapathikaram (சிலப்பதிகாரம்) - CE 100-300, epic
-- 5. Kambaramayanam (கம்பராமாயணம்) - CE 12th century, medieval epic

UPDATE works SET traditional_sort_order = 1 WHERE work_name = 'Tolkappiyam';
UPDATE works SET traditional_sort_order = 2 WHERE work_name = 'Sangam Literature';
UPDATE works SET traditional_sort_order = 3 WHERE work_name = 'Thirukkural';
UPDATE works SET traditional_sort_order = 4 WHERE work_name = 'Silapathikaram';
UPDATE works SET traditional_sort_order = 5 WHERE work_name = 'Kambaramayanam';

-- Verify the update
SELECT work_id, work_name, work_name_tamil, period, traditional_sort_order
FROM works
ORDER BY traditional_sort_order;
