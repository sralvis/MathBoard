from flask import Flask, request, jsonify
from flask_cors import CORS
from math_engine import evaluate_expression, evaluate_worksheet
import logging

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    app.logger.debug(f"Received data: {data}")

    # Check if this is a bulk worksheet evaluation
    if 'regions' in data:
        try:
            results = evaluate_worksheet(data['regions'])
            return jsonify({'results': results})
        except Exception as e:
            app.logger.error(f"Error evaluating worksheet: {e}")
            return jsonify({'error': str(e)}), 400

    # Legacy single expression evaluation (fallback)
    expression = data.get('expression')
    if not expression:
        return jsonify({'error': 'No expression provided'}), 400

    try:
        result = evaluate_expression(expression)
        app.logger.debug(f"Calculated result: {result}")
        return jsonify({'result': str(result)})
    except Exception as e:
        app.logger.error(f"Error evaluating: {e}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
