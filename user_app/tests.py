from django.test import TestCase, Client

# Create your tests here.
from django.test import TestCase


class SendRegisterCodeTest(TestCase):
    """发送验证码"""

    def test_register_code(self):
        client = Client()
        data = {
            "phone": "15886378570",
            "way": "phone"
        }
        response = client.post('/consumer/verification-code-chsc-register-api/', data=data)
        self.assertEqual(response.status_code, 200) # 测试是否正确
        return response.data


class UserContest(TestCase):
    """测试User模块"""

    def test_register(self):
        client = Client()  # 测试客户端
        response = client.get('/register-chsc-api')


        



