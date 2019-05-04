import os

PRODUCTION = "production"
DEVELOPMENT = "development"

COIN_TARGET = "LTC"
COIN_REFER = "USDT"

ENV = os.getenv("ENVIRONMENT", PRODUCTION)
DEBUG = False

BINANCE = {
  "key": os.environ.get( 'binance_key' ),
  "secret": os.environ.get( 'binance_secret' )
}



TELEGRAM = {
  "channel": "<CHANEL ID>",
  "bot": "<BOT KEY HERE>"
}

print("ENV = ", ENV)