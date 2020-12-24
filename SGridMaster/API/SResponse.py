import json

from starlette.responses import JSONResponse


class SResponse:

    def __init__(self, error_code: str = None, body=None):
        self.error_code = {"success": {"success": True, "message": {"en": "Success", "jp": "成功"}},
                           "directory.empty": {"success": True, "message": {"en": "Directory Is Empty", "jp": "ディレクトリが空です"}},
                           "email.confirm.updated": {"success": True, "message": {"en": "Email Confirmation Key Updated", "jp": "メール確認キーが更新されました"}},
                           "account.invalid": {"message": {"en": "Account Is Invalid", "jp": "アカウントが無効です"}},
                           "application.invalid": {"message": {"en": "Application Is Invalid", "jp": "アプリケーションが無効です"}},
                           "account.exists": {"message": {"en": "Account Exists", "jp": "アカウントが存在します"}},
                           "internal.error": {"message": {"en": "Internal Error", "jp": "内部エラーが発生しました"}},
                           "account.email.unconfirmed": {"message": {"en": "Email Not Confirmed", "jp": "メールが確認されてません"}},
                           "token.invalid": {"message": {"en": "Token Is Invalid", "jp": "トークンが無効です"}},
                           "token.expired": {"message": {"en": "Token Expired", "jp": "トークンの期限切れです"}},
                           "params.lacking": {"message": {"en": "Lacking Params", "jp": "パラメーターが不足しています"}},
                           "email.invalid": {"message": {"en": "Email Is Invalid", "jp": "メールアドレスが無効です"}},
                           "password.invalid": {"message": {"en": "Password Invalid", "jp": "パスワードが無効です"}},
                           "email.unconfirmed": {"message": {"en": "Email Is Unconfirmed", "jp": "メールアドレスが認証されてません"}},
                           "web.error": {"message": {"en": "Web Connection Error", "jp": "ウェブ接続エラー"}},
                           "key.invalid": {"message": {"en": "Key Is Invalid", "jp": "キーが無効です"}},
                           "message.invalid": {"message": {"en": "Message Is Invalid", "jp": "メッセージが無効です"}},
                           "object.invalid": {"message": {"en": "Object Is Invalid", "jp": "オブジェクトが無効です"}},
                           "task.exists": {"message": {"en": "Task Already Exists", "jp": "タスクがすでに存在します"}},
                           "node.invalid": {"message": {"en": "Node Is Invalid", "jp": "ノードが無効です"}},
                           "node.not.initialized": {"message": {"en": "Node Not Initialized", "jp": "ノードが初期化されていません"}},
                           "access.limited": {"message": {"en": "Access Limited", "jp": "アクセスが制限されています"}},
                           "plan.invalid": {"message": {"en": "Plan Is Invalid", "jp": "プランが無効です"}},
                           "session.invalid": {"message": {"en": "Session Is Invalid", "jp": "セッションが無効です"}},
                           "game.invalid": {"message": {"en": "Game Is Invalid", "jp": "ゲームが無効です"}},
                           "instance.invalid": {"message": {"en": "Instance Is Invalid", "jp": "インスタンスが無効です"}},
                           "instance.locked": {"message": {"en": "Instance Is Locked", "jp": "インスタンスがロックされています"}},
                           "instance.booted": {"message": {"en": "Instance Is Already Booted", "jp": "インスタンスが既に起動されています"}},
                           "backup.failed": {"message": {"en": "Backup Has Failed", "jp": "バックアップが失敗しました"}},
                           "backup.key.invalid": {"message": {"en": "Backup Key Invalid", "jp": "バックアップキーが無効です"}},
                           "update.failed": {"message": {"en": "Update Failed", "jp": "アップデートが失敗しました"}},
                           "country.invalid": {"message": {"en": "Country Invalid", "jp": "国別コードが無効です"}},
                           "instance.non.trial": {"message": {"en": "Instance Is Not In Free Trial", "jp": "インスタンスは無料トライアル期間中ではありません"}},
                           "instance.non.subscription": {"message": {"en": "Instance Is Not In Subscription", "jp": "インスタンスはサブスクリプションではありません"}},
                           "instance.subscription": {"message": {"en": "Instance Is In Subscription", "jp": "インスタンスはサブスクリプションです"}},
                           "payment.subscription.failed": {"message": {"en": "Subscription Failed", "jp": "サブスクリプションが失敗しました"}},
                           "instance.running": {"message": {"en": "Instance Running", "jp": "インスタンスは既に起動しています"}},
                           "instance.stopped": {"message": {"en": "Instance Is Already Stopped", "jp": "インスタンスは既に止められています"}},
                           "account.unverified": {"message": {"en": "Account Is Unverified", "jp": "アカウントは認証されていません"}},
                           "months.invalid": {"message": {"en": "Month Is Invalid", "jp": "月が無効です"}},
                           "payment.months.over": {"message": {"en": "Month Is Over The Limit", "jp": "月が上限を越しています"}},
                           "freetrial.used": {"message": {"en": "Free Trial Is Used", "jp": "すでに無料トライアルを使用しています"}},
                           "freetrial.disabled": {"message": {"en": "Free Trial Is Disabled", "jp": "無料トライアルは無効です"}},
                           "freetrial.enabled": {"message": {"en": "Free Trial Is Enabled", "jp": "無料トライアルは有効です"}},
                           "refund.period.ended": {"message": {"en": "Refund Period Ended", "jp": "返金期間が終了しています"}},
                           "name.toolong": {"message": {"en": "Name Is Too Long", "jp": "名前が長すぎます"}},
                           "name.invalid": {"message": {"en": "Name Is Invalid", "jp": "名前が無効です"}},
                           "name.exists": {"message": {"en": "Name Exists", "jp": "名前がすでに存在します"}},
                           "port.error": {"message": {"en": "Port Error", "jp": "ポートエラーが発生しました"}},
                           "backup.exceeded": {"message": {"en": "Number Of Backups Exceeded", "jp": "バックアップの数が上限を越しました"}},
                           "backup.invalid": {"message": {"en": "Backup Is Invalid", "jp": "バックアップが無効です"}},
                           "version.invalid": {"message": {"en": "Version Is Invalid", "jp": "バージョンが無効です"}},
                           "path.invalid": {"message": {"en": "Path Is Invalid", "jp": "パスが無効です"}},
                           "task.invalid": {"message": {"en": "Task Invalid", "jp": "タスクが無効です"}},
                           "version.non.selectable": {"message": {"en": "Version Is Not Selectable", "jp": "バージョン選択が無効です"}},
                           "instance.type.invalid": {"message": {"en": "Instance Type Is Invalid", "jp": "インスタンス種類が無効です"}}
                           }

        self.data = {"code": "unknown", "success": False, "message": {"en": "Unknown Error", "jp": "不明なエラーが発生しました"}}
        if error_code in self.error_code:
            self.data = self.error_code[error_code]
            self.data["code"] = error_code
            if body is not None:
                self.data["body"] = body
            if "success" not in self.data:
                self.data["success"] = False
        if error_code is None:
            self.data = body

        self.default_country_code = "en"

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

    def message(self, country_code: str = "en"):
        if "message" in self.data:
            if country_code not in self.data:
                return self.data["message"][country_code]
            return self.data["message"]
        return None

    def body(self):
        if "body" in self.data:
            return self.data["body"]
        return None

    def serialize(self):
        return self.data
