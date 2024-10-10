import streamlit as st
import zmq

# Crea il contesto ZeroMQ
context = zmq.Context()

# Crea un socket di tipo REQ per inviare comandi al server
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5556")

st.title("Controllo del Motorino con Arduino")

# Slider per controllare la velocità del motore
speed = st.slider("Velocità del motore", min_value=4, max_value=9, value=5)

# Pulsanti per controllare la direzione
if st.button("Accendi Motore"):
    socket.send_string("on")
    response = socket.recv_string()
    st.write(response)

if st.button("Spegni Motore"):
    socket.send_string("off")
    response = socket.recv_string()
    st.write(response)

if st.button("Gira a Sinistra"):
    socket.send_string("left")
    response = socket.recv_string()
    st.write(response)

if st.button("Gira a Destra"):
    socket.send_string("right")
    response = socket.recv_string()
    st.write(response)

# Invio del valore di velocità quando lo slider viene cambiato
socket.send_string(str(speed))
response = socket.recv_string()
st.write(response)
