# Stride Studio

A professional desktop application built with Python and PySide6 for analyzing and annotating videos or live camera feeds using Ultralytics YOLO models.



## Features

* **Dual Mode Operation:** Choose between processing a pre-recorded video file or a live camera feed.
* **Video Loading:** Load video files via drag-and-drop or a file dialog. Supported formats: MP4, AVI, MOV, MKV, WMV.
* **Live Camera Processing:** Select an available camera and process its feed in real-time.
* **Camera Selection:** If multiple cameras are detected, choose the desired one from a dropdown.
* **Task/Model Selection:** Select the desired YOLO task (Pose, Detection, Segmentation, Classification, Oriented Bounding Box) via a dropdown. The corresponding pre-trained model (`yolo11x*`) will be used.
* **Playback Controls:** Play, pause, skip, and seek through video files (disabled for live feeds).
* **Variable Speed:** Adjust playback speed for video files.
* **Frame Rotation:** Rotate the video/camera preview and output by 90, 180, or 270 degrees.
* **Video Saving:** Save the processed video (with overlays) to a new file (disabled for live feeds).
* **Dark Theme:** Uses a custom dark theme for the user interface.

## Requirements

* **Python:** 3.10
* **Conda:** For environment management. Miniforge or Anaconda is recommended.
* **Dependencies:** See `environment.yml` for Conda environment setup or `requirements.txt` for pip installation. Key dependencies include:
  * PySide6
  * OpenCV-Python
  * Ultralytics
  * PyTorch (GPU recommended for performance, CUDA setup handled by Conda if available)

## Setup

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd stride-studio # Navigate into the main project directory
    ```

2. **Create Conda Environment:**
    It's recommended to use the provided `environment.yml` file to create a Conda environment with all necessary dependencies, including the correct PyTorch version compatible with your CUDA setup (if applicable).

    ```bash
    conda env create -f environment.yml
    ```

3. **Activate Environment:**

    ```bash
    conda activate Stride_Studio
    ```

4. **(Alternative) Pip Installation:**
    If you prefer pip, you can try installing from `requirements.txt` after creating a Python 3.10 environment, but managing PyTorch/CUDA might require manual steps.

    ```bash
    pip install -r requirements.txt
    # You might need to install PyTorch separately based on your system:
    # See https://pytorch.org/get-started/locally/
    ```

## Usage

1. **Activate the Conda environment:**

    ```bash
    conda activate Stride_Studio
    ```

2. **Run the application:**

    The easiest way is to run the main package directly:

    ```bash
    cd path/to/stride-studio
    python -m stride_studio
    ```

3. **Choose Mode:** Upon launch, a dialog will ask you to select either "Live Camera" or "Load Video".

4. **Live Camera Mode:**
    * Select the desired camera from the "Camera:" dropdown (if multiple are available).
    * Select the desired analysis task ("Pose", "Detection", etc.) from the "Model:" dropdown.
    * Processing will start automatically.
    * Use the Play/Pause button to control the live preview.

5. **Load Video Mode:**
    * A file dialog will appear. Select the video file you want to process.
    * An input dialog will ask you to choose the analysis task ("Pose", "Detection", etc.).
    * Processing will start automatically.
    * Use the transport controls (play, pause, seek slider, speed) to navigate the video.

6. **Processing:** View the annotated video/camera feed in the main window. A progress bar indicates processing status for videos.

7. **Change Task/Model:** Selecting a different task from the "Model:" dropdown will automatically re-process the video/live feed with the new model.

8. **Save (Video Mode Only):** After processing a video file, specify an output filename (optional) and click "Save Video" to save the annotated result.

## Models

The application uses Ultralytics YOLO models located in the `models/` directory.
The specific model used (`yolo11x-pose.pt`, `yolo11x.pt`, etc.) is determined by the task selected in the "Model:" dropdown.

## Author

* Alfredo Sandoval
