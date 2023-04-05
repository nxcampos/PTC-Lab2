from cryptography.fernet import Fernet

# generate a new key
key = Fernet.generate_key()

# save the key to a file
with open("fernet_key.key", "wb") as key_file:
    key_file.write(key)

print("Nova chave gerada e gravada com o nome 'fernet_key.key'")