# 🦺 SiteSafe AI: Construction Compliance System

### 🚀 Project Overview
**SiteSafe** is a computer vision application built to automate safety monitoring on construction sites. It uses a custom-trained **YOLOv8** neural network to detect PPE (Personal Protective Equipment) compliance in real-time.

**Status:** `v3.0 (Stable)`
**Experimental:** `v4.0 (Commercial Scale - In Progress)`

### ⚡ Key Capabilities
* **Safety Gear Detection:** Identifies `Hard Hats` and `Safety Vests` instantly.
* **Worker Tracking:** Detects persons on site to ensure no one is entering dangerous zones.
* **Violation Logic:** Can logically determine if a `Person` is present *without* a `Helmet`.
* **Performance:** Optimized for real-time inference on standard hardware.

###  Technical Stack
* **Model:** YOLOv8 (Custom Trained)
* **Dataset:** 400+ Manual Annotations (SiteSafe Dataset) + 7,000+ External Images (Hard Hat Universe)
* **Augmentation:** Mosaic, tiling, and exposure adjustments.

### 💻 How to Test
1.  Clone the repository.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the detector:
    ```bash
    python inference.py
    ```
