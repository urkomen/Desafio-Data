"""
API Flask del recomendador.

Carga el modelo y los embeddings UNA vez al arrancar (no por petición).

Endpoint:
  POST /recomendar
  {
    "id_user": 10,
    "consulta": "Museo Bilbao planes en familia",   # texto libre del buscador
    "filtros": {
      "carrito": true,
      "cambiador": false,
      "interior": true,
      "accesible": false,
      "mascota": true,
      "gratis": false
    }
  }
"""
from flask import Flask, request, jsonify

import config
import data_access as da
from recommender import Recomendador

app = Flask(__name__)

# El recomendador se inicializa una sola vez (lazy) para no cargar el
# modelo de 2GB al importar el módulo (p. ej. en tests).
store = None
recomendador = None


def init(stub_model=None):
    """Carga embeddings + modelo una sola vez. Pasa stub_model para tests."""
    global store, recomendador
    if recomendador is not None:
        return recomendador

    print("Cargando embeddings...")
    store = da.EmbeddingStore()

    if stub_model is not None:
        model = stub_model
    else:
        print(f"Cargando modelo {config.MODELO_ST} (puede tardar la primera vez)...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(config.MODELO_ST)

    recomendador = Recomendador(store, model)
    print("Listo.")
    return recomendador


@app.route("/health", methods=["GET"])
def health():
    n = store.matrix.shape[0] if store is not None else 0
    return jsonify({"status": "ok", "n_eventos": n})


@app.route("/recomendar", methods=["POST"])
def recomendar():
    payload = request.get_json(silent=True) or {}

    id_user = payload.get("id_user")
    if id_user is None:
        return jsonify({"error": "Falta 'id_user'"}), 400

    filtros  = payload.get("filtros", {})           # dict de booleanos
    consulta = payload.get("consulta", "").strip()  # texto libre del buscador

    # Si no mandan consulta libre, generamos una mínima a partir de los filtros
    if not consulta:
        activos = [k for k, v in filtros.items() if v]
        consulta = "planes recomendados"
        if activos:
            consulta += " " + ", ".join(activos)

    try:
        resultado = recomendador.recomendar(
            user_id=id_user,
            consulta=consulta,
            filtros=filtros,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(resultado)


if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0", port=5000, debug=True)
