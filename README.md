# MPA (My Portable Apps)

<p align="center">
  <img src="icon64px.ico" alt="MPA Icon" width="64" height="64">
</p>

## About the Project

MPA is a portable and practical network management tool designed for Windows users. It automatically checks the status of your internet connection and local network access. By intelligently managing Wi-Fi profiles and connecting to a VPN, it ensures a smooth and uninterrupted user experience.

The core objective of MPA is to provide a collection of essential and portable network tools within a single package, allowing users to easily manage their network and bypass censorship.

## Key Features

* **Wi-Fi Profile Management**: Save and easily connect to different wireless networks.
* **Intelligent VPN Connection**: Automatically manages and monitors the status of the integrated VPN tool.
* **Smart Network Status Check**: Continuously monitors internet connectivity and provides detailed reports.
* **Simple and User-Friendly UI**: Designed with PyQt6, the user interface is clean and intuitive.
* **Advanced Logging**: Displays detailed, real-time logs that are easy to copy for troubleshooting.
* **Portable Environment**: All tools and dependencies are packaged into a single executable file, requiring no pre-installation of Python or other prerequisites.

---

### Integrated VPN

This application utilizes **Psiphon 3**, an open-source censorship circumvention tool, to provide VPN functionality. Psiphon 3 is designed to securely connect users to the internet in a variety of challenging network environments.

* **Project**: [Psiphon 3](https://github.com/Psiphon-Inc/psiphon)
* **Publisher**: Psiphon Inc.

---

## How to Get MPA

There are two main ways to use MPA.

### For End-Users (Recommended)

This method provides a standard and user-friendly installation experience, just like any other Windows application.

1.  Download the **MPA-Installer.exe** file from the [releases page](https://github.com/IbrahimNamdari/My-Portable-Apps/releases).
2.  Double-click the file and follow the installation steps.
3.  An icon will be created on your desktop and in the Start Menu for easy access.

### For Developers (From Source Code)

This method is for developers who want to run the application directly from the source code.

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/IbrahimNamdari/My-Portable-Apps.git](https://github.com/IbrahimNamdari/My-Portable-Apps.git)
    cd My-Portable-Apps
    ```
2.  **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application**:
    ```bash
    python main.py
    ```

---

## Building the Executable

To create the standalone `MPA-Portable.exe` and the `MPA-Installer.exe` files, follow these steps.

1.  **Build the portable executable**: Use the provided `build.bat` script to package all Python code and dependencies into a single file. This process requires PyInstaller (`pip install pyinstaller`).
    ```bash
    # In the project's root directory, run this command in cmd
    build.bat
    ```
2.  **Build the installer**: Once the portable executable is created in the `dist` folder, use the `installer.iss` script with **Inno Setup** to generate a full installer.