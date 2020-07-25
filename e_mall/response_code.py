# -*- coding: utf-8 -*-
# @Time : 2020/5/8 18:37
# @Author : 司云中
# @File : response_code.py
# @Software: PyCharm

"""
自定义业务逻辑Code
"""

# 验证码验证成功
VERIFICATION_CODE_SUCCESS = 1

# 验证码验证失败
VERIFICATION_CODE_ERROR = 0

# 登录验证成功
LOGIN_VERIFICATION_SUCCESS = 11

# 登录验证失败
LOGIN_VERIFICATION_ERROR = -10

# 注册验证成功
REGISTER_VERIFICATION_SUCCESS = 21

# 注册验证失败
REGISTER_VERIFICATION_ERROR = -20

# 邮件验证成功
EMAIL_VERIFICATION_SUCCESS = 31

# 邮件验证失败
EMAIL_VERIFICATION_ERROR = -30

# 电话验证成功
PHONE_VERIFICATION_SUCCESS = 41

# 电话验证失败
PHONE_VERIFICATION_ERROR = -40

# 找回密码验证成功
FIND_PASSWORD_VERIFICATION_SUCCESS = 51

# 找回密码验证失败
FIND_PASSWORD_VERIFICATION_ERROR = -50

# 修改密码验证成功
MODIFY_PASSWORD_VERIFICATION_SUCCESS = 61

# 修改密码验证失败
MODIFY_PASSWORD_VERIFICATION_ERROR = -60

# 用户已经存在
USER_EXISTS = 7

# 用户不存在
USER_NOT_EXISTS = -7

# 邮箱已存在
EMAIL_EXISTS = 8

# 手机已存在
PHONE_EXISTS = 9

# 保存用户信息成功
USER_INFOR_CHANGE_SUCCESS = 4

# 保存用户信息成功

USER_INFOR_CHANGE_ERROR = -4

# 原始密码错误

USER_ORIGINAL_PASSWORD_ERROR = -6

# 绑定邮箱成功

BIND_EMAIL_SUCCESS = 12

# 绑定邮箱失败

BIND_EMAIL_ERROR = -12

# 绑定手机成功

BIND_PHONE_SUCCESS = 13

# 绑定手机失败

BIND_PHONE_ERROR = -13

# 认证真实用户成功
VERIFY_ID_CARD_SUCCESS = 15

# 认证真实用户失败
VERIFY_ID_CARD_ERROR = -15

# 密保设置成功
SECRET_SECURITY_SUCCESS = 17

# 图片实名认证成功
REAL_NAME_AUTHENTICATION_SUCCESS = 21

# 图片实名认证失败

REAL_NAME_AUTHENTICATION_ERROR = -21

# 添加收货地址成功
ADD_ADDRESS_SUCCESS = 35

# 添加收获地址失败

ADD_ADDRESS_ERROR = -35

# 修改收获地址成功

MODIFY_ADDRESS_SUCCESS = 36

# 修改收获地址失败

MODIFY_ADDRESS_ERROR = -36

# 修改默认地址成功

MODIFY_DEFAULT_SUCCESS = 42

# 修改默认地址失败

MODIFY_DEFAULT_ERROR = -42

# 删除地址成功

DELETE_ADDRESS_SUCCESS = 55

# 删除地址失败

DELETE_ADDRESS_ERROR = -55

# 修改地址成功

REVISE_ADDRESS_SUCCESS = 56

# 修改地址失败

REVISE_ADDRESS_ERROR = -56

# 删除订单成功

DELETE_ORDER_SUCCESS = 321

# 删除订单失败

DELETE_ORDER_ERROR = -321

# 删除收藏夹成功

DELETE_FAVORITES_SUCCESS = 108

# 删除收藏夹失败

DELETE_FAVORITES_ERROR = -108

# 添加收藏夹成功
ADD_FAVORITES_SUCCESS = 155

# 添加收藏夹失败
ADD_FAVORITES_ERROR = -155

# 添加足迹成功
ADD_FOOT_SUCCESS = 142

# 添加足迹失败
ADD_FOOT_ERROR = -142

# 删除足迹成功
DELETE_FOOT_SUCCESS = 123

# 删除足迹失败
DELETE_FOOT_ERROR = -123

# 删除购物车商品成功
DELETE_SHOP_CART_GOOD_SUCCESS = 678

# 删除购物车商品失败
DELETE_SHOP_CART_GOOD_ERROR = -678

