import json
import logging
from flask import Flask, render_template, jsonify, request

app = Flask(__name__, static_url_path='/static')

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Load your JSON data for certificates_status
with open('certificates_status.json', 'r') as json_file:
    certificates_data = json.load(json_file)

# Load your JSON data for execution_history
with open('execution_history.json', 'r') as json_file:
    execution_data = json.load(json_file)


@app.route('/')
def home():
    """
    Render the home page with links to other endpoints.

    Returns:
        A rendered HTML template for the home page.
    """
    app.logger.info('Home page accessed')
    return render_template('home.html')


@app.route('/certificates')
def certificates_dashboard():
    """
    Render the certificates dashboard.

    Returns:
        A rendered HTML template for the certificates dashboard.
    """
    app.logger.info('Certificates dashboard accessed')

    # Check if the referrer is the same as the base URL
    is_iframe = request.referrer == request.host_url

    return render_template('dashboard.html', data=certificates_data, is_iframe=is_iframe)


@app.route('/execution')
def execution_history():
    """
    Render the execution history page.

    Returns:
        A rendered HTML template for the execution history page.
    """
    app.logger.info('Execution history accessed')

    # Check if the referrer is the same as the base URL
    is_iframe = request.referrer == request.host_url

    return render_template('execution.html', data=execution_data, is_iframe=is_iframe)


@app.route('/certificates_data')
def get_certificates_data():
    """
    Get JSON data for certificates.

    Returns:
        JSON data for certificates_status.
    """
    return jsonify(certificates_data)


@app.route('/execution_data')
def get_execution_data():
    """
    Get JSON data for execution history.

    Returns:
        JSON data for execution_history.
    """
    return jsonify(execution_data)


@app.errorhandler(404)
def page_not_found(error):
    """
    Handle 404 errors by rendering a custom error page.

    Returns:
        A rendered HTML template for the 404 error page.
    """
    app.logger.warning('Page not found: %s', request.url)
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
