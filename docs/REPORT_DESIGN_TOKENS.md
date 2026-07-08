# Report Design Tokens - Ticket 06H

## Colour Palette

The DOO U brand colour scheme is applied consistently across all HTML/PDF reports.

### Primary Colours

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Dark Green | #20352D | rgb(32, 53, 45) | Primary text, main headings, table headers |
| Deep Green | #083F32 | rgb(8, 63, 50) | Cover page background, secondary headers |
| Soft Green | #2E6B4F | rgb(46, 107, 79) | Section headers, badges, highlights |
| Gold | #C8A247 | rgb(200, 162, 71) | Accents, section borders, special highlights |

### Neutral Colours

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Cream | #F5F3F0 | rgb(245, 243, 240) | Page/section backgrounds |
| Text Primary | #333333 | rgb(51, 51, 51) | Body text |
| Text Secondary | #666666 | rgb(102, 102, 102) | Supporting text, annotations |
| Border | #E0E0E0 | rgb(224, 224, 224) | Dividers, table borders |

### Status Colours

| Status | Colour | Hex | Usage |
|--------|--------|-----|-------|
| Success | Green | #4CAF50 | High scores (75-100%), positive indicators |
| Warning | Orange | #FF9800 | Medium scores (50-75%), caution zones |
| Danger | Red | #F44336 | Low scores (0-50%), alerts |
| Info | Soft Green | #2E6B4F | Informational badges, neutral highlights |

## Typography

### Font Family

**Primary Font:** Segoe UI, Tahoma, Geneva, Verdana, sans-serif

Consistent sans-serif stack for excellent screen readability and print quality.

### Type Scale

| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| h1 (Title) | 2.0 em | 600 | 1.2 | Main section headings |
| h2 (Section) | 1.6 em | 600 | 1.3 | Section headers |
| h3 (Subsection) | 1.3 em | 600 | 1.4 | Subsection headers |
| h4-h6 | 1.0 em | 600 | 1.5 | Minor headings |
| Body Text | 1.0 em (16px) | 400 | 1.8 | Paragraphs, lists |
| Table Text | 1.0 em | 400 | 1.6 | Table cells |
| Small Text | 0.9 em | 400 | 1.5 | Footnotes, annotations |
| Code | 0.9 em | 400 | 1.4 | Variable codes (R01, D01, etc) |

### Font Weights

- **Regular (400):** Body text, standard content
- **Semi-bold (600):** Headings, emphasis
- **Bold (700):** Score values, critical highlights

## Spacing

### Base Unit: 1 em (16px)

| Purpose | Rem | Pixels | Usage |
|---------|-----|--------|-------|
| Extra small | 0.25 | 4px | Internal padding on small elements |
| Small | 0.5 | 8px | Button padding, minor margins |
| Base | 1 | 16px | Standard padding, margins |
| Large | 1.5 | 24px | Section spacing |
| Extra large | 2.5 | 40px | Major section breaks |

### Document Layout

- **Page Width:** 8.5 inches (letter size)
- **Page Height:** 11 inches (letter size)
- **Document Padding:** 0.75 inches all sides
- **Section Margin Bottom:** 2.5 em
- **Paragraph Margin Bottom:** 1 em
- **Line Height (Body):** 1.8

## Component Styles

### Section Headers

```css
background-color: #F5F3F0;
border-left: 4px solid #C8A247;
padding: 1em;
margin-bottom: 1.5em;
```

Used for all section titles to create visual consistency and hierarchy.

### Content Blocks

```css
background-color: white;
border: 1px solid #E0E0E0;
padding: 1.5em;
margin-bottom: 1.5em;
border-radius: 4px;
```

Basic container for paragraph content.

### Highlight Blocks

```css
background-color: #F5F3F0;
border-left: 4px solid #C8A247;
```

For important callout content.

### Score Display (Large)

```css
background: linear-gradient(135deg, #2E6B4F 0%, #20352D 100%);
color: white;
border-radius: 8px;
padding: 1.5em;
font-size: 3em;
font-weight: 700;
```

Used for overall score and key metrics on cover page.

### Score Cards

