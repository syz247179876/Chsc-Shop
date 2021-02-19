from django.test import TestCase, Client


# Create your tests here.


class VerificationTestCase(TestCase):
    client = Client()

    def test_send_phone_code(self):
        """测试邮箱验证码发送"""
        path = '/universal/chsc/apis/verification-code/register'
        data = {
            'email':'247179876@qq.com',
            'way':'email'
        }
        response = self.client.post(path=path, data=data)
        self.assertEqual(response.status_code, 200)

    def test_send_email_code(self):
        """测试手机验证码发送"""
        path = '/universal/chsc/apis/verification-code/register'
        data = {
            'phone': '13787833290',
            'way':'phone'
        }
        response = self.client.post(path=path, data=data)
        self.assertEqual(response.status_code, 200)
        

