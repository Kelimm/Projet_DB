from flask import Flask, jsonify
from routes.requirements import requirements_bp
from routes.testers import testers_bp
from routes.tests import tests_bp
from routes.campaigns import campaigns_bp


app = Flask(__name__)
# Permet d'afficher les données dans l'ordre que l'on souhaite
app.json.sort_keys = False

app.register_blueprint(requirements_bp)
app.register_blueprint(testers_bp)
app.register_blueprint(tests_bp)
app.register_blueprint(campaigns_bp)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "Home_msg": "API de gestion de tests fonctionnels"
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
