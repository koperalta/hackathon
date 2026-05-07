# UI/UX Design Architecture

## Aesthetic Philosophy
For the Commuter App (`commuter.html`), we deliberately avoided complex, data-heavy dashboard layouts. Commuting is inherently stressful; therefore, the UI must be calm, intuitive, and instantly readable. We pivoted to a **"Smart Home Security Camera"** mobile-first aesthetic, providing a premium, native-app feel directly in the browser.

## Design Language (Tailwind CSS)
* **Theme:** Strictly Light Mode for maximum visibility in bright, outdoor terminal environments.
* **Color Palette:** White backgrounds (`bg-white`), light gray secondary areas (`bg-gray-50`), and dark charcoal text for high contrast and readability.
* **Typography:** Clean, modern sans-serif stack to maintain a sleek, utilitarian look.
* **Styling:** Soft drop shadows (`shadow-md`, `shadow-lg`) and smooth, rounded corners (`rounded-2xl`, `rounded-3xl`) on all cards to mimic high-fidelity apps like iOS Home or Ring.

## Core UI Components
1. **The Hero Card (Live Feed):** The focal point of the app. A prominent, rounded rectangle displaying the live OpenCV/YOLO video feed of the PITX queue. It features a highly visible overlay badge stating the **Estimated Wait Time** in minutes, giving commuters the most crucial information instantly.
2. **Smart Route Alternative Card:** Positioned directly below the video feed in a soft accent color. If AI predicts severe delays, this card dynamically surfaces a faster transit alternative.
3. **Horizontal Navigation:** A scrollable menu of pill-shaped tags for quick switching between terminal areas, keeping the interface uncluttered.