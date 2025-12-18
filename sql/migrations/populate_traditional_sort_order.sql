-- Migration: Populate traditional_sort_order for existing works
-- Date: 2025-12-17
-- Description: Updates traditional_sort_order values for all existing works based on traditional chronological ordering

-- Update traditional_sort_order based on work_id to traditional_sort_order mapping
UPDATE works SET traditional_sort_order = 1 WHERE work_id = 1;
UPDATE works SET traditional_sort_order = 2 WHERE work_id = 3;
UPDATE works SET traditional_sort_order = 3 WHERE work_id = 2;
UPDATE works SET traditional_sort_order = 4 WHERE work_id = 4;
UPDATE works SET traditional_sort_order = 5 WHERE work_id = 8;
UPDATE works SET traditional_sort_order = 6 WHERE work_id = 9;
UPDATE works SET traditional_sort_order = 7 WHERE work_id = 7;
UPDATE works SET traditional_sort_order = 8 WHERE work_id = 5;
UPDATE works SET traditional_sort_order = 9 WHERE work_id = 6;
UPDATE works SET traditional_sort_order = 10 WHERE work_id = 10;
UPDATE works SET traditional_sort_order = 11 WHERE work_id = 11;
UPDATE works SET traditional_sort_order = 12 WHERE work_id = 12;
UPDATE works SET traditional_sort_order = 13 WHERE work_id = 13;
UPDATE works SET traditional_sort_order = 14 WHERE work_id = 14;
UPDATE works SET traditional_sort_order = 15 WHERE work_id = 15;
UPDATE works SET traditional_sort_order = 16 WHERE work_id = 16;
UPDATE works SET traditional_sort_order = 17 WHERE work_id = 19;
UPDATE works SET traditional_sort_order = 18 WHERE work_id = 17;
UPDATE works SET traditional_sort_order = 19 WHERE work_id = 18;
UPDATE works SET traditional_sort_order = 20 WHERE work_id = 20;
UPDATE works SET traditional_sort_order = 21 WHERE work_id = 21;
UPDATE works SET traditional_sort_order = 22 WHERE work_id = 22;

-- Verify the update
SELECT work_id, work_name, work_name_tamil, traditional_sort_order
FROM works
ORDER BY traditional_sort_order;
