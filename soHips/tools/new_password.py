import random
import string 

#Genera una contrasena random
def random_password():
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = random.sample(password_characters, 8)
    password = "".join(password)
    return password