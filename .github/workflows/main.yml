name: Enviar jogos do dia

on:
  workflow_dispatch:  # permite rodar manualmente
  schedule:
    - cron: "0 3 * * *"  # 03:00 UTC = 00:00 BRT

jobs:
  send-message:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.x"

      - name: Instalar dependências
        run: pip install requests pytz

      - name: Executar script Python
        env:
          API_FOOTBALL_KEY: ${{ secrets.API_FOOTBALL_KEY }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python bot_jogos.py
