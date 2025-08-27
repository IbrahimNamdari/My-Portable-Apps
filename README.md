# MPA (My Portable Apps)

<p align="center">
  <img src="img/mpas.ico" alt="MPA Icon" width="128" height="128">
</p>

## About the Project

**MPA** is a portable toolbox for Windows that bundles several useful applications into a single package. The main goal of this program is to provide a set of essential tools for programmers, IT engineers, and anyone who works with computers on a daily basis, all in a convenient, portable format.

You can carry MPA on a USB flash drive or install it directly onto your system. Besides offering various applications, MPA also intelligently manages your network to maintain a stable connection in challenging conditions.

In areas with highly fluctuating internet connections, where the network might drop every few seconds or minutes, MPA can help keep you connected by attempting to automatically reconnect. The application also includes an integrated portable VPN, which is particularly useful for users in countries with strict internet regulations.

This software will be continuously developed to provide more features and convenience in the future. For example, it will eventually allow users to easily access detailed network information like IP addresses and more with just a few clicks. In essence, MPA is designed to be multiple essential programs in one.

## Key Features

* **Wi-Fi Profile Management**: Save and easily connect to different wireless networks.
* **Intelligent VPN Connection**: Automatically manages and monitors the status of the integrated VPN tool.
* **Smart Network Status Check**: Continuously monitors internet connectivity to maintain stability.
* **Simple and User-Friendly UI**: Designed with PyQt6, the user interface is clean and intuitive.
* **Advanced Logging**: Displays detailed, real-time logs that are easy to copy for troubleshooting.
* **Portable Environment**: All tools and dependencies are packaged into a single executable file.

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

1.  **Build the portable executable**: Use the provided `build.bat` script to package all Python code and dependencies into a single file.
    ```bash
    # In the project's root directory, run this command in cmd
    build.bat
    ```
2.  **Build the installer**: Once the portable executable is created in the `dist` folder, use the `installer.iss` script with **Inno Setup** to build the full installer.