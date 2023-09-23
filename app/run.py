from app import create_app

# Create an instance of the Flask app
app = create_app()

# This conditional is used when running locally and not via uwsgi
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)