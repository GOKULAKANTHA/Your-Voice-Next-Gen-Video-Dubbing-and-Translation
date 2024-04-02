import subprocess
import platform

def run_another_script():
    script_path = "your_voice.py"
    if platform.system() == "Windows":
        subprocess.Popen(["python", script_path], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen(["python3", script_path])

if __name__ == "__main__":
    run_another_script()
