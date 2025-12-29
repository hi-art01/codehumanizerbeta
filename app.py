import time
from flask import Flask, render_template, request, jsonify
from humanizer import humanize_code

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/humanize', methods=['POST'])
def humanize():
    data = request.get_json()
    input_code = data.get('code', '')
    options = data.get('options', {})
    
    output_code = humanize_code(input_code, options)

    return jsonify({'code': output_code})

if __name__ == '__main__':
    app.run(debug=True)
