#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

input_file = r'C:\Claude\Projects\tamil-works-db\Tamil-Source-TamilConcordence\3_சங்க_இலக்கியம்_பதினெண்கீழ்க்கணக்கு\1-நாலடியார்.txt'
output_file = r'C:\Claude\Projects\tamil-works-db\scripts\naladiyar_iyals.txt'

with open(input_file, 'r', encoding='utf-8') as f:
    with open(output_file, 'w', encoding='utf-8') as out:
        for i, line in enumerate(f, 1):
            # Look for lines with number followed by Tamil text (Iyal markers)
            if re.match(r'^\d+\s+[\u0B80-\u0BFF]', line):
                out.write(f'{i:5d}: {line}')

print(f"Iyals written to {output_file}")
