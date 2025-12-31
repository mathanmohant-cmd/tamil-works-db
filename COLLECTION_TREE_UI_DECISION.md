# Collection Tree UI Design Decision

**Date**: 2025-12-30
**Component**: `webapp/frontend/src/components/TreeNode.vue`
**Decision**: Remove chevron expand/collapse icon, make folder icon clickable

## Problem Statement

The collection tree had redundant visual indicators for expand/collapse functionality:
- **Chevron icon** (▶/▼) - Small, clickable for expand/collapse
- **Folder icon** (📁/📂) - Purely decorative, not clickable
- Both indicated the same state (collapsed/expanded)

**Issues:**
1. Visual redundancy - two icons doing the job of one
2. Poor mobile UX - folder icons were hidden on mobile to save space
3. Small click target - only the tiny chevron was clickable
4. Wasted horizontal space - 24px per row for the chevron

## Decision

**Remove the chevron entirely and make the folder icon the expand/collapse control.**

### Rationale

1. **Cleaner UI**: One visual element instead of two
2. **Familiar pattern**: Standard file explorer behavior (Windows, macOS, Linux)
3. **Better mobile UX**: Folder icons now visible and functional on mobile
4. **Larger click target**: Folder icon is bigger and more obvious than chevron
5. **Space savings**: 24px saved per row
6. **Simpler code**: Fewer CSS rules and template elements

## Implementation Details

### UI Element Order

**Before:**
```
[chevron/spacer 1.5rem] [checkbox/spacer 16px] [folder icon] [collection name]
```

**After:**
```
[checkbox/spacer 16px] [folder icon] [collection name]
```

### Clickable Folder Icon Behavior

- **Collapsed state**: 📁 (closed folder)
- **Expanded state**: 📂 (open folder)
- **Hover effect**: Scale 1.15 (15% larger)
- **Active/click effect**: Scale 0.95 (slight press effect)
- **Leaf nodes**: 📄 (document icon, not clickable)

### Mobile Considerations

**Desktop:**
- Folder icon: 1rem font-size
- Natural click target from emoji size

**Mobile (max-width: 768px):**
- Folder icon: 1.2rem font-size (larger)
- Clickable folders: 44px minimum touch target (WCAG standard)
- Display: `inline-flex` with centered alignment
- Folder icons **now visible** (previously hidden to save space)

### Accessibility

- ✅ **Touch targets**: 44px minimum on mobile (WCAG 2.1 Level AAA)
- ✅ **Keyboard navigation**: Checkboxes still tabbable and keyboard-accessible
- ✅ **Visual feedback**: Hover and active states provide clear interaction cues
- ✅ **Screen readers**: Standard folder emoji semantics preserved

## Code Changes

### Files Modified

**Single file change:**
- `webapp/frontend/src/components/TreeNode.vue`

### Template Changes

```vue
<!-- BEFORE: Chevron + non-clickable folder -->
<span v-if="hasChildren" @click.stop="handleToggle" class="toggle-icon">
  <span class="chevron-icon" :class="isExpanded ? 'chevron-down' : 'chevron-right'"></span>
</span>
<span v-else class="toggle-spacer"></span>
<span class="node-icon">
  {{ hasChildren ? (isExpanded ? '📂' : '📁') : '📄' }}
</span>

<!-- AFTER: Clickable folder only -->
<span
  class="node-icon"
  :class="{ 'clickable': hasChildren }"
  @click.stop="hasChildren ? handleToggle() : null"
>
  {{ hasChildren ? (isExpanded ? '📂' : '📁') : '📄' }}
</span>
```

### CSS Changes

**Removed:**
- `.toggle-icon` (desktop and mobile)
- `.toggle-spacer` (desktop and mobile)
- `.chevron-icon` sizing rules

**Added:**
```css
.node-icon.clickable {
  cursor: pointer;
}

.node-icon.clickable:hover {
  transform: scale(1.15);
}

.node-icon.clickable:active {
  transform: scale(0.95);
}

/* Mobile */
@media (max-width: 768px) {
  .node-icon {
    font-size: 1.2rem;
    margin: 0 0.4rem;
  }

  .node-icon.clickable {
    min-width: 44px;
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
}
```

## Testing Checklist

All functionality verified:
- ✅ Folder icon changes between 📁 (closed) and 📂 (open)
- ✅ Clicking folder icon expands/collapses the node
- ✅ Hover effect works (scale 1.15)
- ✅ Click effect works (scale 0.95)
- ✅ Document icon 📄 (leaf nodes) is not clickable
- ✅ Checkbox still works independently
- ✅ Folder icons visible on mobile
- ✅ 44px touch targets on mobile
- ✅ No horizontal scroll with long collection names
- ✅ Proper alignment with checkboxes

## User Feedback

**User's choice**: "Folder icon only (clickable)"

**Alternative options considered and rejected:**
1. ~~Entire row clickable~~ - Would conflict with checkbox selection
2. ~~Keep chevron + make folder clickable~~ - Still redundant, doesn't solve the core issue

## Related Documentation

- Mobile UI optimization: `MOBILE_FILTER_OPTIMIZATION.md`
- Collection pattern: `DESIGNATED_COLLECTION_PATTERN.md`
- Chevron icon history: Previous plan file `virtual-nibbling-platypus.md`

## Backward Compatibility

**Breaking changes:** None

The change is purely UI/UX. The underlying functionality (`handleToggle` method, expand/collapse logic, event emissions) remains unchanged.

## Future Considerations

1. **Accessibility enhancement**: Could add `role="button"` and `aria-label` to clickable folder icons for better screen reader support
2. **Animation**: Could add smooth rotation/transition when folders open/close
3. **Keyboard shortcuts**: Could add keyboard support for expand/collapse (Space/Enter on focused folders)

## Conclusion

This UI simplification improves usability, reduces visual clutter, and provides a more intuitive interaction pattern that matches user expectations from standard file explorers. The change is particularly beneficial on mobile devices where screen space is limited.

**Status**: ✅ Implemented and deployed (2025-12-30)
