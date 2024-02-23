# write_timestamp.py
from datetime import datetime

# Format the current timestamp
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Write the timestamp to a file
with open("timestamp.txt", "a") as file:
    file.write(f"{current_time}\n")
