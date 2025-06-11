from flask import Flask, request, jsonify, render_template, send_file
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['HISTORY_FILE'] = 'static/historico.txt'


CARACTERES = [chr(i) for i in range(32, 127)]
TOTAL_CARACTERES = len(CARACTERES)

def criptografar(texto, chave=3):
    resultado = ''
    for c in texto:
        if c in CARACTERES:
            i = CARACTERES.index(c)
            novo_i = (i + chave) % TOTAL_CARACTERES
            resultado += CARACTERES[novo_i]
        else:
            resultado += c 
    return resultado

def descriptografar(texto, chave=3):
    resultado = ''
    for c in texto:
        if c in CARACTERES:
            i = CARACTERES.index(c)
            novo_i = (i - chave) % TOTAL_CARACTERES
            resultado += CARACTERES[novo_i]
        else:
            resultado += c
    return resultado

def salvar_historico(entrada, saida, tipo):
    if not os.path.exists(app.config['HISTORY_FILE']):
        historico = []
    else:
        try:
            with open(app.config['HISTORY_FILE'], 'r', encoding='utf-8') as f:
                historico = json.load(f)
        except json.JSONDecodeError:
            historico = []

    historico.append({
        'tipo': tipo,
        'entrada': entrada,
        'resultado': saida
    })

    with open(app.config['HISTORY_FILE'], 'w', encoding='utf-8') as f:
        json.dump(historico[-10:], f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/criptografar', methods=['POST'])
def route_criptografar():
    texto = request.json['texto']
    try:
        resultado = criptografar(texto)
        salvar_historico(texto, resultado, "criptografar")
        return jsonify({'resultado': resultado})
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/descriptografar', methods=['POST'])
def route_descriptografar():
    texto = request.json['texto']
    try:
        resultado = descriptografar(texto)
        salvar_historico(texto, resultado, "descriptografar")
        return jsonify({'resultado': resultado})
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['arquivo']
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        with open(path, 'r', encoding='utf-8') as f:
            texto = f.read()
        return jsonify({'texto': texto})
    return jsonify({'erro': 'Nenhum arquivo recebido'}), 400

@app.route('/historico')
def historico():
    if os.path.exists(app.config['HISTORY_FILE']):
        if os.path.getsize(app.config['HISTORY_FILE']) == 0:
            return jsonify([])
        try:
            with open(app.config['HISTORY_FILE'], 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except json.JSONDecodeError:
            return jsonify([])
    return jsonify([])

@app.route('/exportar', methods=['POST'])
def exportar():
    caminho_resultado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado.txt')

    if os.path.exists(app.config['HISTORY_FILE']):
        with open(app.config['HISTORY_FILE'], 'r', encoding='utf-8') as f:
            historico_conteudo = f.read()
    else:
        historico_conteudo = ''

    with open(caminho_resultado, 'w', encoding='utf-8') as f:
        f.write("----- HISTÓRICO -----\n")
        f.write(historico_conteudo)

    return send_file(caminho_resultado, as_attachment=True, download_name='historico.txt', mimetype='text/plain')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    if os.path.exists(app.config['HISTORY_FILE']):
        with open(app.config['HISTORY_FILE'], 'w', encoding='utf-8') as f:
            f.write('')
    app.run(debug=True)