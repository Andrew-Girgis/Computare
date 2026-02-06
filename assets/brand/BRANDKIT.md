# Computare — Brand Kit

---

## 1. Brand Foundations

### Mission

Computare exists to give people true ownership and long-term visibility over their financial data. We provide open tools that allow users to track, understand, and analyse their finances across multiple accounts and over time — without surrendering control of their data to third parties.

### Vision

A future where individuals fully own their financial history, can move it freely between tools, and are never locked into opaque platforms that monetise their data. Computare aims to become the open financial layer people trust to understand their money over a lifetime.

### Values

| Value | Meaning |
|-------|---------|
| **Openness first** | Open-source by default. Users can self-host, inspect the code, and modify the system freely. |
| **Data ownership is non-negotiable** | Users always own their data. Data must be exportable, portable, and usable outside of Computare in multiple formats. |
| **Transparency over convenience** | Clear, explicit data flows over "black-box" integrations that hide how data is accessed or stored. |
| **User control over monetisation** | Self-hosting is free. Managed hosting is optional and paid. No feature gate around data ownership. |
| **Long-term thinking** | Built for years of financial history, not short-term budgeting gimmicks. |

### Target Audience

**Primary** — Canadians with one or more bank, credit card, or investment accounts who want:
- Long-term visibility into their finances
- Control over where their data lives
- An alternative to closed, US-centric fintech platforms

**Secondary:**
- Technically curious users who value open-source software
- Privacy-conscious individuals
- Builders who want programmable access to their own financial data

### Positioning Statement

Computare is an open-source personal finance platform that lets users own and control their financial data. Unlike traditional finance apps that rely on credential-scraping services or manual transaction entry, Computare provides the tools to collect, store, analyse, and export financial data on your terms — whether you host it yourself or choose managed hosting.

---

## 2. Logo System

### Core Concept

The Computare logo system represents **ownership**, **structure**, **long-term storage**, and **financial data as infrastructure**.

### Primary Logo

A serif **"C"** — represents Computare, computation, and continuity. The serif communicates trust, longevity, and seriousness.

### Secondary / Symbol Logo

Three stacked coins forming a subtle **database / storage symbol**. Symbolises financial value, data persistence, and user-owned infrastructure.

### Icon / Mark-Only Usage

The serif "C" alone. Used for app icons, favicons, small UI elements, and social avatars.

### Usage Rules

- No distortion or stretching
- No gradients unless defined in the colour system
- No drop shadows or glow effects
- Maintain generous clear space equal to the height of the "C"

### Approved Backgrounds

| Approved | Avoid |
|----------|-------|
| White | Busy or textured backgrounds |
| Black | Low-contrast or competing patterns |
| Dark green | |

---

## 3. Colour Palette

### Primary Colours

| Role | Colour | Hex | Usage |
|------|--------|-----|-------|
| **Black** | Deep black | `#0A0A0A` | Authority, clarity, seriousness. Primary dark surfaces. |
| **White** | Pure white | `#FAFAFA` | Openness, neutrality, trust. Primary light surfaces. |
| **Luxury Green** | Deep forest | `#1A3A2A` | Finance, growth, restraint. Used intentionally, not loudly. |

> Only one primary colour should dominate a given surface.

### Secondary / Accent Colours

| Role | Colour | Hex | Usage |
|------|--------|-----|-------|
| **Gold** | Warm gold | `#C9A84C` | Sparingly for emphasis, success states, or highlights. Decorative, not informational. |
| **Muted Green** | Sage | `#4A7C5C` | Secondary accent in data visualisations and interactive states. |

### Neutral Colours

| Role | Hex | Usage |
|------|-----|-------|
| Neutral 100 | `#F5F5F5` | Light backgrounds, cards |
| Neutral 200 | `#E5E5E5` | Dividers, borders |
| Neutral 400 | `#A3A3A3` | Secondary text, placeholders |
| Neutral 600 | `#525252` | Body text on light |
| Neutral 800 | `#262626` | Body text on dark |
| Neutral 900 | `#171717` | Deep background |

### CSS Variables (Reference)

```css
:root {
  /* Primary */
  --c-black:       #0A0A0A;
  --c-white:       #FAFAFA;
  --c-green-deep:  #1A3A2A;

  /* Accent */
  --c-gold:        #C9A84C;
  --c-green-sage:  #4A7C5C;

  /* Neutrals */
  --c-neutral-100: #F5F5F5;
  --c-neutral-200: #E5E5E5;
  --c-neutral-400: #A3A3A3;
  --c-neutral-600: #525252;
  --c-neutral-800: #262626;
  --c-neutral-900: #171717;
}
```

