import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

# -------------------- Funciones de MQTT --------------------
def on_publish(client, userdata, result):
    print("✅ El dato ha sido publicado")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.info(f"📩 Mensaje recibido: **{message_received}**")

# -------------------- Configuración del Broker --------------------
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("SimonSaenz")
client1.on_message = on_message

# -------------------- Diseño de la App --------------------
st.set_page_config(page_title="Control por Voz - Interfaces Multimodales", page_icon="🎙️", layout="centered")

st.title("🎛️ INTERFACES MULTIMODALES")
st.subheader("🎙️ Control de Dispositivos por Voz")

# Imagen ilustrativa
try:
    image = Image.open('voice_ctrl.jpg')
    st.image(image, width=250, caption="Control por Voz con MQTT")
except:
    st.warning("⚠️ No se encontró la imagen 'voice_ctrl.jpg'.")

st.markdown("---")
st.markdown("### 🗣️ Instrucciones")
st.write("Haz clic en el botón y habla para enviar comandos por voz al broker MQTT.")

# -------------------- Botón de Activación de Voz --------------------
stt_button = Button(label="🎤 Iniciar Reconocimiento", width=220)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

# -------------------- Procesar Resultado --------------------
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        command = result.get("GET_TEXT").strip()
        st.success(f"🎧 Texto reconocido: **{command}**")

        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": command})
        client1.publish("voice_simon", message)

        st.balloons()  # 🎈 Animación para hacerlo más visual

# -------------------- Crear Carpeta Temp --------------------
try:
    os.mkdir("temp")
except:
    pass
