# Frontend Design Decisions

This document records key UI/UX design decisions to prevent them from being accidentally reverted.

## Search Results Layout (Last updated: 2025-01-09)

### Flat List Structure
**Decision**: Occurrence lines use a flat, simple list - NOT nested boxes or cards.

**Implementation**:
- Separator: Just a `border-bottom: 1px solid` line between occurrences
- Padding: Minimal `0.5rem 0` (vertical only, no horizontal padding)
- No decorative boxes, borders, or background colors
- No nesting of lines inside word containers

**Rationale**:
- Mobile-first design requires compact, scannable layout
- Excessive spacing wastes screen space on mobile devices
- Simple lines are easier to read than complex nested structures

**Files**:
- `src/style.css` lines 757-762 (`.word-expanded-content`)
- `src/style.css` lines 867-871 (`.occurrence-item`)

**Related Commit**: `53ac283` - "Simplify UI: remove decorative boxes and optimize spacing for mobile"

### Chevron Icons (Last updated: 2026-01-09)

**Decision**: Use CSS-based angle/caret chevrons (▶ ▼ ▲), NOT Unicode text characters.

**Implementation**:
- Size: `12px × 12px` (increased from 8px for mobile visibility)
- Border width: `2.5px` (thickened from 2px)
- Style: Two CSS borders forming angle shapes
- Animation: Smooth 0.2s rotation

**Rationale**:
- CSS chevrons render consistently across all browsers/fonts
- More visible on mobile touchscreens
- Enable smooth rotation animations
- Professional, modern appearance

**Files**:
- `src/style.css` lines 731-754 (chevron CSS)
- `src/components/search/SearchResults.vue` lines 65, 170 (usage)

**Related Commit**: `75bfaad` - "Replace Unicode arrows with CSS chevron icons"

## Mobile Optimization (Last updated: 2026-01-09)

### Responsive Padding
**Decision**: Reduce padding progressively on smaller screens to maximize content space.

**Implementation**:
- Desktop: `2rem` padding
- ≤640px: `1rem` padding
- ≤480px: `0.5rem` padding

**Rationale**:
- Mobile screens have limited width
- Users complained about "too much space on the sides"
- Desktop experience unchanged, mobile gets more content space

**Files**:
- `src/style.css` lines 1815-1817, 1928-1936 (responsive padding)

### Container Width
**Decision**: Use `max-width: 1000px` for consistent content width across all pages.

**Implementation**:
- All page containers: `max-width: 1000px`
- Matches "About & Help" page that user approved
- Centered with `margin: 0 auto`

**Rationale**:
- User feedback: "About & Help looks just right"
- Consistency: All tabs should have same width
- Readability: Prevents extremely wide lines on large screens

**Files**:
- `src/layouts/AppLayout.vue` line 35
- `src/pages/SearchPage.vue` line 278
- `src/components/AppHeader.vue` line 158

## Header Design (Last updated: 2026-01-09)

### Kurinji Blue Theme
**Decision**: Use deep blue gradient background for header instead of light gradient.

**Implementation**:
```css
background: linear-gradient(135deg, #4a5f8c 0%, #2d4168 100%);
border-bottom: 3px solid #1a2942;
```
- All text white or semi-transparent white
- Tabs use white underline for active state

**Rationale**:
- Strong visual identity for Tamil literature
- Better contrast for readability
- Professional, modern appearance

**Files**:
- `src/components/AppHeader.vue` lines 153-154

### Tab Navigation
**Decision**: Use bottom-border tab style, NOT boxed button tabs.

**Implementation**:
- Transparent background
- `border-bottom: 3px solid white` for active tab
- Minimal padding: `0.5rem 0.75rem`
- No gaps between tabs

**Rationale**:
- Modern design pattern (Gmail, GitHub, LinkedIn)
- Clean, minimal visual clutter
- Clear active state indication

**Files**:
- `src/components/AppHeader.vue` lines 191-217

## Principles for Future Changes

1. **Mobile-First**: Always consider mobile screens first, then scale up
2. **Minimal Spacing**: Use the least padding/margin necessary for readability
3. **Flat Hierarchies**: Avoid nested boxes and complex visual structures
4. **Consistent Widths**: All content should use the same max-width across pages
5. **Document Decisions**: Update this file when making significant design changes

## How to Use This File

Before making UI changes:
1. Read relevant sections to understand current decisions
2. If changing existing patterns, document why in commit message
3. Update this file with new decisions
4. Consider mobile impact of all spacing/layout changes
