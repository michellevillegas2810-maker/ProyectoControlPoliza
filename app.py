# app.py
# Capa: Aplicacion principal - crea la app Flask y registra el Blueprint.
# La variable se llama 'app'.

from flask import Flask
from controllers.polizas_controller import bp

app = Flask(
    __name__,
    template_folder="views",
    static_folder="public/static",
    static_url_path="/static"
)

app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)