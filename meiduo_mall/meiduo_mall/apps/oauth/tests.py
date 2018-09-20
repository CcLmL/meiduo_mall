from django.test import TestCase
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
# Create your tests here.


if __name__ == '__main__':
    # urlopen:发送网络请求
    from urllib.request import urlopen

    # 请求地址
    req_url = 'http://api.meiduo.site:8000/mobiles/13155667788/count/'

    # 发送网络请求
    response = urlopen(req_url)

    # 获取响应数据
    req_data = response.read()  # bytes 注:响应数据为bytes类型
    print(req_data)


    # urlencode:将python字典转换为查询字符串
    from urllib.parse import urlencode

    # 定义字典
    req_dict = {
        'a': 1,
        'b': 2,
        'c': 3
    }

    res = urlencode(req_dict)
    print(res)


    # parse_qs:将查询字符串转换为python字典
    from urllib.parse import parse_qs

    # 定义查询字符串
    req_data1 = 'c=3&b=2&a=1&c=4'

    res1 = parse_qs(req_data1)  # 注:当key有多个相同时,对应的value是list


    # itsdangerous
    # 数据加密
    # serializer = TJWSSerializer(secret_key='加密密钥', expires_in='j解密有效时间')
    serializer = TJWSSerializer(secret_key='abc123', expires_in=3600)

    # 数据
    req_dict = {
        'openid': '1kkdk*KDLLS*09103003'
    }

    # 加密并返回加密之后数据
    res = serializer.dumps(req_dict)
    res = res.decode()
    print(res)


    # 数据解密
    req_data = 'eyJpYXQiOjE1MzczMjU3OTAsImV4cCI6MTUzNzMyOTM5MCwiYWxnIjoiSFMyNTYifQ.eyJvcGVuaWQiOiIxa2tkaypLRExMUyowOTEwMzAwMyJ9.qsyGzXn6rHGgKbNYYxplEvgW-mPQDLlu8ArKvqNA4Wg'

    serializer = TJWSSerializer(secret_key='abc123')

    try:
        res = serializer.loads(req_data)
    except Exception:
        print('解密失败')
    else:
        print(res)
