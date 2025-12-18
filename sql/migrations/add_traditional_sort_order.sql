-- Migration: Add traditional_sort_order column to works table
-- Date: 2025-12-17
-- Description: Adds a traditional_sort_order column to maintain chronological ordering of Tamil literary works

-- Add the column
ALTER TABLE works ADD COLUMN traditional_sort_order INTEGER;

-- Note: Values for traditional_sort_order should be set by the parser scripts when importing works.
-- The parsers will assign:
-- 1. Tolkappiyam (தொல்காப்பியம்) - BCE 300-200, earliest Tamil grammar
-- 2. Sangam Literature (சங்க இலக்கியம்) - BCE 300 - CE 300
-- 3. Thirukkural (திருக்குறள்) - CE 200-400, ethical text
-- 4. Silapathikaram (சிலப்பதிகாரம்) - CE 100-300, epic
-- 5. Kambaramayanam (கம்பராமாயணம்) - CE 12th century, medieval epic
