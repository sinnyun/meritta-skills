# Image Poster Generation Skill

## Positioning

This skill provides complete capabilities from design specifications to image poster output.

**Output format**: Generate various types of image posters to meet different scenario needs.

## Core Capabilities

### Design Specification Capability

Built-in complete design specifications ensure consistent and professional poster styles:

- **Color system**: 9 color families × 7 levels complete palette
- **Font system**: Size, weight, line-height specifications for titles, body text, and auxiliary text
- **Layout system**: Page dimensions, margins, spacing specifications
- **Style system**: Preset style classes

### Content Generation Capability

Generate structured content to meet different scenario needs:

- **Ad posters**: Product ads, brand ads, promotional ad posters
- **Promotional posters**: Event promotion, brand promotion, product promotion posters
- **Event posters**: Conference, exhibition, performance, competition event posters
- **Product posters**: Product introduction, product features, product advantage posters

### Template Application Capability

Quick generation based on templates, maintaining style consistency:

- **Built-in templates**: Common templates
- **Custom templates**: Support user-defined templates
- **Style inheritance**: Inherit styles and formats from templates

### Output and Save Capability

Support multiple output options to meet different usage scenarios:

- **Standard output**: Standard format
- **Format preservation**: Preserve all formatting
- **Version compatibility**: Support different versions
- **Image export**: Generated HTML posters include a "Export as Image" button — click to export high-resolution PNG in one step, no additional tools or commands needed

### Style Optimization Capability (Collaborates with design-taste-frontend Skill)

After content generation, invoke the `design-taste-frontend` skill for professional-level aesthetic optimization of poster styles:

- **Design metric-driven**: Validate visual quality based on metric rules, not subjective adjustments
- **Strict component architecture**: Follow professional component design specifications, ensuring maintainability
- **CSS hardware acceleration**: Apply transform, will-change, etc. to optimize rendering performance
- **Balanced design engineering**: Balance visual aesthetics with engineering performance
- **Accessibility**: Ensure color contrast and readability meet WCAG standards

## Usage Rules

### Execution Flow

1. **First load**: Read `references/poster-catalog.md` to get design specifications and component inventory
2. **Deep dive as needed**: After confirming the type, read `references/poster-requirements.md` for generation requirements; if samples are needed, read `references/exemplars.md` for references
3. **Style optimization (key step)**: After content generation is complete, invoke the `design-taste-frontend` skill for professional aesthetic optimization of the poster, including but not limited to:
   - Visual hierarchy and information architecture optimization
   - Spacing, alignment, and grid specification calibration
   - Color contrast and readability improvement
   - Font hierarchy and typography detail polishing
   - Component style and micro-interaction optimization
   - CSS hardware acceleration and performance optimization
4. **Independent execution**: This skill, except for invoking `design-taste-frontend` for style optimization, has all other capabilities built-in and can generate directly

### Output Rules

1. **File output**: Generated content is saved as corresponding format files
2. **Software viewing**: Users can open files through corresponding software
3. **Format preservation**: Ensure all formats display correctly

## Execution Framework

This skill embeds a complete execution framework.

**Core philosophy**:
- **Specification-driven**: All content must follow design specifications
- **Content adaptation**: Select the most appropriate content structure based on requirements
- **User-friendly**: Output files can be used directly, no additional processing needed

**Unified execution flow**: After receiving a task, execute in 5 steps — Requirements Analysis → Content Planning → Content Generation → Style Optimization → File Output.

### Step 0: Requirements Analysis

Analyze user requirements:
- Content type
- Target audience
- Usage scenario
- Save requirements

### Step 1: Content Planning

Plan content based on requirements analysis results:
- **Structure planning**: Content structure
- **Style planning**: Design style
- **Content planning**: Specific content

### Step 2: Content Generation

Generate content based on design specifications:
- Apply color system
- Apply font system
- Apply layout rules
- Apply style system

### Step 3: Style Optimization (Invoke design-taste-frontend Skill)

