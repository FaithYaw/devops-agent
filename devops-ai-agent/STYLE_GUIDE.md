# DevOps AI Agent UI style guide

This document captures the design language used for the dashboard so future work matches the product visual system.

## Design direction

The interface uses a dark, high-contrast command-center aesthetic inspired by infrastructure and deployment dashboards. The goal is to feel technical, calm, and reliable without becoming visually noisy.

## Brand colors

- Background: `#020b17`
- Surface: `#0d1827`
- Surface alt: `#101d2f`
- Border: `rgba(132, 151, 180, 0.22)`
- Primary accent: `#d9ff4a`
- Secondary accent: `#67d3ff`
- Success: `#7ef9d3`
- Warning: `#f4d35e`
- Danger: `#ff7b7b`
- Text primary: `#edf6ff`
- Text muted: `#8a9ab0`

## Typography

- Primary font: `Inter`, `Segoe UI`, `sans-serif`
- Headline weight: 700
- Body weight: 400–500
- Use sentence case for labels and headings.
- Dashboard headings are large, high-contrast, and spaced with generous line-height.

## Layout rules

- Use a dark global shell with rounded cards and subtle borders.
- Keep a 16–20px spacing rhythm between major sections.
- Build KPI blocks as equal-width cards in a 4-column grid on desktop.
- Use a split layout for a primary workflow panel and a secondary environment panel.
- Keep links and key states subtle and blue or lime to preserve the system aesthetic.

## Accent usage

- Use `#d9ff4a` for emphasis, active status, primary actions, and attention cues.
- Use `#67d3ff` for neutral technical/information accents.
- Use `#7ef9d3` for success states.
- Use `#ff7b7b` for failures only.

## Components

- Cards: dark surfaces with rounded corners and light borders
- Metrics: bold values with muted labels and small trend text
- Status pills: tinted soft backgrounds with strong contrast text
- Workflow pipeline: clearly segmented status tiles with active, done, and queued states

## Examples

Use the design tokens above when creating new dashboard sections or cards so the UI remains consistent across pages.

## Implementation note

The theme is currently configured in `.streamlit/config.toml`, and the dashboard layout styling lives in `devops-ai-agent/app_pages/overview.py`.
