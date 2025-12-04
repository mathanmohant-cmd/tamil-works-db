#!/usr/bin/env python3
"""
Generate ER Diagram for Tamil Literary Works Database
Creates a visual diagram showing all tables and relationships
"""

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("Graphviz not available. Attempting alternative method...")

import os

def create_er_diagram_graphviz():
    """Create ER diagram using Graphviz"""

    # Create a new directed graph
    dot = Digraph(comment='Tamil Literary Works Database ER Diagram')
    dot.attr(rankdir='TB', splines='ortho', nodesep='0.5', ranksep='0.8')
    dot.attr('node', shape='plaintext', fontname='Arial', fontsize='10')

    # Define table HTML-like labels
    works_label = '''<
    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="lightblue">
    <TR><TD COLSPAN="2" BGCOLOR="darkblue"><FONT COLOR="white"><B>WORKS</B></FONT></TD></TR>
    <TR><TD ALIGN="LEFT"><B>PK</B></TD><TD ALIGN="LEFT">work_id</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">work_name</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">work_name_tamil</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">period</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">author</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">author_tamil</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">description</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">created_at</TD></TR>
    </TABLE>>'''

    sections_label = '''<
    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="lightgreen">
    <TR><TD COLSPAN="2" BGCOLOR="darkgreen"><FONT COLOR="white"><B>SECTIONS</B></FONT></TD></TR>
    <TR><TD ALIGN="LEFT"><B>PK</B></TD><TD ALIGN="LEFT">section_id</TD></TR>
    <TR><TD ALIGN="LEFT"><B>FK</B></TD><TD ALIGN="LEFT">work_id</TD></TR>
    <TR><TD ALIGN="LEFT"><B>FK</B></TD><TD ALIGN="LEFT">parent_section_id</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">level_type</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">level_type_tamil</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">section_number</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">section_name</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">section_name_tamil</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">description</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">sort_order</TD></TR>
    </TABLE>>'''

    verses_label = '''<
    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="lightyellow">
    <TR><TD COLSPAN="2" BGCOLOR="orange"><FONT COLOR="white"><B>VERSES</B></FONT></TD></TR>
    <TR><TD ALIGN="LEFT"><B>PK</B></TD><TD ALIGN="LEFT">verse_id</TD></TR>
    <TR><TD ALIGN="LEFT"><B>FK</B></TD><TD ALIGN="LEFT">work_id</TD></TR>
    <TR><TD ALIGN="LEFT"><B>FK</B></TD><TD ALIGN="LEFT">section_id</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">verse_number</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">verse_type</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">verse_type_tamil</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">meter</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">total_lines</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">sort_order</TD></TR>
    </TABLE>>'''

    lines_label = '''<
    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="lightpink">
    <TR><TD COLSPAN="2" BGCOLOR="crimson"><FONT COLOR="white"><B>LINES</B></FONT></TD></TR>
    <TR><TD ALIGN="LEFT"><B>PK</B></TD><TD ALIGN="LEFT">line_id</TD></TR>
    <TR><TD ALIGN="LEFT"><B>FK</B></TD><TD ALIGN="LEFT">verse_id</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">line_number</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">line_text</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">line_text_transliteration</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">line_text_translation</TD></TR>
    </TABLE>>'''

    words_label = '''<
    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="lavender">
    <TR><TD COLSPAN="2" BGCOLOR="purple"><FONT COLOR="white"><B>WORDS</B></FONT></TD></TR>
    <TR><TD ALIGN="LEFT"><B>PK</B></TD><TD ALIGN="LEFT">word_id</TD></TR>
    <TR><TD ALIGN="LEFT"><B>FK</B></TD><TD ALIGN="LEFT">line_id</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">word_position</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">word_text</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">word_text_transliteration</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">word_root</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">word_type</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">sandhi_split</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">meaning</TD></TR>
    </TABLE>>'''

    commentaries_label = '''<
    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="lightcyan">
    <TR><TD COLSPAN="2" BGCOLOR="teal"><FONT COLOR="white"><B>COMMENTARIES</B></FONT></TD></TR>
    <TR><TD ALIGN="LEFT"><B>PK</B></TD><TD ALIGN="LEFT">commentary_id</TD></TR>
    <TR><TD ALIGN="LEFT"><B>FK</B></TD><TD ALIGN="LEFT">verse_id</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">commentator</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">commentator_tamil</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">commentary_text</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">commentary_period</TD></TR>
    </TABLE>>'''

    cross_refs_label = '''<
    <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="peachpuff">
    <TR><TD COLSPAN="2" BGCOLOR="chocolate"><FONT COLOR="white"><B>CROSS_REFERENCES</B></FONT></TD></TR>
    <TR><TD ALIGN="LEFT"><B>PK</B></TD><TD ALIGN="LEFT">reference_id</TD></TR>
    <TR><TD ALIGN="LEFT"><B>FK</B></TD><TD ALIGN="LEFT">source_verse_id</TD></TR>
    <TR><TD ALIGN="LEFT"><B>FK</B></TD><TD ALIGN="LEFT">target_verse_id</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">reference_type</TD></TR>
    <TR><TD ALIGN="LEFT"></TD><TD ALIGN="LEFT">notes</TD></TR>
    </TABLE>>'''

    views_label = '''<
    <TABLE BORDER="2" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4" BGCOLOR="wheat" STYLE="dashed">
    <TR><TD COLSPAN="2" BGCOLOR="goldenrod"><FONT COLOR="white"><B>VIEWS</B></FONT></TD></TR>
    <TR><TD ALIGN="LEFT">📊</TD><TD ALIGN="LEFT">verse_hierarchy</TD></TR>
    <TR><TD ALIGN="LEFT">📊</TD><TD ALIGN="LEFT">word_details</TD></TR>
    </TABLE>>'''

    # Add nodes
    dot.node('works', works_label)
    dot.node('sections', sections_label)
    dot.node('verses', verses_label)
    dot.node('lines', lines_label)
    dot.node('words', words_label)
    dot.node('commentaries', commentaries_label)
    dot.node('cross_refs', cross_refs_label)
    dot.node('views', views_label)

    # Add edges (relationships)
    dot.edge('works', 'sections', label='1:N', color='blue', fontsize='9')
    dot.edge('works', 'verses', label='1:N', color='blue', fontsize='9')
    dot.edge('sections', 'sections', label='1:N\nparent-child', color='green', fontsize='9')
    dot.edge('sections', 'verses', label='1:N', color='blue', fontsize='9')
    dot.edge('verses', 'lines', label='1:N', color='blue', fontsize='9')
    dot.edge('verses', 'commentaries', label='1:N', color='blue', fontsize='9')
    dot.edge('verses', 'cross_refs', label='N:N\nsource', color='purple', fontsize='9')
    dot.edge('cross_refs', 'verses', label='N:N\ntarget', color='purple', fontsize='9', style='dashed')
    dot.edge('lines', 'words', label='1:N', color='blue', fontsize='9')

    # Views connections (shown as dashed lines)
    dot.edge('verses', 'views', style='dashed', color='gray', arrowhead='none')
    dot.edge('words', 'views', style='dashed', color='gray', arrowhead='none')

    return dot


