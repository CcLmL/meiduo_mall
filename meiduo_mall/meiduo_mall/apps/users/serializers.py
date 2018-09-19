import re

from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):  # 我们通过序列化器进行反序列化中的验证
    """
    创建用户的序列化器类
    """
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='是否同意协议', write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'mobile', 'passwords2', 'sms_code', 'allow')  # 确定要进行序列化操作的字段

        extra_kwargs = {
            'password': {
                'write_only': True,  # 密码只用于进行校验,所以只需要反序列化
                'min_length': 8,
                'max_length': 20,
                'error_message': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许5-20个字符的密码',
                }
            },
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_message': {
                    'min_length': '仅允许5-20个字符的密码',
                    'max_length': '仅允许5-20个字符的密码',
                }
            }
        }

    def validate_allow(self, value):
        """是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意协议')

        return value

    def validate_mobile(self, value):
        """
        手机格式,手机号是否已经注册
        """
        # 手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式不正确')

        # 手机号是否已经注册
        count = User.objects.filter(mobile=value).count()

        if count>0:
            raise serializers.ValidationError('手机号已经注册')

        return value

    def validate(self, attrs):
        """两次密码是否一致,短信验证码是否正确"""
        # 两次密码是否一致
        password = attrs['password']
        password2 = attrs['password2']

        if password != password2:
            raise serializers.ValidationError('两次密码不一致')

        # 获取手机号
        mobile = attrs['mobile']

        # 从redis中获取真实的短信验证码内容
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)  # bytes

        if not real_sms_code:
            raise serializers.ValidationError('短信验证码已过期')

        # 对比短信验证码
        sms_code = attrs['sms_code']  # str

        # bytes->str
        real_sms_code = real_sms_code.decode()
        if real_sms_code != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        return attrs

    def create(self, validated_data):
        """保存注册用户的信息"""
        # 清除无用的数据
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 保存注册用户的信息
        user = User.objects.create_user(**validated_data)

        # 返回注册用户
        return user
