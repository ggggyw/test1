from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import User, Admin, Merchant
class CustomBackend(BaseBackend):
    # 一个自定义的后端，它可以从不同的模型中验证用户

    def authenticate(self, request, username=None, password=None, model=None):
        # 尝试找到一个具有给定用户名和模型的用户
        try:
            user = model.objects.get(u_name=username)
        except model.DoesNotExist:
            # 没有找到用户
            return None
        else:
            # 检查密码
            if check_password(password, user.u_psw):
                # 密码正确
                return user
            else:
                # 密码错误
                return None

    def get_user(self, user_id):
        # 尝试从任何模型中获取一个具有给定 user_id 的用户
        for model in [User, Admin, Merchant]:
            try:
                return model.objects.get(pk=user_id)
            except model.DoesNotExist:
                # 在这个模型中没有找到用户
                continue
        # 在任何模型中都没有找到用户
        return None
