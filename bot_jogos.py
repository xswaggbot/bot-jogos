import requests
from datetime import datetime, timedelta, time
import pytz
from collections import defaultdict
import os

# Pega as variáveis de ambiente (dos Secrets)
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LIGAS_ID_NOME = {
    71: "Brasileirão Série A",
    72: "Brasileirão Série B",
    75: "Brasileirão Série C",
    128: "Liga Profesional Argentina",
    129: "Primera Nacional (Argentina B)",
    262: "Liga MX (México)",
    283: "Liga I (Romênia)",
    375: "Superliga (Romênia)",
    103: "Eliteserien (Noruega)",
    113: "Allsvenskan (Suécia)",
    94: "Primeira Liga (Portugal)",
    88: "Eredivisie (Holanda)",
    1032: "Prva HNL (Croácia)",
    62: "Scottish Premiership (Escócia)",
    138: "Czech First League (República Tcheca)",
    354: "SuperLiga (Sérvia)",
    237: "Swiss Super League (Suíça)",
    25: "Belgian Pro League (Bélgica)",
    61: "Nemzeti Bajnokság I (Hungria)",
    78: "Austrian Bundesliga (Áustria)",
    109: "Turkish Süper Lig (Turquia)",
    1364: "Danish Superliga (Dinamarca)",
    1290: "Ekstraklasa (Polônia)",
    244: "Veikkausliiga (Finlândia)",
    344: "Bolivian Primera División",
    268: "Copa Libertadores",
    289: "Copa Sudamericana",
    333: "LigaPro Serie A (Equador)",
    294: "Liga 1 (Peru)",
    297: "Torneo Betano (Argentina)",
    323: "USL Championship (EUA)",
    325: "MLS Next Pro (EUA)",
    253: "MLS (EUA)",
    326: "USL League One (EUA)",
    362: "Euro Feminina 2025",
}

def enviar_mensagem_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": texto, "parse_mode": "HTML"}
    r = requests.post(url, data=payload)
    print("Status Telegram:", r.status_code)
    if r.status_code != 200:
        print("Erro Telegram:", r.text)

def buscar_jogos_amanha_brasilia():
    tz_br = pytz.timezone("America/Sao_Paulo")
    amanha_date = (datetime.now(tz_br) + timedelta(days=1)).date()
    inicio_amanha_br = tz_br.localize(datetime.combine(amanha_date, time.min))
    fim_amanha_br = tz_br.localize(datetime.combine(amanha_date, time.max))
    inicio_utc = inicio_amanha_br.astimezone(pytz.utc)
    fim_utc = fim_amanha_br.astimezone(pytz.utc)
    datas_busca = sorted({inicio_utc.date(), fim_utc.date()})
    jogos_por_liga = defaultdict(list)

    for data_utc in datas_busca:
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {"x-apisports-key": API_FOOTBALL_KEY}
        params = {"date": data_utc.strftime("%Y-%m-%d")}
        resp = requests.get(url, headers=headers, params=params)

        if resp.status_code != 200:
            print("Erro na API:", resp.text)
            continue

        jogos = resp.json().get("response", [])
        for jogo in jogos:
            liga_id = jogo["league"]["id"]
            if liga_id not in LIGAS_ID_NOME:
                continue
            fixture_date_utc = datetime.strptime(jogo["fixture"]["date"], "%Y-%m-%dT%H:%M:%S%z")
            fixture_date_br = fixture_date_utc.astimezone(tz_br)
            if not (inicio_amanha_br <= fixture_date_br <= fim_amanha_br):
                continue
            hora = fixture_date_br.strftime("%H:%M")
            casa = jogo["teams"]["home"]["name"]
            fora = jogo["teams"]["away"]["name"]
            nome_liga = LIGAS_ID_NOME[liga_id]
            jogos_por_liga[nome_liga].append((fixture_date_br, f"• <b>{casa} x {fora}</b> - {hora}"))

    return jogos_por_liga

def montar_mensagem(jogos_liga):
    if not jogos_liga:
        return "🚫 <b>Nenhum jogo encontrado para amanhã nas ligas selecionadas.</b>"
    mensagem = "<b>📅 Jogos de amanhã:</b>\n\n"
    for liga in sorted(jogos_liga):
        mensagem += f"<b>🏆 {liga}</b>\n"
        for _, jogo in sorted(jogos_liga[liga], key=lambda x: x[0]):
            mensagem += jogo + "\n"
        mensagem += "\n"
    mensagem += "⚽ <i>Fique ligado!</i>"
    return mensagem

def main():
    jogos = buscar_jogos_amanha_brasilia()
    mensagem = montar_mensagem(jogos)
    enviar_mensagem_telegram(mensagem)

if __name__ == "__main__":
    main()
