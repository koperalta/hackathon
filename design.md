# Design System: ViaVidentis (Terminal Edition)

## 1. Visual Identity & Atmosphere
- **Concept:** "The Royal Marauder" — A high-prestige, high-contrast interface blending historical academic elegance with modern "Smart City" utility. Think of a magical, futuristic train station departures board.
- **Mood:** Authoritative, Precise, and Magical.
- **Goal:** To provide a "Lumos" (light) effect where critical transit and queue data glows against a dark, focused background.

## 2. Color Palette (The "Venerable Gold" System)
*Note: This palette uses high-contrast accessibility standards.*

| Role | Hex Code | Usage |
| :--- | :--- | :--- |
| **Foundation** | `#000000` | **Deep Onyx** — Main application background. |
| **Surface** | `#1A1A1A` | **Charcoal** — Gate Cards, sidebars, and container backgrounds. |
| **Primary Accent**| `#FFC107` | **Tiger Gold** — Interactive elements, active departures, and "Magic Eye" icons. |
| **Text (High)** | `#FFFFFF` | **Pure White** — Primary titles and body text. |
| **Text (Low)** | `#E0E0E0` | **Platinum Grey** — Metadata, ETAs, and secondary info. |
| **Border** | `#333333` | **Iron** — Subtle dividers and card outlines. |

## 3. Semantic Status Indicators
These colors overlay the base palette to indicate real-time gate queue density:
- **Comfortable (<50 pax):** `#FFC107` (The Gold Standard)
- **Crowded (50-100 pax):** `#B8860B` (Darker Gold/Bronze)
- **Siksikan (>100 pax):** `#FF4444` (Alert Red — Flashes when a gate is overwhelmed)

## 4. Typography Hierarchy
- **Font Stack:** `Inter`, `system-ui`, `sans-serif`.
- **Display:** `24px / Bold / #FFC107` — Main App Title and Terminal Name.
- **Subheading:** `18px / Semi-bold / #FFFFFF` — Gate Options and Departure headers.
- **Labels:** `12px / Monospace / #E0E0E0` — Live IoT Data, "Queue Length," and "Bus Capacity."

## 5. Component Specifications
- **The "Gate Card":** Surfaces are `#1A1A1A` with a left-border accent of `#FFC107`. This replaces the traditional map marker.
- **Live Departures Board:** The central UI element. Rows of upcoming departures featuring glowing Tiger Gold text for ETAs.
- **IoT Feed Monitor:** A video container with a `#FFC107` glowing border when the YOLO model is actively detecting the passenger queue.
- **Buttons:** Solid Tiger Gold (`#FFC107`) with Black text (`#000000`) for maximum visual "pop."

## 6. Layout Principles
- **The "Terminal-First" View:**
    - The main focus is the Live Departures Board, which organizes commuter flow *before* they board.
- **UX Rule:** "Never hide the board." All alternative route suggestions or warnings must appear as non-intrusive floating banners or by expanding an existing Gate Card.

## 7. AI Agent UI Prompt Guide
"Execute all HTML/CSS generation using the **Venerable Gold** system. All containers must have a background of `#1A1A1A`. All primary actions must use `#FFC107`. If a `gate` queue reaches 'Siksikan' status, change the `Gate Card` border to `#FF4444` and trigger the auto-reroute UI animation."