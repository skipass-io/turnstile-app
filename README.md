# Turnstile app

`turnstile-app` - Python application for Raspberry Pi 5 with Pi Camera. 
This application provides the ability to check frames from a video stream and validate guests using it using `guest-recognition` by biometrics or QR code
## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Run](#run)
- [Finite-State Machine (FSM)](#finite-state-machine-fsm)


## Prerequisites

Before installing and running the `turnstile-app`, ensure your Raspberry Pi is set up correctly with the necessary hardware and software:

- **Raspberry Pi 5** with Raspberry Pi OS installed.
- **Raspberry Pi Camera Module** connected and enabled.

## Installation

Follow these steps to set up the project on your Raspberry Pi:

### Step 1: Update Raspberry Pi OS

First, update your Raspberry Pi OS to ensure all packages are up-to-date:

```bash
sudo apt update
sudo apt full-upgrade
```

### Step 2: Install Required Packages for Raspberry Pi Camera `picamera2`, `PySide2` and `pyzbar`
Install the necessary packages to enable and use the Raspberry Pi Camera:

```bash
sudo apt install -y libcamera-apps libcamera-dev python3-libcamera
```

And install the necessary packages to enable and use PySide2:

```bash
sudo apt-get install --upgrade python3-pyside2.qt3dcore python3-pyside2.qt3dinput python3-pyside2.qt3dlogic python3-pyside2.qt3drender python3-pyside2.qtcharts python3-pyside2.qtconcurrent python3-pyside2.qtcore python3-pyside2.qtgui python3-pyside2.qthelp python3-pyside2.qtlocation python3-pyside2.qtmultimedia python3-pyside2.qtmultimediawidgets python3-pyside2.qtnetwork python3-pyside2.qtopengl python3-pyside2.qtpositioning python3-pyside2.qtprintsupport python3-pyside2.qtqml python3-pyside2.qtquick python3-pyside2.qtquickwidgets python3-pyside2.qtscript python3-pyside2.qtscripttools python3-pyside2.qtsensors python3-pyside2.qtsql python3-pyside2.qtsvg python3-pyside2.qttest python3-pyside2.qttexttospeech python3-pyside2.qtuitools python3-pyside2.qtwebchannel python3-pyside2.qtwebsockets python3-pyside2.qtwidgets python3-pyside2.qtx11extras python3-pyside2.qtxml python3-pyside2.qtxmlpatterns
```

And install the necessary package to enable and use Pyzbar:

```bash
sudo apt-get install libzbar0
```

### Step 3: Create a Virtual Environment

Navigate to your project folder and create a virtual environment. The `--system-site-packages` flag is crucial because some necessary packages are only available system-wide:

```bash
python -m venv --system-site-packages env
source ./env/bin/activate
```

### Step 4: Install Poetry

Poetry is a dependency management tool that simplifies package installation. Install it using pip:

```bash
pip install poetry
```

### Step 5: Install Project Dependencies

Use Poetry to install all the required dependencies listed in your pyproject.toml:

```bash
poetry install
```

## Run 

```
python ./app/main.py
```

## Finite-State Machine (FSM)

The `turnstile-app` uses a **Finite-State Machine (FSM)** to manage the different states of the guest recognition process. The FSM is defined in the status_fsm.py file, and the following states are used:

### States

- **DETECTING**: This state indicates that the system is currently detecting a QR code or a face in the frame.
- **QRCODE_DETECTED**: This state indicates that a QR code has been detected in the frame.
- **FACE_DETECTED_LEVEL_A**: This state indicates that a face has been detected in the frame, but it is far away from the turnstile. The guest needs to get closer to start Face recognition.
- **FACE_DETECTED_LEVEL_B**: This state indicates that a face has been detected in the frame, and it is at the turnstile level. The guest needs to stay in the same place so that his face is recognized.
- **FACE_DETECTED_LEVEL_C**: This state indicates that a face has been detected in the frame, and it is very close to the turnstile. The guest needs to step back to start Face recognition
- **ALLOWED**: This state indicates that the guest has been recognized and is allowed to pass through the turnstile.
- **NOT_ALLOWED**: This state indicates that the guest has not been recognized and is not allowed to pass through the turnstile.