def create_simple_ascii_diagram():
    """Create a simple ASCII-based ER diagram"""
    diagram = """
╔═══════════════════════════════════════════════════════════════════════════╗
║         TAMIL LITERARY WORKS DATABASE - ENTITY RELATIONSHIP DIAGRAM       ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌──────────────────┐
│     WORKS        │
├──────────────────┤
│ PK: work_id      │
│     work_name    │
│     author       │
│     period       │
└────────┬─────────┘
         │ 1:N
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│    SECTIONS      │              │     VERSES       │
├──────────────────┤              ├──────────────────┤
│ PK: section_id   │◄──┐          │ PK: verse_id     │◄────┐
│ FK: work_id      │   │          │ FK: work_id      │     │
│ FK: parent_sec_id│───┘ (1:N)    │ FK: section_id   │     │
│     level_type   │              │     verse_number │     │
│     section_name │              │     verse_type   │     │
└────────┬─────────┘              └─────┬──────┬─────┘     │
         │ 1:N                          │      │           │
         └──────────────────────────────┘      │           │
                                                │ 1:N       │
                    ┌───────────────────────────┼───────────┤
                    │                           │           │
                    ▼                           ▼           │
         ┌──────────────────┐         ┌──────────────────┐ │
         │  COMMENTARIES    │         │      LINES       │ │
         ├──────────────────┤         ├──────────────────┤ │
         │ PK: commentary_id│         │ PK: line_id      │ │
         │ FK: verse_id     │         │ FK: verse_id     │ │
         │     commentator  │         │     line_number  │ │
         │     comm_text    │         │     line_text    │ │
         └──────────────────┘         └────────┬─────────┘ │
                                                │ 1:N       │
                                                ▼           │
                                       ┌──────────────────┐ │
                                       │      WORDS       │ │
                                       ├──────────────────┤ │
                                       │ PK: word_id      │ │
                                       │ FK: line_id      │ │
                                       │     word_position│ │
                                       │     word_text    │ │
                                       │     word_root    │ │
                                       │     word_type    │ │
                                       └──────────────────┘ │
                                                            │
                  ┌─────────────────────────────────────────┘
                  │
                  ▼
         ┌──────────────────────┐
         │  CROSS_REFERENCES    │
         ├──────────────────────┤
         │ PK: reference_id     │
         │ FK: source_verse_id  │───┐
         │ FK: target_verse_id  │◄──┘ (N:N self-referencing)
         │     reference_type   │
         └──────────────────────┘

╔═════════════════════════════════════════════════════════════════╗
║                           VIEWS                                  ║
╠═════════════════════════════════════════════════════════════════╣
║  📊 verse_hierarchy - Complete hierarchical path for verses     ║
║  📊 word_details - Words with full context (work, hierarchy)    ║
╚═════════════════════════════════════════════════════════════════╝

LEGEND:
  PK = Primary Key
  FK = Foreign Key
  1:N = One-to-Many relationship
  N:N = Many-to-Many relationship
  ◄── = Relationship direction
"""
    return diagram


