import json

from common import util
from common.logger import log
from . import PushChannel


class QQBotClaw(PushChannel):
    def __init__(self, config):
        super().__init__(config)
        self.base_url = str(config.get("base_url") or "https://api.sgroup.qq.com")
        self.app_id = str(config.get("appid") or "")
        self.app_secret = str(config.get("appsecret") or "")
        self.openid_list = list(dict.fromkeys([
            str(openid).strip()
            for openid in config.get("openid_list", [])
            if str(openid).strip() != ""
        ]))
        if self.app_id == "" or self.app_secret == "" or len(self.openid_list) == 0:
            log.error(f"【推送_{self.name}】配置不完整，推送功能将无法正常使用")
            return

    def push(self, title, content, jump_url=None, pic_url=None, extend_data=None):
        headers = {
            "Content-Type": "application/json",
        }
        headers.update(self.get_headers())
        body = {
            "content": title + "\n\n" + content,
            "msg_type": 0,
        }
        if pic_url is not None:
            body["content"] += f"\n\n{pic_url}"

        for openid in self.openid_list:
            response = util.requests_post(
                self.base_url + f"/v2/users/{openid}/messages",
                self.name,
                headers=headers,
                data=json.dumps(body),
            )
            push_result = "成功" if util.check_response_is_ok(response) else "失败"
            log.info(f"【推送_{self.name}】【{openid}】{push_result}")

    def get_headers(self):
        response = util.requests_post("https://bots.qq.com/app/getAppAccessToken", f"{self.name}_获取accessToken", headers={
            "Content-Type": "application/json",
        }, data=json.dumps({
            "appId": self.app_id,
            "clientSecret": self.app_secret
        }))
        if util.check_response_is_ok(response):
            result = json.loads(str(response.content, "utf-8"))
            return {
                "Authorization": f"QQBot {result['access_token']}"
            }
        return {}
