import os
import subprocess

def install(package):
    subprocess.check_call([os.sys.executable, "-m", "pip", "install", package])

def main():
    print("Installing required libraries...")

    # List of libraries required for the script
    libraries = [
        "opencv-python",    # For cv2 (OpenCV)
        "numpy",            # For array processing
        "pywin32",          # For win32api
        "bettercam",        # For bettercam (camera capture)
        "keyboard",         # For hotkey management
        "psutil",           # For process management (if needed)
        "socket",           # For networking (if used in the script)
        "threading",        # For multithreading
        "time",             # For timing functionalities
        "random",           # For random number generation
        "hashlib",          # For generating hashes
        "ctypes",           # For working with Windows libraries
        "json"              # For configuration handling
    ]

    # Install each required library
    for lib in libraries:
        try:
            install(lib)
            print(f"{lib} installed successfully")
        except Exception as e:
            print(f"Failed to install {lib}: {e}")

    print("All libraries installed")

if __name__ == "__main__":
    main()
