import re
from html.parser import HTMLParser

class PoemExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.poems = []
        self.current_poem = None
        self.in_poem = False
        self.poem_count = 0
        
    def handle_starttag(self, tag, attrs):
        pass
    
    def handle_endtag(self, tag):
        pass
    
    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        
        # Check if this is a poem header (starts with #)
        if data.startswith('#'):
            # Save previous poem if exists
            if self.current_poem:
                self.poems.append('\n'.join(self.current_poem))
                self.poem_count += 1
            
            # Start new poem
            self.current_poem = [data]
            self.in_poem = True
        elif self.in_poem and self.current_poem:
            # This is a verse line
            self.current_poem.append(data)

# Read the HTML file
with open(r'C:\Users\t_mat\Downloads\அகநானூறு _ சங்கம்பீடியா.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Remove HTML entities and tags
html_content = html_content.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
html_content = html_content.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')

# Remove most HTML tags but keep the content
html_content = re.sub(r'<[^>]+>', '', html_content)

# Extract lines starting with #
lines = html_content.split('\n')
poems_text = []
current_poem = []

for line in lines:
    line = line.strip()
    
    if not line:
        continue
    
    # Check if line starts with a poem header
    if re.match(r'^#\d+\s', line):
        # Save previous poem if exists
        if current_poem:
            poems_text.append('\n'.join(current_poem))
        
        # Start new poem
        current_poem = [line]
    elif current_poem:
        # Add to current poem if it's not just whitespace/HTML artifacts
        if line and not line.startswith('<') and len(line) > 0:
            current_poem.append(line)

# Don't forget the last poem
if current_poem:
    poems_text.append('\n'.join(current_poem))

# Write to output file
output_path = r'C:\Users\t_mat\அகநானூறு_poems.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(poems_text))

print(f"Total poems extracted: {len(poems_text)}")
print(f"Output file created at: {output_path}")
