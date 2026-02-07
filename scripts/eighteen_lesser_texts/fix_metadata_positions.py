#!/usr/bin/env python3
"""Fix position_in_collection and filenames to match actual files"""
from pathlib import Path

# Read the metadata file
metadata_file = Path(__file__).parent / 'shared' / 'work_metadata.py'
content = metadata_file.read_text(encoding='utf-8')

# Fix the remaining 7 works
fixes = [
    # ('201012', '12', "'12-ஆசாரக்கோவை'", '201013', '13', "'13-ஆசாரக்கோவை'"),  # Asarakkovai
    ('201012', '12', "'12-ஆசாரக்கோவை'", '201013', '13', "'13-ஆசாரக்கோவை'"),  # Asarakkovai
    ('201013', '13', "'13-பழமொழி நானூறு'", '201014', '14', "'14-பழமொழி நானூறு'"),  # Pazhamozhi Nanuru
    ('201014', '14', "'14-சிறுபஞ்சமூலம்'", '201015', '15', "'15-சிறுபஞ்சமூலம்'"),  # Sirupanchamoolam
    ('201015', '15', "'15-முதுமொழிக்காஞ்சி'", '201016', '16', "'16-முதுமொழிக்காஞ்சி'"),  # Muthumozhikkanchi
    ('201016', '16', "'16-ஏலாதி'", '201017', '17', "'17-ஏலாதி'"),  # Elathi
    ('201017', '17', "'17-கைந்நிலை'", '201018', '18', "'18-கைந்நிலை'"),  # Kainnilai
    ('201018', '18', "'18-திருக்குறள்'", '201011', '11', "'11-திருக்குறள்'"),  # Thirukkural
]

for old_canonical, old_pos, old_filename, new_canonical, new_pos, new_filename in fixes:
    # Replace canonical_order
    content = content.replace(f"'canonical_order': {old_canonical},", f"'canonical_order': {new_canonical},")
    # Replace position_in_collection
    content = content.replace(f"'position_in_collection': {old_pos},", f"'position_in_collection': {new_pos},")
    # Replace filename
    content = content.replace(f"'filename': {old_filename}", f"'filename': {new_filename}")

# Write back
metadata_file.write_text(content, encoding='utf-8')
print("✓ Fixed all 8 work positions and filenames")
