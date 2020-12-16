import json

from starlette.responses import JSONResponse


class SResponse:

    def __init__(self, error_code: str = None, body=None):
        self.error_code = {
            "success": {"success": True},
            "email.confirm.updated": {"success": True, "body": "Email Confirmation Key Updated"},
            "account.invalid": {"body": "Account Is Invalid"},
            "application.invalid": {"body": "Application Is Invalid"},
            "account.exists": {"body": "Account Exists"},
            "internal.error": {"body": "Internal Error"},
            "account.email.unconfirmed": {"body": "Email Not Confirmed"},
            "token.invalid": {"body": "Token Is Invalid"},
            "token.expired": {"body": "Token Expired"},
            "params.lacking": {"body": "Lacking Params"},
            "email.invalid": {"body": "Email Is Invalid"},
            "password.invalid": {"body": "Password Invalid"},
            "email.unconfirmed": {"body": "Email Is Unconfirmed"},
            "web.error": {"body": "Web Connection Error"},
            "key.invalid": {"body": "Key Is Invalid"},
            "message.invalid": {"body": "Message Is Invalid"},
            "object.invalid": {"body": "Object Is Invalid"},
            "task.exists": {"body": "Task Already Exists"},
            "node.invalid": {"body": "Node Is Invalid"},
            "node.not.initialized": {"body": "Node Not Initialized"},
        }
        self.data = {"code": "unknown", "success": False}
        if error_code in self.error_code:
            self.data = self.error_code[error_code]
            self.data["code"] = error_code
            if body is not None:
                self.data["body"] = body
            if "success" not in self.data:
                self.data["success"] = False
        if error_code is None:
            self.data = body

    def __str__(self):
        return json.dumps(self.data, default=lambda o: '<not serializable>')

    def web(self):
        return JSONResponse(json.loads(json.dumps(self.data, default=lambda o: '<not serializable>')))

    def success(self):
        if "success" in self.data:
            return self.data["success"]
        return False

    def fail(self):
        if "success" in self.data:
            return not self.data["success"]
        return True

    def code(self):
        if "code" in self.data:
            return self.data["code"]
        return None

    def body(self):
        if "body" in self.data:
            return self.data["body"]
        return None

    def serialize(self):
        return self.data
