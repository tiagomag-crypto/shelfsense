from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

TOTAL_PRODUTOS = 3
produtos_restantes = 3

alerta_ativo = False
aviso_ativo = False
alerta_resolvido = False

data_alerta = None
data_aviso = None

historico_alertas = []

@app.route("/limpar_alertas", methods=["POST"])
def limpar_alertas():
    global historico_alertas
    historico_alertas = []
    return jsonify({"ok": True})

@app.route("/")
def home():
    return render_template(
        "index.html",
        restantes=produtos_restantes,
        total=TOTAL_PRODUTOS,
        alerta_ativo=alerta_ativo,
        aviso_ativo=aviso_ativo,
        alerta_resolvido=alerta_resolvido,
        data_alerta=data_alerta,
        data_aviso=data_aviso,
        historico_alertas=historico_alertas
    )


@app.route("/estado")
def estado():
    return jsonify({
        "restantes": produtos_restantes,
        "total": TOTAL_PRODUTOS,
        "alerta_ativo": alerta_ativo,
        "aviso_ativo": aviso_ativo,
        "alerta_resolvido": alerta_resolvido,
        "data_alerta": data_alerta,
        "data_aviso": data_aviso,
        "historico_alertas": historico_alertas
    })


@app.post("/alerta")
def alerta():
    global produtos_restantes, alerta_ativo, aviso_ativo
    global alerta_resolvido, data_alerta, data_aviso

    data = request.get_json(force=True, silent=True) or {}
    nivel = data.get("nivel", TOTAL_PRODUTOS)

    try:
        nivel = int(nivel)
    except:
        nivel = TOTAL_PRODUTOS

    if nivel < 0:
        nivel = 0
    if nivel > TOTAL_PRODUTOS:
        nivel = TOTAL_PRODUTOS

    produtos_restantes = nivel

    # Quando fica com 2 produtos
    if produtos_restantes == 2 and not aviso_ativo:
        aviso_ativo = True
        alerta_ativo = False
        alerta_resolvido = False
        data_aviso = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        historico_alertas.insert(0, {
            "mensagem": "Os sumos estão a acabar",
            "data": data_aviso,
            "estado": "Aviso"
        })

    # Quando chega a 0 produtos
    if produtos_restantes == 0 and not alerta_ativo:
        alerta_ativo = True
        aviso_ativo = False
        alerta_resolvido = False
        data_alerta = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        historico_alertas.insert(0, {
            "mensagem": "Os sumos acabaram, é necessário repor",
            "data": data_alerta,
            "estado": "Alerta"
        })

    # Se voltar a haver mais de 2 produtos, limpa aviso/alerta ativos
    if produtos_restantes == 3:
        aviso_ativo = False
        alerta_ativo = False

    print("Produtos restantes:", produtos_restantes, flush=True)

    return jsonify({
        "ok": True,
        "restantes": produtos_restantes,
        "alerta_ativo": alerta_ativo,
        "aviso_ativo": aviso_ativo
    })


@app.post("/reposto")
def reposto():
    global alerta_ativo, aviso_ativo, alerta_resolvido, produtos_restantes

    alerta_ativo = False
    aviso_ativo = False
    alerta_resolvido = True
    produtos_restantes = TOTAL_PRODUTOS

    if historico_alertas:
        historico_alertas[0]["estado"] = "Resolvido"

    return jsonify({"ok": True})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)