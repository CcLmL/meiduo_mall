import base64
import os

from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OAuthQQUser
from oauth.utils import OAuthQQ
from users.models import User


class QQAuthUserSerializer(serializers.ModelSerializer):
    """保存绑定QQ登陆用户数据序列化器类"""
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    access_token = serializers.CharField(label='绑定操作凭据', write_only=True)
    token = serializers.CharField(label='JWT TOKEN数据', read_only=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$', write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'password', 'sms_code', 'access_token', 'token')

        extra_kwargs = {
            'username': {
                'read_only': True
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }

        }

    def validate(self, attrs):
        """access_token是否有效,短信验证码是否正确"""
        # access_token是否有效
        access_token = attrs['access_token']

        openid = OAuthQQ.check_save_user_token(access_token)

        if openid is None:
            raise serializers.ValidationError('无效的access_token')

        attrs['openid'] = openid

        # 短信验证码是否正确
        # 获取手机号
        mobile = attrs['mobile']

        # 从redis中获取真实的短信验证码内容
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)  # bytes

        if not real_sms_code:
            raise serializers.ValidationError('验证码已过期')

        # 对比短信验证码
        sms_code = attrs['sms_code']

        # bytes->str
        real_sms_code= real_sms_code.decode()
        if real_sms_code != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        # 如果'mobile'已注册,校验密码是否正确
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 未注册,不校验
            user = None
        else:
            # 已注册,校验密码
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError('用户密码错误')

        # 给attrs中添加user数据,以便在保存绑定QQ登陆用户的数据直接使用
        attrs['user'] = user

        return attrs

    def create(self, validated_data):
        """保存绑定QQ登陆用户的数据并签发jwt token"""
        # 获取mobile和password
        mobile = validated_data['mobile']
        password = validated_data['password']

        # 如果'mobile'没有注册过,需要创建新用户
        user = validated_data['user']

        if user is None:
            # 随机生成用户名
            username = base64.b64encode(os.urandom(10)).decode()
            user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 保存绑定QQ登陆用户的数据
        openid = validated_data['openid']

        OAuthQQUser.objects.create(
            user=user,
            openid=openid
        )

        # 签发jwt token
        # 由服务器生成一个jwt token数据,包含登陆用户身份信息
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 生成载荷
        payload = jwt_payload_handler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)

        # 给user对象增加属性token,保存服务器签发jwt token数据
        user.token = token

        # 返回user
        return user

