import os
import time
import uuid
from flask import Flask, render_template, request, jsonify, url_for
from g4f.client import Client
from gtts import gTTS

app = Flask(__name__)
client = Client()

# No Render, caminhos padrão funcionam muito bem
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


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
        # Volta a usar a IA 100% gratuita que não pede chaves
        response = client.chat.completions.create(
            model="gpt-4o",
            provider=g4f.Provider.DuckDuckGo, # Força o uso de um provedor específico que aceita requisições do Render
            messages=[{"role": "user", "content": pergunta}]
        )
        resposta_final = response.choices[0].message.content
        resposta_final = response.choices[0].message.content

        # Limpa o texto para o áudio
        texto_limpo = resposta_final.replace("*", "").replace("#", "").replace("`", "")

        # Gera o áudio dinâmico
        audio_filename = f"fala_{uuid.uuid4().hex}.mp3"
        audio_path = os.path.join(STATIC_DIR, audio_filename)

        tts = gTTS(text=texto_limpo, lang='pt', tld='com.br')
        tts.save(audio_path)

        audio_url = url_for('static', filename=audio_filename)

        return jsonify({
            "resposta": resposta_final,
            "audio_url": audio_url
        })

    except Exception as e:
        return jsonify({"resposta": f"Erro na rede CyberDuck: {str(e)}"})


if __name__ == "__main__":
    # O Render exige que o app use uma porta dinâmica definida pelo sistema
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
