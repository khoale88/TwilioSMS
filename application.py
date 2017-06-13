from twilio_app import app
app.config["APP_HOST"] = '0.0.0.0'
app.config["APP_PORT"] = 5000
app.config["APP_DEBUG"] = True

if __name__ == "__main__":
    app.run(debug=app.config["APP_DEBUG"],
            host=app.config["APP_HOST"],
            port=app.config["APP_PORT"])
