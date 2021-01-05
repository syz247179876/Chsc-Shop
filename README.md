# Eat-syz商城

本项目架构从0到1，从本地开发到部署到云服务器均单独完成，现开源出来，目的只为共享交流，锻炼自己的编码能力，不得参与任何商业用途！

本项目过程中参考的学习资料主要来源:官方文档，优质的技术博客。

在开发中，我遇到的问题也会写在我自己搭建的博客中，地址在文章最底下。

如果该项目对您的学习有帮助的话，可以考虑star下，谢谢~

我会定期review code 质量,进一步完善和优化

---

---
## **🥰个人技术博客🥰**

  👉👉👉  [博客地址](https://syzzjw.cn)
  
  qq:247179876(技术交流使用）

---
## **Version 1.0🐡（所在分支为master，包含了静态资源）：**

🐳基于后端框架Django和前端框架amazeui的前后段不分离开发。

🐉2020年4月2日---5月25日（已完成）


💃开发使用到的技术栈：Django+amzeui+layui+jquery+redis+celery+websocket+whoosh+mysql


🕺部署服务器用到的技术栈：nginx+uwsgi+channels


🤸一些第三方的服务：阿里云云服务器（学生机） + OSS + OCR身份识别 + 阿里云短信服务


🐠服务管理工具：supervisor

---

## **Version 2.0🐙（所在分支为version2.0，去除了静态资源)：**

🐋重构Version1.0，基于后端框架Django+接口框架Django-Restful-Framework框架（正在开发，目前已开发80%的功能），前端欲打算使用Vue框架（才刚动工）,实现前后段分离式开发。


🐲2020年6月5日-----目前（正在开发中）


💃开发使用到的技术栈：Django+DRF+Vue+Jquery+Redis+Celery+Rabbitmq+Elasticsearch+Websocket+Mysql+Fastdfs+JWT


🕺部署服务器用到的技术栈：nginx+uwsgi+channels


🤸一些第三方的服务：阿里云云服务器（学生机） + OSS + OCR身份识别 + 阿里云短信服务


🐠服务管理工具：supervisor

---
## **开发流程**

master:上线运行分支

develop:开发分支

hotfix:bug 处理分支

feature:成员共同开发分支（目前尚无该分支）

---
#### **🥳主要修改🥳：**

1. 传统前后端不分离===>基于restful风格接口开发  👀

2. whoosh搜索后端====>elasticsearch搜索后端👀

3. django自带的模板语言====>前端使用vue前端框架👀

4. 由原来的redis作为消息队列====>增加消息队列rabbitmq👀

5. django默认的Storage本地存储=====>分布式fastdfs存储

6. django默认的传统session认证=====>JWT算法认证

---
## **🥶目前已完成的功能🥶：**

目前已开发43个API

<!--

---
## **🤤接口文档🤤：**

### 一. 用户个人信息相关API
  
  ---
  #### 1. 绑定手机号（PUT）
  
  **Url：http://127.0.0.1:8000/consumer/email-or-phone-binding-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "phone": "13787833295",
  "code": "200",
  "is_existed": false,
  "way": "phone"
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |phone|code|is_existed|way|
  -:|:-:|:-:|:-
  |str|str|bool|str|
  
  ---
  #### 2. 修改个人用户名（PATCH）
  
  **Url http://127.0.0.1:8000/consumer/information-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "username": "司yz"
  }
  ```
  
  **请求数据类型**
  |username|
  -:|:-
  |str|
  
  **响应Json数据格式:**
  ```json
  {
  "code": 4,
  "msg": "修改信息成功",
  "status": "success",
  "data": ""
}
```

 ---
  #### 3. 获取用户个人基本信息（GET）
  
  **Url http://127.0.0.1:8000/consumer/information-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  无
  ```
  
  **响应Json数据格式:**
  ```json
  {
  "username": "syz247179876",
  "phone": "13787833295",
  "first_name": "张三",
  "head_image": "group1/M00/00/00/wKgAaV86kJ-ARxCAAA543lGjCZc7153661",
  "birthday": "1999-05-20",
  "sex": "男",
  "rank": "先锋会员",
  "safety": 60,
  "last_login": null
}
  ```
  
  **响应数据类型**
  |username|phone|first_name|head_image|birthday|sex|rank|safety|last_login|
  -:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-
  |str|str|str|str|str|str|str|int|str|
  
  ---
  #### 4. 修改用户密码（PATCH）
  
  **Url：http://127.0.0.1:8000/consumer/password-changes-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "new_password": "123456",
  "old_password": "654321",
  "code": "52351"
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
|new_password|old_password|code|
  -:|:-:|:-
  |str|str|str|
  
  
  ---
  #### 5. 实名认证（PUT）
  
  **Url：http://127.0.0.1:8000/consumer/verification-name-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "face": file,
  "back": file
}
  ```
  
  **响应Json数据格式:**
  ```json
  {
  "code": 15,
  "msg": "身份认证成功",
  "status": "success",
  "data": ""
}
  ```
  
  **请求数据类型**
  |face|back|
  -:|:-
  |file|file|
  
  
   ---
  #### 6. 修改头像（PUT）
  
  **Url：http://127.0.0.1:8000/consumer/shop-head-image-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "head_image": file
  }
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |head_image|
  -:|:-
  |file|
  
  ---
  ### 二  用户收货地址相关API
  
  ---
  #### 7. 添加收获地址（PUT）
  
  **Url：http://127.0.0.1:8000/consumer/address-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "recipients": "SYZ",
  "region": "XXXXXX地区XXXXX",
  "address_tags": "2",
  "phone": "13787833295"
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |recipients|region|address_tags|phone|
  -:|:-:|:-:|:-
  |str|str|str|str|
  
  
  
  ---
  #### 8. 查询收获地址（GET）
  
  **Url：
  http://127.0.0.1:8000/consumer/address-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  无
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  
  待填
  
  
  
  ---
  #### 9. 修改地址信息（PUT）
  
  **Url：http://127.0.0.1:8000/consumer/address-chsc-api/2/**
  
  
  **请求Json数据格式：**
  ```json
 {
  "recipients": "司司",
  "region": "度假村",
  "address_tags": "1",
  "phone": "13787833295",
  "default_address": true
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |recipients|region|address_tags|phone|default_address|
  -:|:-:|:-:|:-:|:-
  |str|str|str|str|bool|
  
  **响应数据类型**
  待填
  
  
  
  ---
  #### 10. 删除收获地址信息（PUT）
  
  **Url：  http://127.0.0.1:8000/consumer/address-chsc-api/6/**
  
  
  **请求Json数据格式：**
  ```json
  无
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **响应数据类型**
  待填
  
  ---
  ### 三  用户注册登陆API
  
  ---
  #### 11. 用户注册（POST）
  
  **Url：http://127.0.0.1:8000/consumer/register-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
 {
  "password": "1234567",
  "phone": "13787833295",
  "code": "PJHAV5",
  "way": "phone"
}
  ```
  
  **响应Json数据格式:**
  ```json
 待填
  ```
  
  **请求数据类型**
  |password|phone|code|way|
  -:|:-:|:-:|:-
  |str|str|str|str|
  
  
  
  
  ---
  #### 12. 用户登录（PUT）
  
  **Url：  http://127.0.0.1:8000/consumer/login-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "username": "13787833290",
  "password": "1234567",
  "previous_page": "?next=/chsc-syz-247179876-docs/",
  "is_remember": true,
  "way": "2"
}
  ```
  
  **响应Json数据格式:**
  ```json
   {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjozLCJ1c2VybmFtZSI6ImNoY2gyNDcxNzk4NzZAcXEuY29tIiwiZXhwIjoxNTk3NzUxNTE0LCJlbWFpbCI6IjI0NzE3OTg3NkBxcS5jb20iLCJvcmlnX2lhdCI6MTU5NzY2NTExNH0.x2YToUZ1VssJ9PGVLhlcNJVnFxSCsBi-E9N4NATf31g",
  "previous_page": "/chsc-syz-247179876-docs/"
}
  ```
  
  **请求数据类型**
  |username|password|previous_page|is_remember|way|
  -:|:-:|:-:|:-:|:-
  |str|str|str|bool|str|
  
  **响应数据类型**
  
  |token|previous_page|
  -:|:-
  |str|str|
  
  ---
  ### **四  足迹相关API** 
  
  ---
  #### 13. 删除单个足迹（DELETE）
  
  **Url：http://127.0.0.1:8000/consumer/foot-chsc-api/1/**
  
  
  **请求Json数据格式：**
  ```json
  无
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **响应数据类型**
  
  
  
  
  
  ---
  #### 14. 删除全部足迹（DELTE）
  
  **Url：http://127.0.0.1:8000/consumer/foot-chsc-api/destroy_all/**
  
  
  **请求Json数据格式：**
  ```json
  无
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  
  
  
  ---
  #### 15. 添加足迹（POST）
  
  **Url：http://127.0.0.1:8000/consumer/foot-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "pk":231231
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |pk|
  -:|:-
  |int|
  
  
  ---
  #### 16. 查看用户足迹（GET）
  
  **Url：http://127.0.0.1:8000/consumer/foot-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  无
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**

  ---
  ### **五  收藏模块API**
  

  #### 17. 添加收藏（PUT）
  
  **Url：http://127.0.0.1:8000/consumer/favorites-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
    "commodity_pk":26537
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
   |pk|
   -:|:-
   |int|
  
  
  
  
  ---
  #### 18. 删除全部收藏商品（DEL）
  
  **Url：http://127.0.0.1:8000/consumer/favorites-chsc-api/destroy_all/**
  
  
  **请求Json数据格式：**
  ```json
  无
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **响应数据类型**
  
  

  
  ---
  #### 19. 删除单个收藏商品（PUT）
  
  **Url：http://127.0.0.1:8000/consumer/favorites-chsc-api/132/**
  
  
  **请求Json数据格式：**
  ```json
  无
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **响应数据类型**
  
  
  
  ---
  #### 20. 查看收藏的商品（PUT）
  
  **Url：http://127.0.0.1:8000/consumer/favorites-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  无
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **响应数据类型**


  ### **六  购物车模块API**
  
  ---
  #### 21. 添加商品到购物车 （POST）
  
  **Url：http://127.0.0.1:8000/consumer/trolley-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
    "provision":{
        "pk":26454,
        "count":222,
        "label":{
            "pk":2,
            "content":"湛蓝色-大号"
        }
    }
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |pk|count|content|
  -:|:-:|:-:
  |int|int|str|
  
  
  
  
  ---
  #### 22. 单删购物车商品（PUT）
  
  **Url：http://127.0.0.1:8000/consumer/trolley-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
无
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **响应数据类型**
  
  
  
  ---
  #### 23. 浏览购物车（GET）
  
  **Url：http://127.0.0.1:8000/consumer/trolley-chsc-api**
  
  
  **请求Json数据格式：**
  ```json