Grid layout with individual score indicators:
- Card width: 250px minimum
- Card padding: 1 em
- Border: 1px solid #E0E0E0
- Card score font size: 1.8 em
- Card score colour: #2E6B4F

### Score Gauge (Progress Bar)

```css
height: 24px;
border-radius: 12px;
border: 1px solid #2E6B4F;
background: linear-gradient(90deg, #2E6B4F, #C8A247);
```

Visual representation of score progress (0-100%).

### Tables

- **Header:** Dark green background (#083F32), white text, 600 weight
- **Cell Padding:** 0.8 em vertical, 1 em horizontal
- **Row Alternation:** Every even row #F5F3F0
- **Border:** Bottom border on cells, 1px #E0E0E0

### Badges

**Default Badge:**
```css
display: inline-block;
padding: 0.4em 0.8em;
border-radius: 20px;
font-size: 0.85em;
font-weight: 600;
```

**Badge Variants:**
- Success (Green): #4CAF50, white text
- Warning (Orange): #FF9800, white text
- Danger (Red): #F44336, white text
- Info (Soft Green): #2E6B4F, white text

### Flag Boxes

Left border (4px) + background colour:

| Flag Type | Border Colour | Background |
|-----------|---------------|------------|
| Protected Evidence | #9C27B0 | #F3E5F5 |
| Unsafe Route | #FF5722 | #FFEBEE |
| Manual Review | #FFC107 | #FFFDE7 |

## Responsive Design

### Breakpoints

| Device | Width | Adjustments |
|--------|-------|-------------|
| Desktop | > 768px | Full layout, 3-column grids |
| Tablet | 480px - 768px | 2-column grids |
| Mobile | < 480px | 1-column layout, larger touch targets |

### Print Styles

```css
@media print {
    body { background: white; }
    section { page-break-inside: avoid; }
    table, tr { page-break-inside: avoid; }
}
```

## Accessibility

### Colour Contrast

- Text on white background: Dark Green (#20352D) - WCAG AAA
- Text on cream background: Dark Green (#20352D) - WCAG AAA
- Text on green background: White text - WCAG AAA
- Gold accent on white: Not used for text, only decoration

### Font Sizing

- Minimum body text: 16px (1 em)
- No text smaller than 14px in tables
- Headings progressively scale for visual hierarchy

### Interactive Elements

- Badge borders and backgrounds clearly differentiate status
- Links include underlines or colour changes on hover
- Buttons have minimum touch target of 44px × 44px

## Print Considerations

### Page Breaks

- Sections: `page-break-inside: avoid`
- Tables: Row breaks allowed, but table headers repeat
- Long lists: Allow natural breaks
- Cover page: Always starts fresh page

### Margins & Gutters

- Top/bottom: 0.75 inches
- Left/right: 0.75 inches
- Footer space: Minimum 0.5 inches

### Font Preservation

- Use system fonts (no web font dependencies)
- Verdana as fallback for pdf rendering
- Test print output at 300 DPI

## Code Style Standards

### CSS Organisation

1. Reset and normalization
2. Typography rules
3. Component styles (sections, cards, badges)
4. Layout and grids
5. Responsive breakpoints
6. Print styles

### Naming Convention

Use descriptive class names:
- `.section-header` - Main section heading container
- `.content-block` - Generic content wrapper
- `.score-display` - Large score indicator
- `.score-card` - Individual score container
- `.badge-success` - Success badge variant
- `.flag-box.protected-evidence` - Protected evidence flag

### CSS Variable Usage

```css
:root {
    --doo-dark-green: #20352D;
    --doo-deep-green: #083F32;
    --doo-soft-green: #2E6B4F;
    --doo-gold: #C8A247;
    --doo-cream: #F5F3F0;
}
```

## Animation & Motion

- Minimal animations for print-focused design
- No autoplay video/audio
- Transitions for hover states only
- Fade-in acceptable for interactive HTML

## Dark Mode (Future)

Tokens prepared for dark mode variant:
- Invert background/text colours
- Maintain contrast ratios
- Adjust green saturation if needed

---

**Last Updated:** 2026-07-08  
**Version:** 1.0 (Ticket 06H)  
**Status:** Active (DOO U Brand Standard)
