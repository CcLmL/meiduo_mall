import re

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定jwt扩展登录视图响应数据函数
    """
    return {
        'user_id': user.id,
        'username': user.username,
        'token': token
    }


from django.contrib.auth.backends import ModelBackend


# 自定义Django认证后端类
def get_user_by_account(account):
    """
    根据用户名或手机号查询用户信息
    account:用户名或手机号
    """
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            # 根据手机号查询用户
            user = User.objects.get(mobile=account)
        else:
            # 根据用户名查询用户
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


# 添加自定义后端用于authorizate的认证
class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        进行用户登录验证时登录账户支持用户名和手机号
        username: 用户名或手机号
        password: 登录密码
        """
        # 根据用户名或手机号查询用户信息
        user = get_user_by_account(username)

        # 如果存在user,校验用户的密码
        if user and user.check_password(password):
            # 校验成功
            return user
