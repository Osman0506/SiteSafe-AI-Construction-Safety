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
2.  Install dependencies: `pip install -r requirements.ritf`
3.  Run the detector - with the 'Code.py'

    ### 📥 Download the Model
Due to GitHub file size limits, the trained model weights are hosted externally.
[👉 Click Here to Download best.pt (Google Drive)](https://drive.google.com/drive/folders/1q9Y6EyhGl8g7J7viVN56xvG3_rTkMej3?usp=share_link)

**Setup:**
1. Download `best.pt` from the "Models" Folder.
2. Create a folder named `models` inside this project.
3. Place `best.pt` inside that folder.
