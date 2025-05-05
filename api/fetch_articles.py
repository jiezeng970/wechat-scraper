from fastapi import FastAPI, Request
import urllib.request
import urllib.parse
import json
import time
import random
import ssl

app = FastAPI()
ssl._create_default_https_context = ssl._create_unverified_context

def fetch_articles(cookie, user_agent, token, fakeid_list, delay_range=(1, 2)):
    url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    headers = {
        "Cookie": cookie,
        "User-Agent": user_agent
    }

    results = []

    for fakeid in fakeid_list:
        params = {
            "token": token,
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1",
            "action": "list_ex",
            "begin": "0",
            "count": "5",
            "query": "",
            "fakeid": fakeid,
            "type": "9",
        }

      #  time.sleep(random.randint(*delay_range))

        try:
            full_url = url + "?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                content = response.read().decode()
                data = json.loads(content)
                links = [item["link"] for item in data.get("app_msg_list", [])]
                results.append({
                    "fakeid": fakeid,
                    "articles": links
                })
        except Exception as e:
            results.append({
                "fakeid": fakeid,
                "articles": [],
                "error": str(e)
            })

    return results

@app.post("/api/fetch_articles")
async def handle(request: Request):
    body = await request.json()
    cookie = body.get("cookie", "")
    user_agent = body.get("user_agent", "Mozilla/5.0")
    token = body.get("token", "")
    fakeid_list = body.get("fakeid_list", [])
    if not all([cookie, token, fakeid_list]):
        return {"error": "Missing cookie, token or fakeid_list"}
    return {"urls": fetch_articles(cookie, user_agent, token, fakeid_list)}
