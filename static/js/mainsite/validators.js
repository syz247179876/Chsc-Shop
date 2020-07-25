(function($) {
    var user = document.querySelector('#user');
    var phone = document.querySelector('#phone');
    var pwd = document.querySelector('#pwd');
    var btn1 = document.querySelector('.btn1');
    var load = document.querySelector('.load');
    var pawd = document.getElementById('pawd');
    var ruo = document.getElementById('ruo');
    var zo = document.getElementById('zo');
    var btn = document.getElementById('btn');
    var qiang = document.getElementById('qiang');
    var ps = document.querySelectorAll('p');
    var inputs = document.querySelectorAll('input');
    var form = document.querySelector('form');
    var email = document.querySelector('#email')
    var me;
    var ph;
    var ad;
    var pd;


    user.onblur = function() { //昵称正则表达式判断
        var reg = /^[\u2E80-\u9FFF,\w]{3,6}$/; //中文字符

        function z(re, e) { //封装函数判断传入的数据
            if (e.value != '') {
                if (re.test(e.value)) {
                    e.className = "r";
                    e.nextSibling.src = 'img/d.svg';
                    ps[e.index].style.color = "#04f014";
                    ps[e.index].innerHTML = "";
                    me = true;
                } else {
                    e.className = "f";
                    e.nextSibling.src = 'img/c.svg';
                    ps[e.index].style.color = "#f00";
                    ps[e.index].innerText = "3~6个中文字符或数字或字母组合";
                    me = false;
                }
            } else {
                e.className = "f";
                e.nextSibling.src = 'img/c.svg';
                ps[e.index].style.color = "#f00";
                ps[e.index].innerText = "不能为空";
                me = false;
            }
        }
        z(reg, this);
    }
    pawd.onblur = function() { //失去焦点判断密码
        if (this.value.length < 6 || this.value.length > 16) {
            this.nextSibling.src = 'img/c.svg';
            this.className = "f";
            ps[this.index].style.color = "#f00";
            ps[this.index].innerText = "密码长度应为6~16个字符";
            ruo.style.display = "none";
            zo.style.display = "none";
            qiang.style.display = "none";
            ad = false;
        } else {
            this.className = "r";
            this.nextSibling.src = "img/d.svg";
            ps[this.index].innerHTML = "密码强度：" + state;
            ps[this.index].style.color = "#090";
            ruo.style.display = "none";
            zo.style.display = "none";
            qiang.style.display = "none";
            ad = true;
        }
    }
    pwd.onblur = function() { //二次输入密码
        if (this.value != '') {
            if (this.value != pawd.value) {
                ps[this.index].innerText = "两次密码不一致";
                ps[this.index].style.color = "#f00";
                this.className = "f";
                this.nextSibling.src = 'img/c.svg';
                pd = false;
            } else {
                this.className = "r";
                this.nextSibling.src = 'img/d.svg';
                ps[this.index].style.color = "#04f014";
                ps[this.index].innerText = "";
                pd = true;
            }
        } else {
            this.className = "f";
            this.nextSibling.src = 'img/c.svg';
            ps[this.index].innerText = "不能为空";
            ps[this.index].style.color = "#f00";
            pd = false;
        }
    }
    phone.onblur = function() { //手机号判断
        alert('444');
        var reg = /^1[3|4|5|7|8]\d{9}$/;
        function z(re, e) { //封装函数判断传入的数据
            if (e.value != '') {
                if (re.test(e.value)) {
                    e.className = "r";
                    e.nextSibling.src = 'img/d.svg';
                    ps[e.index].style.color = "#04f014";
                    ps[e.index].innerHTML = "";
                    ph = true;
                } else {
                    e.className = "f";
                    e.nextSibling.src = 'img/c.svg';
                    ps[e.index].style.color = "#f00";
                    ps[e.index].innerText = "请填写正确的手机号码";
                    ph = false;
                }
            } else {
                e.className = "f";
                e.nextSibling.src = 'img/c.svg';
                ps[e.index].style.color = "#f00";
                ps[e.index].innerText = "不能为空";
                ph = false;
            }
        }
        z(reg, this);
    }

    for (var i = 0; i < 4; i++) { //获得焦点
        inputs[i].index = i;
        inputs[i].onfocus = function() {
            ps[this.index].style.color = "#000";
            this.nextSibling.src = '';
        }
    }
    var state = '弱'; //模拟密码强度判断
    pawd.onkeyup = function() {
        var regStr = /[a-zA-Z]/; //所有字母
        var regNum = /[0-9]/; //所有数字
        var sup = /\W/; //所有非字母数字
        if (this.value.length >= 6) {
            ruo.style.display = "inline-block";
            ruo.className = "ruo";
            ruo.innerHTML = "弱";
            zo.style.display = "inline-block";
            zo.className = "";
            qiang.style.display = "inline-block";
            qiang.className = "";
            state = "弱";
        }
        var sn = this.value.length >= 6 && regStr.test(this.value) && regNum.test(this.value);
        var sp = this.value.length >= 6 && regStr.test(this.value) && sup.test(this.value);
        var np = this.value.length >= 6 && regNum.test(this.value) && sup.test(this.value);
        if (sn || sp || np) {
            ruo.className = "zo";
            ruo.innerHTML = "&nbsp;";
            zo.className = "zo";
            zo.innerHTML = "中";
            state = "中";
        }
        if (this.value.length >= 6 && regStr.test(this.value) && regNum.test(this.value) && sup.test(this.value)) {
            ruo.className = "qiang";
            ruo.innerHTML = "&nbsp;";
            zo.className = "qiang";
            zo.innerHTML = "&nbsp;";
            qiang.className = "qiang";
            qiang.innerHTML = "强";
            state = "强";
        }
        if (this.value.length < 6) {
            ruo.style.display = "none";
            zo.style.display = "none";
            qiang.style.display = "none";
        }
    }
    btn.onclick = function() { //获取验证码
        if (ph) {
            var t = 59;
            btn.disabled = 'true';
            btn.style.opacity = '0.5';
            btn.style.cursor = "not-allowed";
            phone.readOnly = 'true';
            var y = setInterval(function() {
                btn.innerText = t + 'S';
                t--;
                if (t == -1) {
                    phone.readOnly = '';
                    btn.innerText = '获取验证码';
                    btn.disabled = '';
                    btn.style.opacity = '1';
                    btn.style.cursor = "pointer";
                    clearInterval(y);
                }
            },
            1000)
        } else {
            phone.className = "f";
            phone.nextSibling.src = 'img/c.svg';
            ps[phone.index].style.color = "#f00";
            ps[phone.index].innerText = "请填写正确的手机号码";
            return false;
        }
    }

    btn1.onclick = function() { //提交数据
        if (me) {
            if (ad) {
                if (pd) {
                    if (xbox.offsetWidth == bx + o) {
                        if (ph) {
                            btn1.style.transform = 'scale(0)';
                            btn1.nextElementSibling.style.transform = 'scale(1)';
                            form.style.transform = 'scaleY(0)';
                            setTimeout(function() {
                                load.style.display = "block";
                            },
                            1000)
                        } else {
                            phone.className = "f";
                            phone.nextSibling.src = 'img/c.svg';
                            ps[phone.index].style.color = "#f00";
                            ps[phone.index].innerText = "请填写正确的手机号码";
                        }
                    } else {
                        d.nextElementSibling.innerHTML = "验证失败";
                        d.nextElementSibling.style.color = "#f00";
                        d.style.border = '1px solid #f00';
                    }
                } else {
                    ps[pwd.index].innerText = "两次密码不一致";
                    ps[pwd.index].style.color = "#f00";
                    pwd.className = "f";
                    pwd.nextSibling.src = 'img/c.svg';
                }
            } else {
                pawd.nextSibling.src = 'img/c.svg';
                pawd.className = "f";
                ps[pawd.index].style.color = "#f00";
                ps[pawd.index].innerText = "密码长度应为6~16个字符";
            }
        } else {
            na.className = "f";
            na.nextSibling.src = 'img/c.svg';
            ps[na.index].style.color = "#f00";
            ps[na.index].innerText = "3~6个中文字符或数字或字母组合";
        }

    }
})