# AI & Machine Learning Pipeline

This project utilizes three distinct, interconnected AI modules (agents) to process real-world visual data and deliver actionable insights.

## 1. Computer Vision Agent (`people_counter.py` & `yolo11n.pt`)
* **Core Tech:** Ultralytics YOLOv11 Nano model.
* **Function:** Ingests the live video stream (`data/pitx_rush_hour.mp4`) and processes it frame-by-frame using OpenCV. 
* **Execution:** Detects the `person` class, draws bounding boxes around commuters, and maintains a highly accurate, running count of people in the terminal queue. It simultaneously streams this visual output to the frontend via a multipart/x-mixed-replace feed so users can verify the data.

## 2. Predictive Forecasting Agent (`forecasting_ai.py`)
* **Core Tech:** Custom Data Science Logic.
* **Function:** Translates raw computer vision counts into actionable time metrics.
* **Execution:** Calculates the estimated wait time dynamically based on the live queue density (from the CV Agent), average bus capacity, and historical departure intervals. It serves this metric to the frontend via the `/api/pitx-status` endpoint.

## 3. Dynamic Routing Agent (`route_ai.py`)
* **Core Tech:** Rule-based/Heuristic AI Routing.
* **Function:** Directly addresses opportunity inequality by offering commuters a way to bypass congestion.
* **Execution:** Continuously monitors the output of the Forecasting Agent. If the wait time at PITX exceeds a predefined critical threshold, the agent calculates a faster alternative route using secondary transit options (e.g., EDSA Carousel) and pushes this suggestion to the UI, complete with estimated time saved.