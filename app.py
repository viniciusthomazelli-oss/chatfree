import os
import time
from flask import Flask, render_template, request, jsonify, url_for
from g4f.client import Client
from gtts import gTTS

app = Flask(__name__)
client = Client()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/perguntar", methods=["POST"])
def perguntar():
    dados = request.get_json()
    pergunta = dados.get("pergunta", "").strip()

    if not pergunta:
        return jsonify({"resposta": "Por favor, digite uma pergunta."})

    try:
        # 1. Obtém a resposta textual da IA gratuita
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": pergunta}]
        )
        resposta_final = response.choices[0].message.content

        # 2. Limpa formatações do markdown (como asteriscos) para o áudio não ler "asterisco"
        texto_limpo = resposta_final.replace("*", "").replace("#", "").replace("`", "")

        # 3. Gera o áudio via gTTS (Voz em Português do Brasil)
        tts = gTTS(text=texto_limpo, lang='pt', tld='com.br')

        audio_filename = 'resposta.mp3'
        audio_path = os.path.join('static', audio_filename)
        tts.save(audio_path)

        # O timestamp (?t=...) evita que o navegador use o áudio da pergunta anterior (cache)
        audio_url = url_for('static', filename=audio_filename) + f"?t={int(time.time())}"

        return jsonify({
            "resposta": resposta_final,
            "audio_url": audio_url
        })

    except Exception as e:
        return jsonify({
            "resposta": f"Não foi possível processar os dados na rede. (Erro: {str(e)})"
        })


if __name__ == "__main__":
    app.run(debug=True)