Pass the poster HTML generated in Step 2 to the `design-taste-frontend` skill for professional style aesthetic optimization:
- **Visual hierarchy**: Optimize information architecture and visual weight distribution
- **Spacing and grid**: Calibrate spacing, alignment, and grid specifications, ensuring rhythm
- **Color and contrast**: Improve color contrast and readability, ensuring accessibility
- **Font and typography**: Polish font hierarchy, line height, letter spacing, and other typography details
- **Components and interaction**: Optimize component styles and micro-interaction details
- **Performance optimization**: Apply CSS hardware acceleration and rendering performance optimization
- **Design metrics**: Validate design quality based on metric rules, ensuring compliance with professional standards

After optimization, pass the optimized HTML to Step 4 for file output.

### Step 4: File Output

Save the optimized content as a file:
- Save as corresponding format
- Embed "Export as Image" button and export script (html-to-image) in HTML
- Inform user of file location and how to open it
- Inform user they can click the button directly in the browser to export PNG images


## Image Poster Generation Domain Overview

Organized by usage flow, 5 domains with 19 task types:

| Domain | Task Count | Typical Tasks |
|----|--------|---------|
| P0 Requirements Analysis Domain | 4 | Poster type identification, Target audience analysis, Usage scenario analysis, Output format selection |
| P1 Design Specification Domain | 4 | Color system application, Font system application, Layout rule application, Style system application |
| P2 Content Generation Domain | 4 | Ad poster generation, Promotional poster generation, Event poster generation, Brand poster generation |
| P3 Format Processing Domain | 4 | Style application, Format adjustment, Layout optimization, Compatibility processing |
| P4 Output and Save Domain | 3 | Image file output, Format validation, Resolution processing |

**Inter-domain logic flow**: P0 → P1 → P2/P3 → **Style Optimization (design-taste-frontend)** → P4 (invoked as needed)

Complete inventory see `references/p-catalog.md`.


## Unique Dimensions

The p-generation skill has the following unique dimensions:

| Dimension | Description | Impact |
|------|------|------|
| **Poster type** | Ad poster, Promotional poster, Event poster, Brand poster, etc. | Determines design style and content focus |
| **Visual design** | Color matching, Font selection, Image processing, Composition design | Determines poster visual effect |
| **Distribution channel** | Online promotion, Offline display, Social media, Print materials | Determines size and format requirements |

## Three-Layer Structure

Layer 1: Design specification inventory + dependency topology → references/poster-catalog.md
Layer 2: Generation requirements inventory → references/poster-requirements.md
Layer 3: Generation sample library → references/exemplars.md

## Fact Discipline

1. Design specifications must come from `references/poster-catalog.md`, not from subjective feeling
2. Generated content must comply with specification requirements, no arbitrary style modifications
3. File output must use standard formats, ensuring software compatibility
4. Complex content must use mature libraries, no self-implemented complex logic
5. Format preservation must use standard APIs, no reliance on third-party services
6. **Text gradient effects must be implemented using SVG `<text>` + `<linearGradient>`, CSS `background-clip: text` is prohibited** (CSS gradient text loses background when exporting images, SVG approach ensures gradient effects are fully preserved after export)
7. **html2canvas export is prohibited**, html-to-image must be used (the former re-implements CSS rendering in canvas, causing background/opacity/gradient/shadow inconsistencies with the page)
8. **Export-compatible CSS specifications**: Containers must explicitly set background color (no reliance on inheritance); use `rgba()` instead of `opacity` for transparency; avoid `backdrop-filter`/`mix-blend-mode`; all `var(--xxx)` must have default values; shadows at most 2 layers of outer shadow

## Title Hierarchy Specifications

To ensure title hierarchy does not conflict when merging into a single prompt file, the title hierarchy specifications for each file are as follows:

| File Type | H1 | H2 | H3 | H4 |
|---------|---------|---------|---------|---------|
| SKILL.md | `#` | `##` | `###` | `####` |
| references/catalog.md | `##` | `###` | `####` | `#####` |
| references/requirements.md | `##` | `###` | `####` | `#####` |
| references/exemplars.md | `##` | `###` | `####` | `#####` |
| references/exemplars/*.md | `##` | `###` | `####` | `#####` |
