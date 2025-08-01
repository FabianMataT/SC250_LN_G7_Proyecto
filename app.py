from app import create_app

app = create_app()
app.secret_key = '384759834y8bhfdsn348'

if __name__ == '__main__':
    app.run(debug=True)
