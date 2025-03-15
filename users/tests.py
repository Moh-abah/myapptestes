from rest_framework.test import APITestCase
from rest_framework import status

class UserTests(APITestCase):
    
    def setUp(self):
        # إعداد المستخدم قبل الاختبارات
        self.url_register = '/api/users/register/'
        self.url_login = '/api/users/login/'
        self.url_send_otp = '/api/users/send_otp/'
        self.url_verify_otp = '/api/users/verify_otp/'

        # تسجيل مستخدم جديد
        self.data = {
            "name": "John Doe",
            "phone": "123456789",
            "password": "password123",
            "confirm_password": "password123",
            "user_type": "customer"
        }
        self.client.post(self.url_register, self.data, format='json')

    def test_send_otp(self):
        data = {
            "phone": "123456789"
        }
        response = self.client.post(self.url_send_otp, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "OTP sent successfully.")

    def test_user_login(self):
        data = {
            "phone": "123456789",
            "password": "password123"
        }
        response = self.client.post(self.url_login, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_otp(self):
        data = {
            "phone": "123456789",
            "otp": "123456"  # تأكد من استخدام OTP صحيح
        }
        response = self.client.post(self.url_verify_otp, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "تم التحقق بنجاح.")
