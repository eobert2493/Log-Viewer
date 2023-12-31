# Log Viewer

This repository contains a Log Viewer application.

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/your-username/log-viewer.git
   ```

2. Create a virtual environment named `venv`:

   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

4. Install the required packages from the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the Log Viewer script, use the following command:

    ```bash
    python3 LogViewer.py
    ```

To build the application as a reusable executable:

    ```bash
    pyinstaller --onefile LogViewer.py
    ```

