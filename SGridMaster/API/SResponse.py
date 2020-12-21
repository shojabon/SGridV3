import json

from starlette.responses import JSONResponse


class SResponse:

    def __init__(self, error_code: str = None, body=None):
        self.error_code = {
            "success": {"success": True},
            "directory.empty": {"success": True, "body": "Directory Is Empty"},
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
            "access.limited": {"body": "Access Limited"},
            "plan.invalid": {"body": "Plan Is Invalid"},
            "session.invalid": {"body": "Session Is Invalid"},
            "game.invalid": {"body": "Game Is Invalid"},
            "instance.invalid": {"body": "Instance Is Invalid"},
            "instance.locked": {"body": "Instance Is Locked"},
            "instance.booted": {"body": "Instance Is Already Booted"},
            "backup.failed": {"body": "Backup Has Failed"},
            "backup.key.invalid": {"body": "Backup Key Invalid"},
            "update.failed": {"body": "Update Failed"},
            "country.invalid": {"body": "Country Invalid"},
            "instance.non.trial": {"body": "Instance Is Not In Free Trial"},
            "instance.non.subscription": {"body": "Instance Is Not In Subscription"},
            "instance.subscription": {"body": "Instance Is In Subscription"},
            "payment.subscription.failed": {"body": "Subscription Failed"},
            "instance.running": {"body": "Instance Running"},
            "instance.stopped": {"body": "Instance Is Already Stopped"},
            "account.unverified": {"body": "Account Is Unverified"},
            "months.invalid": {"body": "Month Is Invalid"},
            "payment.months.over": {"body": "Month Is Over The Limit"},
            "freetrial.used": {"body": "Free Trial Is Used"},
            "freetrial.disabled": {"body": "Free Trial Is Disabled"},
            "freetrial.enabled": {"body": "Free Trial Is Enabled"},
            "refund.period.ended": {"body": "Refund Period Ended"},
            "name.toolong": {"body": "Name Is Too Long"},
            "name.invalid": {"body": "Name Is Invalid"},
            "name.exists": {"body": "Name Exists"},
            "port.error": {"body": "Port Error"},
            "backup.exceeded": {"body": "Number Of Backups Exceeded"},
            "backup.invalid": {"body": "Backup Is Invalid"},
            "version.invalid": {"body": "Version Is Invalid"},
            "path.invalid": {"body": "Path Is Invalid"},
            "task.invalid": {"body": "Task Invalid"},
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