### Accessibility

- All text must meet **WCAG AA** contrast minimums (4.5:1 for body, 3:1 for large text)
- Never rely on colour alone to communicate meaning
- Gold is decorative, not informational

---

## 4. Typography

### Headline Typeface — Serif

An editorial, expressive serif used for brand moments. Choose one:

| Option | Style | Notes |
|--------|-------|-------|
| **Tobias** | Transitional serif | Refined, warm, editorial presence |
| **PP Editorial** | Display italic serif | High contrast, magazine-quality drama |
| **Bradford LL** | Contemporary serif | Balanced, authoritative, restrained |

**Used for:** Hero headlines, section headers, brand moments, pull quotes.

### Body Typeface — Sans-Serif

A clean, modern sans-serif for all functional text. Choose one:

| Option | Style | Notes |
|--------|-------|-------|
| **PP Formula** | Geometric sans | Technical precision, modern edge. *Used by Hex.* |
| **Riposte** | Humanist sans | Warm but structured, highly readable |
| **Knapp** | Grotesque sans | Neutral authority, pairs well with editorial serifs. *Used by Legend.* |

**Used for:** Body text, UI labels, documentation, long-form content.

### Monospace (Optional)

| Option | Style | Notes |
|--------|-------|-------|
| **Diatype Mono** | Grotesque mono | Clean, technical, minimal personality |
| **IBM Plex Mono** | Humanist mono | Readable at small sizes, open-source |
| **Geist Mono** | Geometric mono | Already in the codebase, works as a default |

**Used for:** Code snippets, data examples, technical documentation, transaction IDs, amounts.

### Type Hierarchy

```
SERIF       = ideas, statements, positioning
SANS-SERIF  = clarity, explanation, interaction
MONOSPACE   = data, code, technical specifics
```

### Scale (Desktop)

| Level | Size | Weight | Face |
|-------|------|--------|------|
| Display | 72–96px | Regular/Light | Serif |
| H1 | 48–56px | Regular | Serif |
| H2 | 32–40px | Medium | Serif |
| H3 | 24–28px | Medium | Sans-serif |
| H4 | 20px | Semibold | Sans-serif |
| Body Large | 18px | Regular | Sans-serif |
| Body | 16px | Regular | Sans-serif |
| Body Small | 14px | Regular | Sans-serif |
| Caption | 12px | Medium | Sans-serif or Mono |
| Code | 14px | Regular | Monospace |

---

## 5. Voice & Tone

### Brand Personality

**Calm. Direct. Open. Trustworthy. Non-patronising.**

Computare never sounds salesy, alarmist, gamified, or trend-chasing.

### Tone by Context

| Context | Tone |
|---------|------|
| **Product** | Clear, reassuring, precise. Assumes user intelligence. |
| **Documentation** | Explicit, honest about limitations, neutral — not promotional. |
| **Marketing** | Confident but restrained. Focused on ownership and control. Avoids hype. |

### Language Guidelines

**Words we use:**
- Own your data
- Control your finances
- Open-source
- Self-host
- Long-term visibility
- Financial history

**Words we avoid:**
- "Hack your finances"
- "Get rich"
- "Effortless"
- "AI magic"
- "Free forever" (unless literally true)

### Example Phrases

> "Your financial data, on your terms."
>
> "Track your finances without giving them away."
>
> "Built for years of financial history, not quick wins."

---

## 6. Imagery & Visual Style

### Visual Direction

| Treatment | Description |
|-----------|-------------|
| **Dithered textures** | Adds tactile, analogue quality to digital surfaces |
| **Halftone patterns** | Print-inspired overlays for depth and atmosphere |
| **ASCII-inspired visuals** | Nods to open-source, terminal, and hacker culture |
| **3D isometric graphics** | Structural representations of data, infrastructure, and flow |

### Illustration Style

- Flat or isometric
- Structural, not playful
- Inspired by systems, infrastructure, and data flow
- Should feel like **technical drawings**, not consumer illustrations

### Typography in Visuals

- Serif for headlines and hero text
- Sans-serif for labels and supporting text

### Icons

