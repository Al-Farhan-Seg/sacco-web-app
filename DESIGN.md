---
name: SACCO Management
description: A calm administrator's desk, a floating dark rail beside warm paper cards with raised icon tiles.
colors:
  palladian: "#EEE9DF"
  card: "#FBF9F4"
  oatmeal: "#C9C1B1"
  abyssal: "#1B2632"
  blue-fantastic: "#2C3B4D"
  burning-flame: "#FFB162"
  truffle-trouble: "#A35139"
  muted: "#5B6773"
typography:
  page-title:
    fontFamily: "Roboto, system-ui, Segoe UI, sans-serif"
    fontSize: "24px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  stat-value:
    fontFamily: "Roboto, system-ui, Segoe UI, sans-serif"
    fontSize: "clamp(20px, 8cqi, 24px)"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  modal-title:
    fontFamily: "Roboto, system-ui, Segoe UI, sans-serif"
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.3
  card-title:
    fontFamily: "Roboto, system-ui, Segoe UI, sans-serif"
    fontSize: "16px"
    fontWeight: 500
  body:
    fontFamily: "Roboto, system-ui, Segoe UI, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
  table:
    fontFamily: "Roboto, system-ui, Segoe UI, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    fontFeature: "tnum"
  label:
    fontFamily: "Roboto, system-ui, Segoe UI, sans-serif"
    fontSize: "13px"
    fontWeight: 500
  column-head:
    fontFamily: "Roboto, system-ui, Segoe UI, sans-serif"
    fontSize: "11px"
    fontWeight: 500
    letterSpacing: "0.07em"
rounded:
  control: "9px"
  card: "14px"
  tile: "12px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
components:
  button-primary:
    backgroundColor: "{colors.burning-flame}"
    textColor: "{colors.abyssal}"
    rounded: "{rounded.control}"
    height: "40px"
    padding: "0 16px"
  button-primary-large:
    backgroundColor: "{colors.burning-flame}"
    textColor: "{colors.abyssal}"
    rounded: "{rounded.control}"
    height: "48px"
    padding: "0 22px"
  button-danger:
    backgroundColor: "{colors.truffle-trouble}"
    textColor: "{colors.card}"
    rounded: "{rounded.control}"
    height: "40px"
    padding: "0 16px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.abyssal}"
    rounded: "{rounded.control}"
    height: "40px"
    padding: "0 16px"
  button-sidebar:
    backgroundColor: "transparent"
    textColor: "{colors.palladian}"
    rounded: "{rounded.control}"
    height: "34px"
    padding: "0 10px"
  card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.abyssal}"
    rounded: "{rounded.card}"
    padding: "20px"
  sidebar:
    backgroundColor: "{colors.abyssal}"
    textColor: "{colors.palladian}"
    rounded: "{rounded.card}"
    width: "250px"
    padding: "18px 14px 16px"
  nav-link:
    textColor: "{colors.oatmeal}"
    rounded: "{rounded.control}"
    height: "42px"
    padding: "8px 12px"
  nav-link-current:
    backgroundColor: "{colors.burning-flame}"
    textColor: "{colors.abyssal}"
    rounded: "{rounded.control}"
  stat-tile:
    backgroundColor: "{colors.burning-flame}"
    textColor: "{colors.abyssal}"
    rounded: "{rounded.tile}"
    size: "56px"
  input:
    backgroundColor: "{colors.card}"
    textColor: "{colors.abyssal}"
    rounded: "{rounded.control}"
    height: "42px"
    padding: "9px 12px"
  modal:
    backgroundColor: "{colors.card}"
    textColor: "{colors.abyssal}"
    rounded: "{rounded.card}"
    width: "640px"
---

# Design System: SACCO Management

## Overview

**Creative North Star: "The Administrator's Desk in Daylight"**

A back-office tool for one person entering and checking records all day. The look borrows the Material Dashboard shell and redraws it in one stylesheet: a dark rail that floats off the page edge, a warm off-white work area, rounded paper cards, and coloured icon tiles standing on the top edge of each number card. It is calm, dense enough for tables, and uses colour only to mark meaning.

Depth is soft and real: blurred, low-offset shadows tinted with the dark navy, never hard edges. Warm neutrals (paper and oatmeal) carry the page, cool navy carries structure and text, and a single orange speaks for action and location.

**Key Characteristics:**
- Floating dark rail (250px) with an orange current-page pill.
- Warm paper page, slightly lighter cards, oatmeal hairlines.
- Raised icon tiles on number cards are the recognisable signature.
- One large orange Add button per data page; everything else is quieter.
- Tabular figures everywhere money appears, right-aligned.
- Roboto only, Lucide line icons at one stroke weight.

## Colors

Warm paper and oatmeal neutrals, deep navy structure, one orange voice, one rust for destruction. No green anywhere; success is shown with a check icon, not a colour.

