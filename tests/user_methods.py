# Adicionar método set_password ao modelo User
from flask_bcrypt import Bcrypt

# Adicionar ao final do arquivo app.py
def set_password(self, password):
    """Define a senha hash do usuário"""
    self.password = bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(self, password):
    """Verifica se a senha está correta"""
    return bcrypt.check_password_hash(self.password, password)

# Adicionar métodos ao modelo User
User.set_password = set_password
User.check_password = check_password
