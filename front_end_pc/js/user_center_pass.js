var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: sessionStorage.username || localStorage.username,
		password: '',
        new_password: '',
		new_password2: '',
    },
    mounted: function(){
        // 判断用户的登录状态
        if (this.user_id && this.token) {
            axios.get(this.host + '/user/', {
                    // 向后端传递JWT token的方法
                    headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json',
                })
                .then(response => {
                    // 加载用户数据
                    this.user_id = response.data.id;
                    this.username = response.data.username;
                    this.mobile = response.data.mobile;
                    this.email = response.data.email;
                    this.email_active = response.data.email_active;

                })
                .catch(error => {
                    if (error.response.status==401 || error.response.status==403) {
                        location.href = '/login.html?next=/user_center_info.html';
                    }
                });
        } else {
            location.href = '/login.html?next=/user_center_info.html';
        }
    },
    methods: {
        check_opwd: function () {
            var len = this.password.length;
            console.log(len);
            if (len < 5 || len > 20) {
                alert("密码长度8-20位");
                return;
            }
        },
        check_pwd: function (){
			var len = this.new_password.length;
			if(len<5||len>20){
				alert("密码长度8-20位");
				return;
			}
		},
		check_cpwd: function (){
			if(this.new_password!=this.new_password2) {
				alert("两次密码不一致");
				return
			}
		},
        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 注册
        change_password: function(){
            this.check_opwd();
            this.check_pwd();
            this.check_cpwd();
            axios.put(this.host + '/user/password/', {
                    password: this.password,
                    new_password: this.new_password,
                    new_password2: this.new_password2,
                }, {
                 headers: {
                        'Authorization': 'JWT ' + this.token
                    },
                    responseType: 'json'
                })
                .then(response => {
                    alert("密码修改成功");
                })
                .catch(error=> {
                    if (error.response.status == 400) {
                        alert("Not Found");
                    } else {
                        console.log(error.response.data);
                    }
                })
            }
        },

    })