import requests
import json
from datetime import datetime

# Загружаем данные матча
with open('tennis_match_sample.json', 'r') as f:
    match_data = json.load(f)

match_info = match_data['match_info']
token_id = match_info['markets'][0]['clobTokenIds'].strip('[]"').split('", "')[0]

print("Загружаем данные матча Djokovic vs Fritz")
print(f"Token ID: {token_id[:50]}...")
print()

# Получаем временные рамки из существующих данных
start_date = datetime.fromisoformat(match_info['startDate'].replace('Z', '+00:00'))
end_date = datetime.fromisoformat(match_info['endDate'].replace('Z', '+00:00'))
game_start = datetime.fromisoformat(match_info['startTime'].replace('Z', '+00:00'))

start_ts = int(start_date.timestamp())
end_ts = int(end_date.timestamp())
game_start_ts = int(game_start.timestamp())

print(f"Период: {start_date} - {end_date}")
print(f"Начало матча: {game_start}")
print()

# Запрашиваем с разной детализацией
result = {
    'match_info': {
        'title': match_info['title'],
        'start_date': start_date.isoformat(),
        'game_start': game_start.isoformat(),
        'end_date': end_date.isoformat(),
        'volume': match_info['volume']
    },
    'pregame_hourly': [],
    'ingame_10min': []
}

# 1. PRE-GAME: fidelity=60 (с начала до старта матча)
print("Запрашиваем pre-game данные (fidelity=60)...")
params = {
    "market": token_id,
    "startTs": start_ts,
    "endTs": game_start_ts,
    "fidelity": 60
}

response = requests.get("https://clob.polymarket.com/prices-history", params=params)
if response.status_code == 200:
    data = response.json()
    result['pregame_hourly'] = data.get('history', [])
    print(f"  ✅ Получено {len(result['pregame_hourly'])} точек (почасовые)")
else:
    print(f"  ❌ Ошибка: {response.status_code}")

# 2. IN-GAME: fidelity=10 (с старта матча до конца)
print("Запрашиваем in-game данные (fidelity=10)...")
params = {
    "market": token_id,
    "startTs": game_start_ts,
    "endTs": end_ts,
    "fidelity": 10
}

response = requests.get("https://clob.polymarket.com/prices-history", params=params)
if response.status_code == 200:
    data = response.json()
    result['ingame_10min'] = data.get('history', [])
    print(f"  ✅ Получено {len(result['ingame_10min'])} точек (каждые 10 минут)")
else:
    print(f"  ❌ Ошибка: {response.status_code}")

# Сохраняем
with open('djokovic_fritz_detailed.json', 'w') as f:
    json.dump(result, f, indent=2)

print()
print("✅ Данные сохранены в djokovic_fritz_detailed.json")
print()
print(f"Итого:")
print(f"  Pre-game (hourly): {len(result['pregame_hourly'])} точек")
print(f"  In-game (10 min): {len(result['ingame_10min'])} точек")
