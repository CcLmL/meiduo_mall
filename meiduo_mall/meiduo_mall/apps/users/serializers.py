import re

from django.conf import settings
from django.core.mail import send_mail
from django_redis import get_redis_connection
from rest_framework import serializers

from celery_tasks.email.tasks import send_verify_email
from users.models import User


class EmailSerializer(serializers.ModelSerializer):
    """用户邮箱设置序列化器"""
    class Meta:
        model = User
        fields = ('id', 'email')

    def update(self, instance, validated_data):
        """
        设置user用户的邮箱并发送邮箱认证邮件
        instance: 创建序列化器时传递的对象
        validated_data:验证之后的数据
        """
        # 设置用户的邮箱
        email = validated_data['email']
        instance.email = email
        instance.save()

        # TODO: 发送邮箱验证邮件
        # 生成邮箱验证的链接地址:http://www.meiduo.site:8000/success_verify_email.html?user_id=<user.id>
        # 如果链接地址中直接存储用户的信息,可能会造成别人的恶意请求
        # 在生成邮箱验证的链接地址时,对用户的信息进行加密生成token,把加密之后的token放在链接地址中
        # http://www.meiduo.site:8000/success_verify_email.html?token=<token>
        # 所以对每个用户都需要创造一个token,即在数据模型类中添加一个方法
        verify_url = instance.generate_verify_url()

        # 发送邮件
        # subject = "美多商城邮箱验证"
        # html_message = '<p>尊敬的用户您好！</p>' \
        #                '<p>感谢您使用美多商城。</p>' \
        #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #                '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        #
        # send_mail(subject, '', settings.EMAIL_FROM, [email], html_message=html_message)

        # 发出发送邮件的任务消息
        send_verify_email.delay(email, verify_url)

        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """用户个人信息序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class CreateUserSerializer(serializers.ModelSerializer):  # 我们通过序列化器进行反序列化中的验证
    """
    创建用户的序列化器类
    """
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='是否同意协议', write_only=True)
    token = serializers.CharField(label='JWT Token', read_only=True)  # 只用于序列化

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'mobile', 'password2', 'sms_code', 'allow', 'token')  # 确定要进行序列化操作的字段

        extra_kwargs = {
            'password': {
                'write_only': True,  # 密码只用于进行校验,所以只需要反序列化
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许5-20个字符的密码',
                }
            },
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
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
        user = User.objects.create_user(**validated_data)  # 此时已经创建了对应的用户数据

        # 由服务器生成一个jwt token数据,包含登录用户身份信息(使用扩展生成jwt token数据)
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 调用api_setting中的方法
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 生成荷载
        payload = jwt_payload_handler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)

        # 给user对象增加属性token,保存服务器签发jwt token数据
        user.token = token  # 这里添加这个属性是为了给客户端返回token
        # (因为这个序列化器对应的模型类就是User,user又是User实例,所以给user.token添加值就是给序列化器中的token字段添加值)
        # (这里并不是将token数据存入数据库,只是给序列化器的token字段添加数据)
        # 返回注册用户
        return user