### Primary
- **Burning Flame** (#FFB162): the action and location colour. Primary buttons, the current nav pill, the brand tile, the check in toasts, selection highlight, the focus ring inside the dark rail. Text on it is always Abyssal.

### Secondary
- **Blue Fantastic** (#2C3B4D): secondary tiles, focus rings and caret on the page, links in card headers, the top of the rail gradient and the login backdrop.

### Tertiary
- **Truffle Trouble** (#A35139): delete buttons, field errors, error borders, the error toast. Also used as a decorative tile colour on two dashboard cards (Accounts, Loan repayments), a recorded ruling; it does not extend to any other decoration.

### Neutral
- **Palladian** (#EEE9DF): the page background, hover fill on ghost buttons, icon buttons and table rows, and text on the dark rail.
- **Card Paper** (#FBF9F4): cards, modals, input fields, the login card.
- **Oatmeal** (#C9C1B1): table rules, card borders (at half strength), pagination rule, scrollbar thumbs, nav link text on the dark rail. Input borders use a stronger mix of Oatmeal and Muted (derived, not a separate token).
- **Abyssal** (#1B2632): body text, the rail base, toasts, the current page number.
- **Muted Slate** (#5B6773): secondary text, column heads, captions, placeholders, resting icon buttons.

### Named Rules
**The Rust Means Harm Rule.** Truffle Trouble marks delete and errors. Its two decorative tiles are a ruling already made; add no more, and never use it for anything that is not destructive or an error.

**The One Voice Rule.** Orange marks the action to take or the page you are on. A screen has one large orange button; do not tint other controls orange.

## Typography

**Display Font:** none; headings use Roboto (with system-ui, Segoe UI, sans-serif)
**Body Font:** Roboto (400, 500, 700)

**Character:** One workmanlike sans at three weights. Hierarchy comes from weight and size, not from a second face.

### Hierarchy
- **Headline** (700, 24px, 1.25, -0.01em): the page title in the top row.
- **Title** (700, 18px, 1.3): modal titles. Login title is 22px, 700.
- **Card title** (500, 16px): headers of cards such as Recent savings.
- **Stat value** (700, 24px fluid from 20px, tabular): number cards, right-aligned; the feature card (Total savings) scales to 34px.
- **Body** (400, 15px, 1.5): default text and form fields. Table cells and the nav are 14px.
- **Label** (500, 13px): field labels, card links, pagination.
- **Column head** (500, 11px, 0.07em tracking, uppercase, Muted): table column headings only.

### Named Rules
**The Tabular Money Rule.** Any figure that is money or a count sits in tabular numerals, and money columns are right-aligned, formatted as "UGX 850,000".

## Layout

A two-column shell: the 250px rail and a fluid work area, 28px gap, 16px outer padding. The work area opens with a title row (page title left, actions right), then content as cards separated by 24px. Dashboard: a grid of number cards (1 column, 2 from 561px, 4 from 1280px; 24px column and 40px row gap to leave room for raised tiles), then two recent-activity cards side by side from 1380px, stacked below.

Spacing rhythm is 4/8/12/16/20/24 px: control gaps 8-10px, cell padding 11px by 16px (12px sideways at 1440px and below), card padding 20px. Tables scroll sideways inside their card; the actions column is pinned to the right edge with a fade that follows the scroll. At 1100px and below, name cells wrap.

Below 860px the rail becomes a compact bar: brand and log out on the first row, the pages as one horizontally scrolling row of pills beneath it (scroll-snapped, scrollbar hidden, the current page scrolled into view). At 560px forms go to one column and modal padding tightens.

## Elevation & Depth

Hybrid: tonal layering (page, then lighter card) plus soft blurred shadows. Shadows are always navy-tinted with negative spread, so they read as lift, not outline. Coloured glow shadows sit under orange and rust elements.

### Shadow Vocabulary
- **Card** (`0 2px 4px -1px rgb(27 38 50 / 0.06), 0 10px 24px -8px rgb(27 38 50 / 0.14)`): every card.
- **Raised** (`0 12px 28px -10px rgb(27 38 50 / 0.45), 0 4px 10px -4px rgb(27 38 50 / 0.3)`): the floating rail.
- **Modal** (`0 24px 48px -12px rgb(27 38 50 / 0.4), 0 8px 16px -8px rgb(27 38 50 / 0.25)`): dialogs, over a 50% navy backdrop.
- **Tile and primary glow** (`0 8px 18px -6px` in the tile's own colour at about 0.6 to 0.7 alpha, plus a small navy shadow): icon tiles; primary and danger buttons and the current nav pill use a smaller `0 6px 14px -6px` glow.
- **Toast** (`0 14px 28px -10px rgb(27 38 50 / 0.55), 0 4px 8px -4px rgb(27 38 50 / 0.3)`).

### Named Rules
**The Soft Lift Rule.** Shadows are blurred and navy-tinted. Never a hard offset or a pure black edge (the login card is the one place where black-based shadow is used, over the dark backdrop).

## Shapes

Two radii carry the system: 14px for cards, the rail and modals; 9px for every control (buttons, inputs, nav links, icon buttons, pagination links). Icon tiles are 12px, toasts 12px, tags and scrollbar thumbs are fully round. Borders are 1px hairlines in Oatmeal; cards use a half-strength Oatmeal border. Icon tiles overlap the top edge of their card by 22px (negative margin), which is the signature silhouette.

## Components

### Buttons
- **Shape:** 9px radius, 40px tall, 14px Roboto 500, icon plus label with 8px gap.
- **Primary:** Burning Flame fill, Abyssal text, orange glow; hover mixes toward Abyssal (about 12%). Large variant is 48px, 15px text, 22px side padding, reserved for the single Add button in the title row.
- **Danger:** Truffle Trouble fill, Card Paper text, rust glow; only the confirm-delete button.
- **Ghost:** transparent with a strong Oatmeal-Muted border; Cancel and quiet actions. Hover fills Palladian.
- **Sidebar:** 34px, transparent, Palladian text with a faint oatmeal border; Log out.
- **Icon button:** 34px square, Muted icon, Palladian hover; the danger variant tints rust on hover. Used for row edit, row delete and modal close.
- **Press / disabled:** 1px downward press; disabled is 60% opacity.

### Cards / Containers
- **Corner Style:** 14px. **Background:** Card Paper. **Shadow:** Card shadow. **Border:** half-strength Oatmeal.
- **Padding:** 20px body; header 18px 20px 12px. Consecutive cards stack 24px apart.

### Number cards
Card with a 56px icon tile (Flame, Blue Fantastic or Truffle, a 24px Lucide icon) raised above the top-left edge, label and value right-aligned at the top, a hairline and a 13px Muted caption at the bottom. The feature card (Total savings) has a larger value.

### Inputs / Fields
- **Style:** 42px tall, Card Paper fill, 1px strong-line border, 9px radius, 15px text; labels above at 13px 500, 6px gap; two-column grid with 16px by 18px gaps, textareas span both.
- **Focus:** border shifts to Blue Fantastic plus a 2px Blue Fantastic outline offset 1px. Hover darkens the border to Muted.
- **Error:** border and message in Truffle Trouble; a form-level error block is a rust-tinted panel with a rust hairline.

### Navigation
Dark floating rail with a brand tile (Flame, letter S) and the word mark, a Dashboard link, then the seven record pages as one flat icon list, Django Admin pinned at the bottom, then the signed-in user name and Log out. Links are 14px Oatmeal on dark, 42px tall, 12px icon gap; hover adds a faint Palladian wash; the current page is a Flame pill with Abyssal text, weight 500 and a glow. The user chip lives in the rail, not the top bar. On small screens see Layout.

### Tables
14px with tabular numerals, uppercase 11px Muted column heads over an Oatmeal rule, no vertical rules, row hover tint, nowrap cells. Numeric columns carry right alignment. The last column holds the edit and delete icon buttons, pinned. Empty state is centred Muted text. Pagination sits under the table: summary left, 34px page links right, current page an Abyssal pill.

### Modals
Native dialog, 640px max, Card Paper, 14px radius, Modal shadow, 0.24s rise-and-fade entry. Head (18px title plus close icon button), body, and a right-aligned foot with Cancel (ghost) and the confirm button. Delete modals name the record and say it cannot be undone.

### Toasts
Abyssal pill at bottom-right with a Flame check for success; error toasts are Truffle Trouble. They leave on their own after about five seconds.

### Login
A centred 400px Card Paper card over the same dark gradient as the rail, with a full-width 44px primary button.

## Do's and Don'ts

### Do:
- **Do** keep the page on Palladian and raise content as Card Paper cards with 14px radius and the Card shadow.
- **Do** use exactly one large (48px) primary Burning Flame button per page, top right of the title row.
- **Do** use 9px radius for every control and keep Lucide icons at 18px (16px in links and compact nav, 24px in tiles), stroke 1.75.
- **Do** right-align money, in tabular numerals, and pin row actions to the right edge of wide tables.
- **Do** use Truffle Trouble only for delete and error states.
- **Do** keep text at 4.5:1 or better: Abyssal on paper, Abyssal on Flame, Muted (not lighter) for secondary text.

### Don't:
- **Don't** add a second accent, and do not introduce green for success or positive figures.
- **Don't** use hard offset shadows or pure black edges; depth is blurred and navy-tinted.
- **Don't** add a second typeface, and no glyph or emoji icons; Roboto and Lucide only.
- **Don't** put the signed-in user chip in the top bar.
- **Don't** introduce Bootstrap or Tailwind idioms; new styling goes into the one stylesheet using the existing custom properties.
