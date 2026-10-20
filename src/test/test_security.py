from security import hash_password, verify_password


password = "123456"

password_hash = hash_password(password)

print("Hash:", password_hash)

print("Correct password:",
      verify_password("123456", password_hash))

print("Wrong password:",
      verify_password("wrongpassword", password_hash))
