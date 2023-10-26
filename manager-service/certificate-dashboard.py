from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

# Load your JSON data
with open('certificates_status.json', 'r') as json_file:
    data = json.load(json_file)


@app.route('/')
def dashboard():
    return render_template('dashboard.html', data=data)


@app.route('/data')
def get_data():
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
