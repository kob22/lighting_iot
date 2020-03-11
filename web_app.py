from web_app import create_app, db

app = create_app()


if __name__ == '__main__':

    # Flask-MQTT only supports running with one instance
    app.run(host='0.0.0.0', port=5000, use_reloader=False, debug=True)