- Simple, geometric
- Consistent stroke weight (1.5–2px)
- Prefer **outlined** icons over filled
- Based on a 24px grid

### Filters & Treatments

| Approved | Avoid |
|----------|-------|
| Dither overlays | Heavy blur |
| Halftone patterns | Neon effects |
| ASCII art overlays | Lens flare |
| Subtle grain (2–4%) | Excessive gradients |
| Noise textures | Drop shadows on text |

---

## 7. Motion & Animation

### Philosophy

Motion in Computare is **architectural, not decorative**. Animations communicate structure — elements arriving, data resolving, sections entering the viewport. Movement should feel like machinery operating with precision, not ornamentation seeking attention.

The landing page is the exception to restraint. It is Computare's brand moment — where motion earns trust, demonstrates craft, and makes the product memorable. The dashboard and product UI remain utilitarian.

### Landing Page Motion

The landing page uses **orchestrated, scroll-driven animation** to reveal content with intent.

**Page Load / Hero:**
- Staggered entrance sequence — headline, subhead, and CTA arrive in deliberate succession using `animation-delay`
- Serif headline fades and translates up (subtle, 20–30px travel)
- Supporting elements follow with 80–150ms stagger intervals
- Total orchestration completes within 1.2s — never leave the user waiting

**Scroll-Triggered Reveals:**
- Sections animate into view as the user scrolls using `IntersectionObserver` or a library like GSAP ScrollTrigger
- Preferred entrance: fade + translate-up (12–24px travel, 400–600ms duration)
- Stagger child elements within each section (60–100ms between siblings)
- Trigger threshold: ~15–20% of the element visible

**Parallax & Depth:**
- Subtle parallax on background textures (dither, grain overlays) — keep displacement under 30px
- Isometric illustrations or coin graphics may have independent scroll rates for layered depth
- Never parallax text — only decorative or atmospheric elements

**Hover & Interaction:**
- Buttons: scale or background shift on hover (80–120ms, `ease-out`)
- Cards/links: border or shadow transition, not colour change alone
- Navigation elements: underline slide or opacity shift

**Number/Data Animations:**
- Counting/ticker animations for key statistics (transactions processed, categories, etc.)
- Use `tabular-nums` during animation to prevent layout shift
- Duration: 1–2s with an easing curve that decelerates (`ease-out` or custom cubic-bezier)

### Dashboard / Product UI Motion

Inside the product, motion is **functional and minimal**:

| Context | Animation | Duration |
|---------|-----------|----------|
| Page transitions | Fade or cross-dissolve | 150–250ms |
| Data loading | Skeleton shimmer or subtle pulse | Until resolved |
| Expanding/collapsing | Height + opacity | 200–300ms |
| Toasts/notifications | Slide in from edge + fade | 200ms in, 150ms out |
| Modal open/close | Scale from 0.97 + fade | 150–200ms |
| Hover states | Background or border shift | 80–120ms |

- No entrance animations on dashboard page loads — data should feel instantly present
- No scroll-triggered reveals inside the product
- Transitions serve **state changes**, not decoration

### Easing & Timing

| Use case | Easing | Notes |
|----------|--------|-------|
| Entrances | `cubic-bezier(0.22, 1, 0.36, 1)` | Fast start, gentle settle — elements arriving |
| Exits | `cubic-bezier(0.55, 0, 1, 0.45)` | Accelerates out — elements departing |
| Hover/interaction | `ease-out` or `cubic-bezier(0, 0, 0.2, 1)` | Immediate response, soft land |
| Scroll parallax | `linear` | Constant rate tied to scroll position |

- Avoid `ease-in-out` for UI — it feels sluggish at both ends
- Never exceed 600ms for any single animation in the product UI
- Landing page orchestrations may extend to 1.2–1.5s total, but individual elements stay under 600ms

### Implementation

- **Landing page:** CSS animations + `IntersectionObserver` for scroll triggers. GSAP ScrollTrigger if complexity demands it. Prefer CSS-only where possible.
- **Product UI:** CSS transitions on state changes. Framer Motion (React) for coordinated mount/unmount and layout animations where needed.
- **Reduced motion:** All animation must respect `prefers-reduced-motion: reduce`. Replace motion with instant state changes or opacity-only fades (no translation, no scale).

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Motion Don'ts

