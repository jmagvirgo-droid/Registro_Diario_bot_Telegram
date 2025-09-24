import os
import json
import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# El token ahora lo tomamos de una variable de entorno
TOKEN = os.getenv("TOKEN")

ARCHIVO = "registro.json"

# --- Funciones para manejar el guardado ---
def cargar_registro():
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def guardar_registro(registro):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=4)

# Cargamos actividades previas al iniciar
registro = cargar_registro()

# --- Funciones del bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hola, soy tu bot de productividad.\n\n"
        "Envíame tus actividades y las registraré por fecha.\n"
        "Usa /ver para consultar tu día.\n"
        "Usa /versemana para ver tus últimos 7 días."
    )

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fecha = datetime.date.today().isoformat()
    actividad = update.message.text.strip()

    if fecha not in registro:
        registro[fecha] = []
    registro[fecha].append(actividad)
    guardar_registro(registro)

    await update.message.reply_text(f"✅ Actividad registrada: {actividad}")

async def ver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fecha = datetime.date.today().isoformat()
    actividades = registro.get(fecha, [])
    if actividades:
        lista = "\n".join([f"- {a}" for a in actividades])
        await update.message.reply_text(f"📅 Actividades de hoy ({fecha}):\n{lista}")
    else:
        await update.message.reply_text("📭 Aún no has registrado actividades hoy.")

async def ver_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hoy = datetime.date.today()
    mensaje = "📊 Actividades de la última semana:\n\n"
    for i in range(7):
        dia = hoy - datetime.timedelta(days=i)
        fecha = dia.isoformat()
        actividades = registro.get(fecha, [])
        if actividades:
            lista = "\n".join([f"   - {a}" for a in actividades])
            mensaje += f"{fecha}:\n{lista}\n\n"
        else:
            mensaje += f"{fecha}: (sin registros)\n\n"
    await update.message.reply_text(mensaje)

# --- Iniciar bot ---
def main():
    if not TOKEN:
        print("❌ ERROR: No se encontró la variable de entorno TOKEN")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ver", ver))
    app.add_handler(CommandHandler("versemana", ver_semana))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar))

    print("🤖 Bot corriendo en la nube...")
    app.run_polling()

if __name__ == "__main__":
    main()
