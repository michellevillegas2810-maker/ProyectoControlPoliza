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
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)