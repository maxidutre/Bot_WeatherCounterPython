from typing import Text
import requests
import json

from telegram import  InlineKeyboardButton, InlineKeyboardMarkup, update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler

TOKEN = "2039709074:AAGmVM1KWSTZ2UyJInxXxtFAqu2gCQzqzPY"
OW_API = "6cb89b163832df06b4acab8f9545aa6e"
STATE_CIUDAD = 0
contador_MENSAJES = 0


# Al poner /start se ejecuta la función 'saludo'
# Se crea un menú abajo del mensaje de respuesta del bot
# Menú 2 opciones

def saludo(update, context):
    # Aumenta el contador (tomamos el comando /start como mensaje enviado)
    aumentarContador(update, context)
    # Lista con los botones del menú
    keyboard = [
        [
            InlineKeyboardButton("¡Quiero saber el Clima! ☀", callback_data= "respuestaClima"),
            InlineKeyboardButton("¡Quiero Contar! 🔢", callback_data= "respuestaContar"),
        ]
    ]   
    # Objeto que muestra las opciones (Le paso la lista con los botones)
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Mensaje respuesta del bot + Botones con opciones bajo el mensaje
    update.message.reply_text(
        text="¡Hola! ¿Que necesitas? ☺",
        reply_markup= reply_markup
    )
    
    # Output: ¡Hola! ¿Que necesitas?
    #         (¡Quiero saber el Clima! ☀)
    #         (¡Quiero Contar! 🔢)
    

# Función previa a que el usuario nos diga una ciudad
# Devuelve mensaje

def respuestaClima(update, context):
    query = update.callback_query
    query.answer()

    query.edit_message_text(
        text="Dime una ciudad 😋"
        )
    
    return STATE_CIUDAD
    # Output: Dime una ciudad 😋
    

# Función que aumenta el contador de mensajes en 1 

def aumentarContador(update, context):
    global contador_MENSAJES
    contador_MENSAJES += 1
    update

# Función respuesta de opción mensajes enviados

def respuestaContar(update, context):
    query = update.callback_query
    
    query.answer()
   
    query.edit_message_text(text=f"Me has enviado {contador_MENSAJES} mensajes")
    
    return ConversationHandler.END

def respuestaCiudad(update, context):
    # Respuesta del usuario sobre la Ciudad que quiere
    mensajeCiudad = update.message.text

    # Respuesta del bot
    mensajeBot = (datosClima(update, mensajeCiudad))

    # Retorna 'ConversationHandler.END', que le dice al
    # ConversationHandler que la conversación terminó.

    return ConversationHandler.END

# Función que descompone el json
# Obtiene los datos de éste
# Le envía al usuario mensaje con el clima de la ciudad

def datosClima(update, mensajeCiudad):
    try:
        respuesta_clima = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={mensajeCiudad}&units=metric&appid={OW_API}"
            )
        jsonText = respuesta_clima.text
        diccionarioDatos = dict(json.loads(jsonText))

        # Ciudad
        ciudad = diccionarioDatos.get("name")

        # Pais
        sys = diccionarioDatos.get("sys")   
        pais = sys.get("country")

        # Temperatura
        main = diccionarioDatos.get("main")
        temperatura = main.get("temp")

        # Humedad
        humedad = main.get("humidity")

        # Clima
        weather = diccionarioDatos.get("weather")
        diccionarioWeather = weather[0]
        clima = diccionarioWeather.get("description")

        mensajeClima = f"Ciudad: 🗺 {ciudad}\nPaís: 🌍 {pais}\nTemperatura: 🌡 {temperatura}°C\nHumedad: 💧 {humedad}%\nClima: ☁ {clima}"

        chat = update.message.chat
        chat.send_message(text=mensajeClima, timeout=None)
    except Exception:
        chat = update.message.chat
        chat.send_message(text="No existe esa Ciudad 😥", timeout=None)
    
    # Output: Ciudad: 🗺 (Nombre)
    #         País: 🌍 (País)
    #         Temperatura: 🌡 (Temperatura)°C
    #         Humedad: 💧 (Humedad)%
    #         Clima: ☁ (Clima)
    #
    # Error Output: No existe esa Ciudad 😥
    

def main() -> None:
    """Start the bot."""
    
    # Crea el Updater y le pasamos el token del bot
    updater = Updater(TOKEN)

    # Dispatcher para registrar handlers
    dispatcher = updater.dispatcher

    # Comando - Respuesta en Telegram
    dispatcher.add_handler(CommandHandler("start", saludo))
    dispatcher.add_handler(ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern='respuestaClima', callback=respuestaClima),
            CallbackQueryHandler(pattern='respuestaContar', callback=respuestaContar)

        ],
        states={
            STATE_CIUDAD: [MessageHandler(Filters.text, respuestaCiudad)]
        },
        fallbacks=[])
    )
    # Cuando el usuario manda mensajes que no son comandos
    # El bot aumenta el contador con la función aumentarContador
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, aumentarContador))

    # Inicia el bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
