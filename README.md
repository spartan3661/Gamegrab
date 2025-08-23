# Game-OCR
![status](https://img.shields.io/badge/status-beta-orange)
![wip](https://img.shields.io/badge/🚧-work_in_progress-red)

OCR app for video games — capture game windows, run OCR (EasyOCR), and translate text.

Game-OCR lets you capture text directly from PC game windows.  
It supports **Japanese + English OCR** using [EasyOCR](https://github.com/JaidedAI/EasyOCR) and integrates with **DeepL** for automatic translation.
Built with **PySide6** for the GUI, it’s designed to help players understand menus, dialogues, and HUD elements in games that don’t have English localization.


## Disclaimer

This project is **experimental** and currently in **beta**.  
It is not a full-fledged app — expect bugs, missing features, and breaking changes.  

Use at your own risk, and please report issues if you try it out!

## Features
- Simple PySide6 GUI with screenshot, refresh, OCR, and API settings.
- EasyOCR with GPU acceleration.
- DeepL integration.
- Captures any window including games.
- Works for full screen, borderless, and windowed modes.

## Note
- Currently, you must compile the dll file needed to run the OCR. In the future, the dll will be packaged into an exe.
- You can skip compiling the DLL file if you use the dev branch.
- You must **grab a screen at least once** before OCR is enabled.
- You must get at DeepL API key (free) in order to perform translation.
- Image will appear low quality if viewed on a monitor with higher resolutions than the game window's monitor.

## Requirements
- tested on python **3.11.5**
- (Optional) Visual Studio 2022 with **Desktop Development with C++** workload to build DLL files
- (Optional) PyTorch (GPU Acceleration)

## Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/spartan3661/Game-OCR.git
   ```
2. cd Game-OCR
3. Create a venv (Optional, recommended) and install dependencies.
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. In cpp_backend open wgc_core.sln in Visual Studio 2022 and build for x64. This creates an x64 folder in cpp_backend
5. Copy the generated wgc_core.dll **from** cpp_backend/wgc_core/x64 **to** cpp_backend
6. run main.py

## Usage
1. Launch the app with `python main.py` from project directory.
2. Add a DeepL API key in **Settings** to enable translation.
3. Select a game window from the dropdown.
4. Click **Screen Grab** to capture it.
5. Click **OCR** to recognize text.

## License

MIT License — see [LICENSE](LICENSE) for details.
