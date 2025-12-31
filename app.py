from flask import Flask, request
import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def webhook():
    print("==== SSRF HIT ====")
    print("Time:", datetime.datetime.utcnow())
    print("Method:", request.method)
    print("Headers:", dict(request.headers))
    print("Args:", request.args)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