- No bounce or elastic easing — conflicts with the serious, tool-like tone
- No infinite looping animations (except loading indicators)
- No animation on page load inside the dashboard
- No parallax on text or interactive elements
- No motion that delays access to content by more than 1.5s
- No spring physics that feel playful or toy-like

---

## 8. Layout & UI

### Principles

- **Grid-based layouts** — strict column structure, asymmetry allowed for brand moments
- **Generous spacing** — breathing room communicates quality and confidence
- **Clear visual hierarchy** — one focal point per section, no competing elements
- **Tool-like, not consumer-app-like** — precision and clarity over friendliness and flair

### Grid System

| Context | Columns | Gutter | Margin |
|---------|---------|--------|--------|
| Desktop (1440px) | 12 | 24px | 80px |
| Tablet (768px) | 8 | 20px | 40px |
| Mobile (375px) | 4 | 16px | 20px |

### Component Guidelines

**Buttons:**
- Simple shapes, minimal decoration, clear affordances
- Primary: filled black/white with text
- Secondary: outlined with 1px border
- No rounded-pill shapes — use subtle radii (`4–8px`)

**Cards:**
- Subtle border (`1px`, `neutral-200` or `white/10%` in dark mode)
- No drop shadows by default
- Generous internal padding (`24–32px`)

**Tables & Data:**
- Monospace for numerical columns
- Right-align currency amounts
- Alternating row shading optional, prefer dividers

### Spacing Scale

```
4px  — micro (icon padding, badge insets)
8px  — tight (inline elements, form gaps)
16px — base (paragraph spacing, list items)
24px — comfortable (card padding, section gaps)
32px — spacious (between components)
48px — generous (between sections)
64px — expansive (between page regions)
96px — dramatic (hero padding, page-level separation)
```

---

## 9. Accessibility & Inclusion

- **Colour contrast** compliant by default (WCAG AA minimum, AAA preferred for body text)
- **Keyboard-navigable** interfaces with visible focus indicators
- **Clear language** — no jargon without explanation
- **Respect `prefers-reduced-motion`** — disable animations when requested
- **Design assumes a wide range of technical ability** — progressive disclosure for complexity
- **Screen reader tested** — semantic HTML, ARIA labels where needed
- **Responsive** — every view works from 320px to 2560px

---

## 10. Inspiration References

Sites that inform the visual and tonal direction of Computare:

| Site | What to reference |
|------|-------------------|
| [Titan](https://www.titan.com/) | Dark-first fintech premium aesthetic, illustration-forward hero sections, high-contrast type hierarchy |
| [Hex](https://hex.tech/) | PP Formula typography, noise textures, grid-based dot patterns, micro-interactions, data-forward design |
| [Legend](https://legend.xyz/) | Knapp typeface, stark monochromatic scheme, DeFi-native clarity, mobile-first orientation |
| [Speakeasy](https://www.speakeasy.com/) | Developer tooling aesthetic, technical precision, API-first visual language |
| [Cassette](https://www.cassettemusic.com/) | Dithered textures, halftone treatments, analogue-digital crossover |
| [Popcorn](https://www.popcorn.space/) | Playful isometric 3D, structural illustration, bold colour blocking |
| [Claude](https://claude.ai/) | Clean product design, generous spacing, calm confidence, tool-like UI |
| [General Intelligence](https://www.generalintelligencecompany.com/) | Editorial serif usage, restrained layouts, serious tone |

---

## 11. Quick Reference

### Do

- Use black and white as dominant surface colours
- Let green and gold accent sparingly
- Pair serif headlines with sans-serif body
- Use monospace for anything numerical or code-related
- Keep generous whitespace
- Apply dither/halftone/grain for texture
- Write in a calm, direct, non-patronising voice
- Build tool-like interfaces
- Use orchestrated scroll-triggered animation on the landing page
- Respect `prefers-reduced-motion` in all contexts

### Don't

- Use gradients as primary design elements
- Apply drop shadows or glow effects to logos or text
- Mix more than two primary surface colours on one page
- Use playful, rounded, or "friendly" illustration styles
- Write with urgency, hype, or gamified language
- Sacrifice clarity for aesthetic
- Gate data ownership features behind paid tiers
- Use colour as the sole indicator of meaning
- Use bounce, elastic, or spring easing
- Add entrance animations inside the dashboard
- Let motion delay access to content beyond 1.5s

---

*Computare is open-source. This brand kit is a living document.*
*Last updated: February 2026.*
