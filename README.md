# 🪄 ViaVidentis
*The Smart Transit Oracle | Built by Team "L's Not Found" @ Codewarts Hackathon*

**ViaVidentis** is a real-time smart transit application designed to solve the everyday nightmare of crowded commutes. Instead of guessing if a Jeepney or Bus is full, ViaVidentis *knows*.

By combining edge AI cameras with a sleek, dark-mode map, we help commuters avoid "siksikan" (overcrowded) vehicles and find the most comfortable route home.

---

## ✨ The Magic, Explained Simply
Normally, map apps just tell you the fastest way from Point A to Point B. But what if the jeepney on that route is completely full? 

**Here is how ViaVidentis fixes this:**
1. **The "Eyes" (Edge IoT):** We simulate cameras mounted inside public vehicles. These cameras use AI (YOLOv11) to constantly count how many passengers are inside.
2. **The "Brain" (Cloud Routing):** That head-count is instantly sent to our routing engine.
3. **Your Guide (The App):** If the app sees that your upcoming ride is >90% full, it automatically redraws your map to suggest a different route where vehicles are less than 50% full. 

---

## 🗺️ A Commuter's Journey (The User Experience)

Imagine opening the app during the chaotic evening rush hour:

### 1. The Royal Marauder Interface
You are greeted by an elegant, deep onyx (`#000000`) dashboard with platinum grey text. It feels authoritative, focused, and magical. The map dominates the screen—**we never hide the map.** Your possible routes glow across the dark city streets in bright **Tiger Gold** (`#FFC107`). 

### 2. Live Fleet Cards
You tap on your usual route. A sleek, semi-transparent "Fleet Card" floats over the map. You don't just see the ETA; you see a live feed from the IoT system: 
*`Status: Comfortable | Seats Remaining: 12`*
The card has a glowing gold border, signaling that you are good to go.

### 3. The Auto-Reroute (Magic in Action)
Suddenly, a large group boards the jeepney two stops ahead of you. The AI camera detects the crowd. 

In real-time, the route on your screen flashes **Alert Red** (`#FF4444`). The vehicle is now >90% full. Without you needing to press a single button, ViaVidentis calculates a new path. A new glowing gold line appears on the map, directing you to a secondary jeepney route just one block away that is completely empty. You get a comfortable seat, entirely avoiding the crowd.

---

## 🛠️ Under the Hood (Our "Spells")
We believe in "Not Reinventing the Wheel." Here is the open-source magic making this possible in 24 hours:

* **UI Framework:** `Streamlit` (styled with custom CSS for our "Venerable Gold" aesthetic)
* **Maps:** `streamlit-folium` (Open-source alternative to Google Maps)
* **Computer Vision:** `ultralytics` (Pre-trained YOLOv11n weights for instant person-detection)
* **Routing:** Mocked `OSRM` (Open Source Routing Machine) logic
* **Data Processing:** `pandas` (Processing "Open Data Philippines" transit routes via `routes.json`)

---

## 🚀 How to Run Locally

1. Clone this repository.
2. Install the requirements: `pip install -r requirements.txt`
3. Run the Streamlit app: `streamlit run app.py`
4. Use the sidebar to toggle between the **Commuter App** (Map view) and the **Vehicle IoT Feed** (Camera view).