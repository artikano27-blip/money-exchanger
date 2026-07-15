import json
import urllib.parse
import urllib.request


#guild_data = {"from": "RUB","to":"YEN","amount":"10"}
guild_data = {"baseCurrencyCode":"USD","targetCurrencyCode":"RUB","rate":"90"}
#guild_data = {"rate":"0.88"}
guild_json = urllib.parse.urlencode(guild_data)
data_bytes = guild_json.encode()
url = "http://localhost:8000/exchangeRates"

req = urllib.request.Request(
    url = url,
    method="POST",
    data=data_bytes,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
response = urllib.request.urlopen(req)
print(response.read().decode())