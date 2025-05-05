from fastapi import FastAPI, Request
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

def fetch_articles(cookie, user_agent, token, fakeid_list):
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

        try:
            resp = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=4,
                verify=False
            )
            resp.raise_for_status()
            data = resp.json()
            links = [item["link"] for item in data.get("app_msg_list", [])]
            results.append({
                "fakeid": fakeid,
                "articles": links,
                "error": None
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
    user_agent = body.get("user_agent") or "Mozilla/5.0"
    token = body.get("token", "")
    fakeid_list = body.get("fakeid_list", [])

    if not all([cookie, token, fakeid_list]):
        return {"status": "error", "message": "Missing cookie, token or fakeid_list"}

    results = fetch_articles(cookie, user_agent, token, fakeid_list)
    return {
        "status": "ok",
        "count": len(results),
        "results": results
    }
