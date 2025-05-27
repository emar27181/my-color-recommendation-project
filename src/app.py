from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("color_recommend.html")
    # return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/color_recommend")
def color_recommend():
    return render_template("color_recommend.html")


if __name__ == "__main__":
    app.run(debug=True)
