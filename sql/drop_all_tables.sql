-- Drop all tables and views for Tamil Literature Database
-- Run this before running complete_setup.sql to ensure clean state

-- Drop views first (they depend on tables)
DROP VIEW IF EXISTS word_details CASCADE;
DROP VIEW IF EXISTS verse_hierarchy CASCADE;

-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS cross_references CASCADE;
DROP TABLE IF EXISTS commentaries CASCADE;
DROP TABLE IF EXISTS words CASCADE;
DROP TABLE IF EXISTS lines CASCADE;
DROP TABLE IF EXISTS verses CASCADE;
DROP TABLE IF EXISTS sections CASCADE;
DROP TABLE IF EXISTS work_collections CASCADE;
DROP TABLE IF EXISTS collections CASCADE;
DROP TABLE IF EXISTS admin_users CASCADE;
DROP TABLE IF EXISTS works CASCADE;

-- Drop sequences (they will be recreated by complete_setup.sql)
DROP SEQUENCE IF EXISTS works_work_id_seq CASCADE;
DROP SEQUENCE IF EXISTS collections_collection_id_seq CASCADE;
DROP SEQUENCE IF EXISTS admin_users_user_id_seq CASCADE;
DROP SEQUENCE IF EXISTS sections_section_id_seq CASCADE;
DROP SEQUENCE IF EXISTS verses_verse_id_seq CASCADE;
DROP SEQUENCE IF EXISTS lines_line_id_seq CASCADE;
DROP SEQUENCE IF EXISTS words_word_id_seq CASCADE;
DROP SEQUENCE IF EXISTS commentaries_commentary_id_seq CASCADE;
DROP SEQUENCE IF EXISTS cross_references_reference_id_seq CASCADE;
