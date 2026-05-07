# Smart Transit Hub: Real-Time Commuter Forecasting

## The Problem
Opportunity inequality in the Philippines is heavily exacerbated by severe public transit congestion. Hours spent waiting in line strip citizens of time for education, family, and decent work. 

## Our Solution
A real-time Smart Transit Dashboard aligned perfectly with **SDGs 4, 8, 10, and 11**. We leverage Computer Vision, Artificial Intelligence, and Data Science to monitor terminal congestion, predict commuter wait times, and offer actionable alternative routes. By giving citizens their time back, we build smarter, more equitable cities.

**Live Demo Scope:** For this presentation, our fully functional ML pipeline focuses exclusively on the **PITX (Parañaque Integrated Terminal Exchange)** during rush hour. The architecture, however, is designed to scale to national infrastructure projects like the NSCR and MRT-7.

## Tech Stack
* **Frontend:** Vanilla HTML/JS, Tailwind CSS (CDN)
* **Backend:** Python 
* **Computer Vision:** Ultralytics YOLOv11 Nano (`yolo11n.pt`), OpenCV
* **Data Science/AI:** Custom predictive forecasting and dynamic routing algorithms

## How to Run the Demo
1. Ensure Python 3.x is installed along with the dependencies listed in `requirements.txt`.
2. Place the sample CCTV footage at `data/pitx_rush_hour.mp4`.
3. Run `python app.py` to start the backend API and video processing stream.
4. Open `index.html` in your browser and navigate to the Commuter Portal to view the live AI in action.