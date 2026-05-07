# Design System: ViaVidentis

## 1. Visual Identity & Atmosphere
- **Concept:** "The Royal Marauder" — A high-prestige, high-contrast interface blending historical academic elegance with modern "Smart City" utility.
- **Mood:** Authoritative, Precise, and Magical.
- **Goal:** To provide a "Lumos" (light) effect where critical transit data glows against a dark, focused background.

## 2. Color Palette (The "Venerable Gold" System)
*Note: This palette uses high-contrast accessibility standards.*


| Role | Hex Code | Usage |
| :--- | :--- | :--- |
| **Foundation** | `#000000` | **Deep Onyx** — Main application background. |
| **Surface** | `#1A1A1A` | **Charcoal** — Cards, sidebars, and container backgrounds. |
| **Primary Accent**| `#FFC107` | **Tiger Gold** — Interactive elements, active routes, and "Magic Eye" icons. |
| **Text (High)** | `#FFFFFF` | **Pure White** — Primary titles and body text. |
| **Text (Low)** | `#E0E0E0` | **Platinum Grey** — Metadata, timestamps, and secondary info. |
| **Border** | `#333333` | **Iron** — Subtle dividers and card outlines. |

## 3. Semantic Status Indicators
These colors overlay the base palette to indicate real-time vehicle occupancy:
- **Comfortable (<50%):** `#FFC107` (The Gold Standard)
- **Crowded (50-90%):** `#B8860B` (Darker Gold/Bronze)
- **Full (>90%):** `#FF4444` (Alert Red — used sparingly for critical warnings)

## 4. Typography Hierarchy
- **Font Stack:** `Inter`, `system-ui`, `sans-serif`.
- **Display:** `24px / Bold / #FFC107` — Main App Title and Destination.
- **Subheading:** `18px / Semi-bold / #FFFFFF` — Route Option headers.
- **Labels:** `12px / Monospace / #E0E0E0` — Live IoT data and "Seats Remaining."

## 5. Component Specifications
- **The "Fleet Card":** Surfaces are `#1A1A1A` with a left-border accent of `#FFC107`.
- **Navigation Map:** Custom Folium tiles (Dark Mode). Route paths are drawn in glowing Tiger Gold.
- **IoT Feed Monitor:** A video container with a `#FFC107` glowing border when the YOLO model is actively detecting passengers.
- **Buttons:** Solid Tiger Gold (`#FFC107`) with Black text (`#000000`) for maximum visual "pop."

## 6. Layout Principles
- **Dual-Pane View:**
    - **Control Wing (Sidebar):** Toggles between "Commuter App" and "Vehicle IoT Feed."
    - **Intelligence Hub (Main):** Map-centric with floating cards for "Smart Recommendations."
- **UX Rule:** "Never hide the map." All information cards must be semi-transparent or collapsible to keep the spatial context visible.

## 7. AI Agent UI Prompt Guide
"Execute all UI generation using the **Venerable Gold** system. All containers must have a background of `#1A1A1A`. All primary actions and 'Magic' features must use `#FFC107`. When a vehicle is 'Full', change the route card border to `#FF4444` to signal an automatic reroute."
