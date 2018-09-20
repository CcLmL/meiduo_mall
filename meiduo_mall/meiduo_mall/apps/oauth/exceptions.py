class QQAPIError(Exception):
    """自定义QQ接口调用异常类"""

    def __init__(self, message):
        self.message = message


if __name__ == '__main__':
    # 用于展示这个异常类的使用
    e = QQAPIError({'code': '1001', 'message': '错误信息'})
    print(e.message)
    print(type(e.message))
