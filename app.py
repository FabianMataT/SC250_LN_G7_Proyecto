from app import create_app
from app.routes import main

app = create_app()
app.secret_key = '384759834y8bhfdsn348'

if __name__ == '__main__':
    app.run(debug=True)
    
app.register_blueprint(main)

