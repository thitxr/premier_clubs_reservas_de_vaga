import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import requests

# Configurações
TOKEN_DISCORD = "MTM0MjUzMTM2MDU5NzczNzU2NA.GE2sS9.IBMxJSdJJE3cbjpCtC1uK_w9Tlqc9_9msXBM8g"
GUILD_ID = 1335363713452085391  # ID do servidor do Discord
ROLE_ID = 1336108080408297613  # ID do cargo para assinantes
MERCADO_PAGO_ACCESS_TOKEN = "TEST-7721487807171916-022112-9ff026627f9657a2f7aa7fdf4bb529c0-160304659"
WEBHOOK_SECRET = "7235e3f9bc77d825befd5911cba7135c944bfd903394db990f8c9890f38df47b"

# Inicializa bot do Discord
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Inicializa servidor Flask para Webhook
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Recebido Webhook:", data)  # Log para depuração
    
    if "type" in data and data["type"] == "payment":
        payment_id = data["data"]["id"]
        status, payer_email = verificar_pagamento(payment_id)
        
        if status == "approved":
            bot.loop.create_task(adicionar_role_no_discord(payer_email))
    
    return jsonify({"status": "ok"})

# Função para verificar pagamento
def verificar_pagamento(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data.get("status"), data["payer"].get("email")

# Função para adicionar role no Discord
async def adicionar_role_no_discord(email):
    guild = bot.get_guild(GUILD_ID)
    if guild:
        for member in guild.members:
            if email.lower() in member.display_name.lower() or email.lower() in member.name.lower():
                role = discord.utils.get(guild.roles, id=ROLE_ID)
                if role and role not in member.roles:
                    await member.add_roles(role)
                    print(f"Adicionado cargo a {member.name}")
                    break

# Iniciar bot
@bot.event
async def on_ready():
    print(f"{bot.user} está online!")

# Rodar Flask e Discord simultaneamente
import threading
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
    bot.run(TOKEN_DISCORD)