def main():
    """Main function to generate ER diagram"""
    import sys
    # Set UTF-8 encoding for output
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')

    print("Generating ER Diagram for Tamil Literary Works Database...")
    print("=" * 70)

    if GRAPHVIZ_AVAILABLE:
        print("\n[OK] Graphviz library found!")
        print("Generating visual diagram...")

        dot = create_er_diagram_graphviz()

        # Save as multiple formats
        output_base = os.path.join(output_dir, 'ER_diagram_visual')

        try:
            dot.render(output_base, format='png', cleanup=True)
            print(f"[OK] PNG diagram saved: {output_base}.png")
        except Exception as e:
            print(f"[FAIL] PNG generation failed: {e}")

        try:
            dot.render(output_base, format='svg', cleanup=True)
            print(f"[OK] SVG diagram saved: {output_base}.svg")
        except Exception as e:
            print(f"[FAIL] SVG generation failed: {e}")

        try:
            dot.render(output_base, format='pdf', cleanup=True)
            print(f"[OK] PDF diagram saved: {output_base}.pdf")
        except Exception as e:
            print(f"[FAIL] PDF generation failed: {e}")

        # Save DOT source
        dot_file = os.path.join(output_dir, 'ER_diagram.dot')
        with open(dot_file, 'w', encoding='utf-8') as f:
            f.write(dot.source)
        print(f"[OK] DOT source saved: {dot_file}")

    else:
        print("\n[WARNING] Graphviz library not found.")
        print("To install: pip install graphviz")
        print("Also ensure Graphviz system package is installed:")
        print("  - Windows: https://graphviz.org/download/")
        print("  - Linux: sudo apt-get install graphviz")
        print("  - Mac: brew install graphviz")

    # Always create ASCII diagram
    print("\nGenerating ASCII text diagram...")
    ascii_diagram = create_simple_ascii_diagram()
    ascii_file = os.path.join(output_dir, 'ER_diagram_ascii.txt')
    with open(ascii_file, 'w', encoding='utf-8') as f:
        f.write(ascii_diagram)
    print(f"[OK] ASCII diagram saved: {ascii_file}")

    print("\n" + "=" * 70)
    print("Diagram generation complete!")
    print("\nOutput files:")
    print(f"  - {output_dir}/ER_diagram.md (Mermaid format)")
    print(f"  - {output_dir}/ER_diagram_ascii.txt (Text format)")
    if GRAPHVIZ_AVAILABLE:
        print(f"  - {output_dir}/ER_diagram_visual.png")
        print(f"  - {output_dir}/ER_diagram_visual.svg")
        print(f"  - {output_dir}/ER_diagram_visual.pdf")
        print(f"  - {output_dir}/ER_diagram.dot")


if __name__ == '__main__':
    main()