无
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **响应数据类型**
  
  ---
  #### 24. ES搜索商品（GET）
  
  **Url：http://127.0.0.1:8000/shop/shop-chsc-search?page=1&text=牛肉干**
  
  
  **请求Params：**
  ```
  page=1
  text="牛肉干"
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **响应数据类型**
  待填

  
  ---
  ### **八  商家模块API**
  

  #### 25. 商家注册（POST）
  
  **Url：http://127.0.0.1:8000/shopper/shopper-operation-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "username":"SYZ",
  "phone": "13787833295",
  "sex": "m",
  "is_vip": true,
  "birthday": "2020-08-20",
  "sell_category":"衣服",
  "email":"123456789@126.com",
  "code":"3AS412"
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |username|phone|sex|is_vip|birthday|sell_category|email|code|
  -:|:-:|:-:|:-:|:-:|:-:|:-:|:-
  |str|str|str|bool|str|str|str|str|
  
  
  ---
  ### **九  验证码发送模块API**


  #### 26. 发送验证码（邮箱或手机）（POST）
  
  **Url：http://127.0.0.1:8000/consumer/email-or-phone-binding-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "phone": "13787833295",
  "way": "phone"
}
  ```
  
  **响应Json数据格式:**
  ```json
  {
  "code": 7,
  "msg": "用户已经存在",
  "status": "error",
  "data": ""
 }
  ```
  
  **请求数据类型**
  |phone|way|
  -:|:-:|
  |str|str|
  
  
  
  ---
  #### 27. 发送验证码（绑定邮箱或手机）（POST）
  
  **Url：http://127.0.0.1:8000/consumer/verification-code-chsc-bind-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "email": "247179876@qq.com",
  "way": "email"
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |email|way|
  -:|:-:
  |str|str|
  

  
  ---
  #### 28. 发送验证码（修改密码）（POST）
  
  **Url：http://127.0.0.1:8000/consumer/verification-code-chsc-modify-pwd-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "phone": "1378783322131231"
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |phone|
  -:|
  |str|
  
  
  
  
  ---
  #### 29. 发送验证码（商家注册）（POST）
  
  **Url：http://127.0.0.1:8000/shopper/verification-code-shopper-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
  "phone":"13235123112"
   "way":"phone" 
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |phone|way|
  -:|:-:
  |str|str|
  
  ---
  ### **十 订单模块API**

  #### 30. 生成初始订单（POST）
  
  **Url：  http://127.0.0.1:8000/order/order-create-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
 {
    "commodity_dict":{
        "15":3,
        "51":31,
        "155":255
    },
    "payment":"4"
}
  ```
  
  **响应Json数据格式:**
  ```json
  待填
  ```
  
  **请求数据类型**
  |commodity_dict|payment|
  -:|:-:|
  |json|str|
  
  
  
  
  ---
  #### 31. 群删订单（DELETE）
  
  **Url：http://127.0.0.1:8000/order/order-chsc-api/destroy_multiple/**
  
  **请求Json数据格式：**
  ```json
  {
    "list_pk":[
        "55","5"
    ]
}
  ```
  
  **响应Json数据格式:**
  ```json
  代填
  ```
  

  
  ---
  #### 32. 单删订单（DELETE）
  
  **Url：http://127.0.0.1:8000/order/order-chsc-api/22/**
  
  
  **响应Json数据格式:**
  ```json
  {
    "list_pk":[
        "55","5"
    ]
}
  ```
  
  **响应Json数据格式:**
  ```json
  代填
  ```
  
  
  ---
  #### 33. 获取某用户某个订单详细信息（GET）
  
  **Url：http://127.0.0.1:8000/order/order-chsc-api/32**
  
  
  **响应Json数据格式:**
  ```json
  代填
  ```
  
  ---
  #### 34. 获取某用户某状态的全部订单（GET）
  
  **Url：http://127.0.0.1:8000/order/order-get-chsc-api/1?page=102&status=5**
  
  
  **请求Params数据格式:**
  ```
  page="102"
  status="5"
  ```
  
  **响应Json数据格式:**
  ```json
  {
  "links": {
    "next": null,
    "previous": "http://127.0.0.1:8000/order/order-get-chsc-api/1?age=5&page=101"
  },
  "count": 1020,
  "data": [
    {
      "orderId": "208112031923239690",
      "trade_number": null,
      "total_price": "0.00",
      "commodity_total_counts": 1,
      "generate_time": "2020-08-11T20:19:23.241858",
      "status": "代付款",
      "order_details": []
    },
    {
      "orderId": "208112031923291509",
      "trade_number": null,
      "total_price": "0.00",
      "commodity_total_counts": 1,
      "generate_time": "2020-08-11T20:19:23.293626",
      "status": "代付款",
      "order_details": []
    },
    {
      "orderId": "208112031923425540",
      "trade_number": null,
      "total_price": "0.00",
      "commodity_total_counts": 1,
      "generate_time": "2020-08-11T20:19:23.436737",
      "status": "代付款",
      "order_details": []
    }
   ]
  }
    
  ```
  
  ### **十一  评论模块API**
  
  ---
  #### 35. 删除用户的评论（DELETE）
  
  **Url：http://127.0.0.1:8000/remark/remark-chsc-api/1/**
  
  
  **响应Json数据格式:**
  ```json
  代填
  ```
  
   ---
  #### 36. 用户评论购买的商品（PUT）
  
  **Url：http://127.0.0.1:8000/remark/remark-chsc-api/2222/add_remark/**
  
  **请求Json数据格式:**
  ```json
  {
  "grade": "1",
  "reward_content": "厉害了我的哥！",
  "is_add":true,
  "is_update":false
}
  ```
  
  
  **响应Json数据格式:**
  ```json
  代填
  ```
  
  **请求数据类型**
   |grade|reward_content|is_add|is_update|
  -:|:-:|
  |str|str|bool|bool
  
  
   ---
  #### 37. 评论点赞/差评（PATCH）
  
  **Url：http://127.0.0.1:8000/remark/remark-action-chsc-api/remark_click/**
  
  **请求Json数据格式**
  ```json
  {
    "pk":22222,
    "p_or_n":true,
    "status":true
}
```
  
  **响应Json数据格式:**
  ```json
  代填
  ```
  
  
   ---
  #### 38. 记录每日用户登录次数API(限流)（GET）
  
  **Url：http://127.0.0.1:8000/consumer/record-browser-login/**
  
  
  **响应Json数据格式:**
  ```json
  代填
  ```
  
   ---
  #### 39. 记录所有用户浏览次数API（GET）
  
  **Url：http://127.0.0.1:8000/consumer/record-browser/**
  
  
  **响应Json数据格式:**
  ```json
  代填
  ```
  
  ---
  ### **十二  优惠卷模块API**
  
  #### 40.显示用户优惠卷
  
  
  **Url：http://127.0.0.1:8000/voucher/voucher-chsc-api/**
  
  
  **响应Json数据格式:**
  ```json
  代填
  ```
  
   ---
  #### 41. 领优惠卷（POST）
  
  **Url：http://127.0.0.1:8000/voucher/voucher-chsc-api/**
  
  
  **请求Json数据格式：**
  ```json
  {
    "pk":2
}
  ```
  
  **响应Json数据格式:**
  ```json
  代填
  ```


---

未完待续....
  
-->
  
---
## **POSTMAN文档接口地址**

[PostMan](https://documenter.getpostman.com/view/10963682/T1LFnpyV3)

---
## **SwaggerUI接口地址**

[Swagger](https://127.0.0.1:8000/chsc-api-doc/
