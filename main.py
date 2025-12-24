# ----------------------------------------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------------------------------------- #

from src.app import create_app # função dentro de __init__.py
from src.app.extensions import db # não cria outro db, importa a mesma instância; o db existe e não está ligado a nenhuma app

# ----------------------------------------------------------------------------------------------- #
# Inicializações
# ----------------------------------------------------------------------------------------------- #

# iniciar aplicação
app = create_app()

# ----------------------------------------------------------------------------------------------- #
# Executar o app localmente
# ----------------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Banco de dados criado!')
        app.run(debug = True)
    