# 修改购物车商品数量成功
EDIT_SHOP_CART_GOOD_SUCCESS = 679

# 修改购物车商品数量失败
EDIT_SHOP_CART_GOOD_ERROR = -679

# 创建临时订单失败

CREATE_ORDER_ERROR = -356

# 进入支付宝界面

CREATE_ORDER_SUCCESS = 356

# 添加进购物车成功

ADD_GOOD_INTO_SHOP_CART_SUCCESS = 786

# 添加进购物车失败

ADD_GOOD_INTO_SHOP_CART_ERROR = -786

# 添加进收藏夹失败

ADD_GOOD_INTO_FAVORITES_SUCCESS = 788

# 添加收藏夹失败

ADD_GOOD_INTO_FAVORITIES_ERROR = -788

# 服务器无响应
SERVER_ERROR = 500


class ResponseCode:
    result = {
        'code': '',
        'msg': '',
        'status': '',
        'data': '',
    }

    @property
    def verification_code_error(self):
        """验证码验证"""
        self.result.update(dict(code=VERIFICATION_CODE_ERROR, msg='code', status='error'))
        return self.result

    @property
    def login_success(self):
        """登录验证成功"""
        self.result.update(dict(code=LOGIN_VERIFICATION_SUCCESS, msg='login', status='success'))
        return self.result

    @property
    def login_error(self):
        """登录验证失败"""
        self.result.update(dict(code=LOGIN_VERIFICATION_ERROR, msg='login', status='error'))
        return self.result

    @property
    def register_success(self):
        """注册验证成功"""
        self.result.update(dict(code=REGISTER_VERIFICATION_SUCCESS, msg='register', status='success'))
        return self.result

    @property
    def register_error(self):
        """注册验证失败"""
        self.result.update(dict(code=REGISTER_VERIFICATION_ERROR, msg='register', status='error'))
        return self.result

    @property
    def email_verification_success(self):
        """邮件验证成功"""
        self.result.update(dict(code=EMAIL_VERIFICATION_SUCCESS, msg='email_verification', status='success'))
        return self.result

    @property
    def email_verification_error(self):
        """邮件验证失败"""
        self.result.update(dict(code=EMAIL_VERIFICATION_ERROR, msg='email_verification', status='error'))
        return self.result

    @property
    def phone_verification_success(self):
        """手机验证成功"""
        self.result.update(dict(code=PHONE_VERIFICATION_SUCCESS, msg='phone_verification', status='success'))
        return self.result

    @property
    def phone_verification_error(self):
        """手机验证失败"""
        self.result.update(dict(code=PHONE_VERIFICATION_SUCCESS, msg='phone_verification', status='error'))
        return self.result

    @property
    def find_password_verification_success(self):
        """找回密码验证成功"""
        self.result.update(dict(code=FIND_PASSWORD_VERIFICATION_SUCCESS, msg='find_password', status='success'))
        return self.result

    @property
    def find_password_verification_error(self):
        """找回密码验证成功"""
        self.result.update(dict(code=FIND_PASSWORD_VERIFICATION_ERROR, msg='find_password', status='error'))
        return self.result

    @property
    def modify_password_verification_success(self):
        """找回密码验证成功"""
        self.result.update(dict(code=MODIFY_PASSWORD_VERIFICATION_SUCCESS, msg='modify_password', status='success'))
        return self.result

    @property
    def modify_password_verification_error(self):
        """找回密码验证成功"""
        self.result.update(dict(code=MODIFY_PASSWORD_VERIFICATION_ERROR, msg='modify_password', status='error'))
        return self.result

    @property
    def user_existed(self):
        """用户已经存在"""
        self.result.update(dict(code=USER_EXISTS, msg='register', status='error'))
        return self.result

    @property
    def user_not_existed(self):
        """用户不存在"""
        self.result.update(dict(code=USER_NOT_EXISTS, msg='login', status='error'))
        return self.result

    @property
    def email_exist(self):
        """邮箱已存在"""
        self.result.update(dict(code=EMAIL_EXISTS, msg='email_verification', status='error'))
        return self.result

    @property
    def phone_exist(self):
        """手机已存在"""
        self.result.update(dict(code=PHONE_EXISTS, msg='phone_verification', status='error'))
        return self.result

    @property
    def server_error(self):
        """服务器无响应"""
        self.result.update(dict(code=SERVER_ERROR, msg='server_error', status='error'))
        return self.result

    @property
    def user_infor_change_success(self):
        """succeed to save user information"""
        self.result.update(dict(code=USER_INFOR_CHANGE_SUCCESS, msg='change_information', status='success'))
        return self.result

    @property
    def user_infor_change_error(self):
        """fail to save user information"""
        self.result.update(dict(code=USER_INFOR_CHANGE_ERROR, msg='change_information', status='error'))
        return self.result

    @property
    def user_original_password_error(self):
        """original password of user is error"""
        self.result.update(dict(code=USER_ORIGINAL_PASSWORD_ERROR, msg='change_password', status='error'))
        return self.result

    @property
    def bind_email_success(self):
        """original password of user is error"""
        self.result.update(dict(code=BIND_EMAIL_SUCCESS, msg='bind_email', status='suceess'))
        return self.result

    @property
    def bind_email_error(self):
        """original password of user is error"""
        self.result.update(dict(code=BIND_EMAIL_ERROR, msg='bind_email', status='error'))
        return self.result

    @property
    def bind_phone_success(self):
        """original password of user is error"""
        self.result.update(dict(code=BIND_PHONE_SUCCESS, msg='bind_phone', status='success'))
        return self.result

    @property
    def bind_phone_error(self):
        """original password of user is error"""
        self.result.update(dict(code=BIND_PHONE_ERROR, msg='bind_phone', status='error'))
        return self.result

    @property
    def verify_id_card_success(self):
        """certificate user authentication successfunlly"""
        self.result.update(dict(code=VERIFY_ID_CARD_SUCCESS, msg='verify', status='success'))
        return self.result

    @property
    def verify_id_card_error(self):
        """fail to authenticate User"""
        self.result.update(dict(code=VERIFY_ID_CARD_ERROR, msg='verify', status='error'))
        return self.result

    @property
    def secret_security_success(self):
        """set secret security successfully"""
        self.result.update(dict(code=SECRET_SECURITY_SUCCESS, msg='secret_security', status='success'))
        return self.result

    @property
    def real_name_authentication_success(self):
        """actual name authentication successfully"""
        self.result.update(dict(code=REAL_NAME_AUTHENTICATION_SUCCESS, msg='name_authentication', status='success'))
        return self.result

    @property
    def real_name_authentication_error(self):
        """fail to authenticate actual name"""
        self.result.update(dict(code=REAL_NAME_AUTHENTICATION_ERROR, msg='name_authentication', status='error'))
        return self.result

    @property
    def address_add_success(self):
        """add new address successfully"""
        self.result.update(dict(code=ADD_ADDRESS_SUCCESS, msg='add_address', stuats='success'))
        return self.result

    @property
    def address_add_error(self):
        """fail to add new address"""
        self.result.update(dict(code=ADD_ADDRESS_ERROR, msg='add_error', stuats='error'))
        return self.result

    @property
    def modify_address_success(self):
        """modify new address successfully"""
        self.result.update(dict(code=MODIFY_ADDRESS_SUCCESS, msg='modify_address', stuats='success'))
        return self.result

    @property
    def modify_address_error(self):
        """fail to modify address """
        self.result.update(dict(code=MODIFY_ADDRESS_ERROR, msg='modify_error', stuats='error'))
        return self.result

    @property
    def modify_default_success(self):
        """modify address successfully"""
        self.result.update(dict(code=MODIFY_DEFAULT_SUCCESS, msg='modify_success', stuats='success'))
        return self.result

    @property
    def modify_default_error(self):
        """fail to modify address """
        self.result.update(dict(code=MODIFY_DEFAULT_ERROR, msg='modify_error', stuats='error'))
        return self.result

    @property
    def delete_address_success(self):
        """delete address successfully"""
        self.result.update(dict(code=DELETE_ADDRESS_SUCCESS, msg='delete_error', stuats='success'))
        return self.result

    @property
    def delete_address_error(self):
        """fail to delete address """
        self.result.update(dict(code=DELETE_ADDRESS_ERROR, msg='delete_error', stuats='error'))
        return self.result

    @property
    def address_edit_success(self):
        """succeed to revise address"""
        self.result.update(dict(code=REVISE_ADDRESS_SUCCESS, msg='revise_success', status='success'))
        return self.result

    @property
    def address_edit_error(self):
        """fail to revise address"""
        self.result.update(dict(code=REVISE_ADDRESS_ERROR, msg='revise_error', status='error'))
        return self.result

    @property
    def delete_order_success(self):
        """succeed to delete order"""
        self.result.update(dict(code=DELETE_ORDER_SUCCESS, msg='delete_success', status='success'))
        return self.result

    @property
    def delete_order_error(self):
        """fail to delete order"""
        self.result.update(dict(code=DELETE_ORDER_ERROR, msg='delete_error', status='error'))
        return self.result

    @property
    def delete_favorites_success(self):
        """succeed to delete favorites"""
        self.result.update(dict(code=DELETE_FAVORITES_SUCCESS, msg='delete_success', status='success'))
        return self.result

    @property
    def delete_favorites_error(self):
        """fail to delete favorites"""
        self.result.update(dict(code=DELETE_FAVORITES_ERROR, msg='delete_error', status='error'))
        return self.result

    @property
    def add_favorites_success(self):
        """suuceed to add favorites"""
        self.result.update(dict(code=ADD_FAVORITES_SUCCESS, msg='add_success', status='error'))
        return self.result

    @property
    def add_favorites_error(self):
        """fail to add favorites"""
        self.result.update(dict(code=ADD_FAVORITES_ERROR, msg='add_error', status='error'))
        return self.result

    @property
    def delete_foot_success(self):
        """succeed to delete foot"""
        self.result.update(dict(code=DELETE_FOOT_SUCCESS, msg='delete_success', status='success'))
        return self.result

    @property
    def delete_foot_error(self):
        """fail to delete foot"""
        self.result.update(dict(code=DELETE_FOOT_ERROR, msg='delete_error', status='error'))
        return self.result

    @property
    def add_foot_success(self):
        """succeed to add foot"""
        self.result.update(dict(code=ADD_FOOT_SUCCESS, msg='add_success', status='success'))
        return self.result

    @property
    def add_foot_error(self):
        """fail to add foot"""
        self.result.update(dict(code=ADD_FOOT_ERROR, msg='add_error', status='error'))
        return self.result

    @property
    def delete_shop_cart_good_success(self):
        """succeed to delete good from shop cart"""
        self.result.update(dict(code=DELETE_SHOP_CART_GOOD_SUCCESS, msg='delete_success', status='success'))
        return self.result

    @property
    def delete_shop_cart_good_error(self):
        """fail to delete good from shop cart"""
        self.result.update(dict(code=DELETE_SHOP_CART_GOOD_ERROR, msg='delete_error', status='error'))
        return self.result

    @property
    def edit_shop_cart_good_success(self):
        """succeed to edit good from shop cart"""
        self.result.update(dict(code=EDIT_SHOP_CART_GOOD_SUCCESS, msg='edit_success', status='success'))
        return self.result

    @property
    def edit_shop_cart_good_error(self):
        """fail to edit good from shop cart"""
        self.result.update(dict(code=EDIT_SHOP_CART_GOOD_ERROR, msg='edit_error', status='error'))
        return self.result

    @property
    def create_order_success(self):
        """succeed to create new order"""
        self.result.update(dict(code=CREATE_ORDER_SUCCESS, msg='create_success', status='success'))
        return self.result

    @property
    def create_order_error(self):
        """fail to create new order or fail to use Ali payment"""
        self.result.update(dict(code=CREATE_ORDER_ERROR, msg='create_error', status='error'))
        return self.result

    @property
    def add_goods_into_shop_cart_success(self):
        """succeed to add goods into shop cart of current consumer"""
        self.result.update(dict(code=ADD_GOOD_INTO_SHOP_CART_SUCCESS, msg='add_success', status='success'))
        return self.result

    @property
    def add_goods_into_shop_cart_error(self):
        """fail to add goods into shop cart of current consumer"""
        self.result.update(dict(code=ADD_GOOD_INTO_SHOP_CART_ERROR, msg='add_error', status='error'))
        return self.result

    @property
    def add_goods_into_favorites_success(self):
        """succeed to add goods into shop cart of current consumer"""
        self.result.update(dict(code=ADD_GOOD_INTO_FAVORITES_SUCCESS, msg='add_success', status='success'))
        return self.result

    @property
    def add_goods_into_favorites_error(self):
        """fail to add goods into favorites of current consumer"""
        self.result.update(dict(code=ADD_GOOD_INTO_FAVORITIES_ERROR, msg='add_error', status='error'))
        return self.result


response_code = ResponseCode()
