from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'  # name属性必须和setting配置文件中的安装子应用中的apps前的名称一致
