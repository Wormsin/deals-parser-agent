import subprocess
import time

# Start mails reciver
print("Starting mail reciver...")
email_process = subprocess.Popen(["python", "email_reciver.py"])
time.sleep(2)

# Start the folder monitoring script
print("Starting folder monitoring...")
monitor_process = subprocess.Popen(["python", "monitor.py"])

# Give it some time to start
time.sleep(2)

# Start the Streamlit app
print("Starting Streamlit app...")
streamlit_process = subprocess.Popen(["streamlit", "run", "mvp_app.py"])

try:
    # Keep the script running to monitor both processes
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # If the user stops the script (CTRL+C), terminate both processes
    print("\nShutting down...")
    monitor_process.terminate()
    email_process.terminate()
    streamlit_process.terminate()