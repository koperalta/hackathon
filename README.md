# 🪄 ViaVidentis
*The Smart Transit Oracle | Built by Team "L's Not Found" @ Codewarts Hackathon*

**ViaVidentis** is a real-time smart transit application designed to solve the everyday nightmare of crowded commutes. Instead of tracking unpredictable street traffic, we bring Japanese-style subway efficiency to major Philippine transport hubs (like the PITX terminal).

By combining edge AI cameras with a sleek, dark-mode "Live Departures Board," we help commuters avoid "siksikan" (overcrowded) boarding gates and find the fastest, most comfortable ride home.

---

## ✨ The Magic, Explained Simply
Normally, transit apps just tell you the schedule. But what if the queue at the gate already has 100 people waiting for a bus that only holds 40? 

**Here is how ViaVidentis fixes this Opportunity Inequality:**
1. **The "Eyes" (Edge IoT):** We simulate cameras mounted above the terminal boarding gates. These cameras use AI (YOLOv11) to constantly count how many passengers are in line.
2. **The "Brain" (Flask Routing):** That real-time queue data is instantly sent to our backend engine, cross-referencing it with the capacity of the incoming bus.
3. **Your Guide (The App):** If the app sees that the queue at your gate exceeds the bus capacity, it automatically flags the route as "Siksikan" and directs you to a secondary gate or transport mode with a shorter line.

---

## 🗺️ A Commuter's Journey (The User Experience)

Imagine opening the app inside the chaotic PITX terminal during the evening rush hour:

### 1. The Royal Marauder Interface
You are greeted by an elegant, deep onyx (`#000000`) dashboard with platinum grey text. It feels authoritative, focused, and magical. The screen displays a **Live Departures Board** with active boarding gates glowing in bright **Tiger Gold** (`#FFC107`). 

### 2. Live Gate Cards
You tap on your usual destination. A sleek "Gate Card" expands. You don't just see the ETA; you see a live feed from the IoT system: 
*`Gate 4 Status: Comfortable | Queue: 12 pax | Bus Capacity: 40`*
The card has a glowing gold border, signaling that you are guaranteed a seat.

### 3. The Auto-Reroute (Magic in Action)
Suddenly, a massive crowd floods Gate 4. The AI camera detects the surge. 

In real-time, your gate on the board flashes **Alert Red** (`#FF4444`). The queue is now >90% of the incoming bus's capacity. Without you needing to press a single button, ViaVidentis calculates a new strategy. A glowing gold notification appears, directing you to Gate 6, where a different route heading to the same general area has a completely empty line. You get a comfortable seat, entirely avoiding the crowd.

---

## 🛠️ Under the Hood (Our "Spells")
We believe in "Not Reinventing the Wheel." Here is the open-source magic making this possible in our 24-hour sprint:

* **Backend Framework:** `Python Flask` (Handling API routes and asynchronous video streaming)
* **UI & Styling:** Native `HTML/JS` tailored with our custom "Venerable Gold" CSS system
* **Computer Vision:** `ultralytics` & `opencv-python` (Pre-trained YOLOv11n weights for instant crowd detection)
* **Data Processing:** `pandas` (Processing mock "Open Data Philippines" terminal logistics)

---

## 🚀 How to Run Locally

1. Clone this repository.
2. Ensure you have Python 3.10+ installed.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt