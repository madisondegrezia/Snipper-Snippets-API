from cryptography.fernet import Fernet

key = Fernet.generate_key()

print(f"Key: {key.decode()}")
