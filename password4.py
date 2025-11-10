from cryptography.fernet import Fernet

texto = "x?1_p-M.4!em"


clave = Fernet.generate_key()
f = Fernet(clave)

texto_encriptado = f.encrypt(texto.encode())
print("Texto encriptado:", texto_encriptado)

texto_desencriptado = f.decrypt(texto_encriptado).decode()
print("Texto desencriptado:", texto_desencriptado)

es_correcto = texto == texto_desencriptado
print("¿El texto es correcto?", es_correcto) 