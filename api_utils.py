import urllib.request
import urllib.error
import json
import time

BASE_URL = "https://arctic-shift.photon-reddit.com/api"
HEADERS = {'User-Agent': 'OSINT-Pipeline/1.0'}
IGNORED_AUTHORS = {'[deleted]', 'AutoModerator', 'automoderator', 'KafkaFPS', 'kafka-imperium', 'AskGrok'}

def make_request(url):
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                remaining = response.headers.get('X-RateLimit-Remaining')
                reset = response.headers.get('X-RateLimit-Reset')
                if remaining and reset and int(remaining) <= 2:
                    sleep_t = max(1, int(reset) - time.time() if int(reset) > 1e9 else int(reset))
                    time.sleep(sleep_t + 0.5)
                return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                reset = int(e.headers.get('X-RateLimit-Reset', 10))
                sleep_t = max(1, reset - time.time() if reset > 1e9 else reset)
                time.sleep(sleep_t + 0.5)
            elif e.code in [500, 502, 503, 504, 422]:
                time.sleep(2)
            else:
                return None
        except Exception:
            time.sleep(1)
    return None
