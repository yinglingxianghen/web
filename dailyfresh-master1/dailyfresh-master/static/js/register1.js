$(function () {

    var error_name = false;
    var error_password = false;
    var error_check_password = false;
    var error_email = false;
    var error_check = false;


    $('#user_name').blur(function () {
        // console.log(1)
        // check_has_user();
        check_user_name();
        if (error_name == false) {
            check_user_name_exist2(true)
        }
    });

    $('#pwd').blur(function () {
        check_pwd();
    });

    $('#cpwd').blur(function () {
        check_cpwd();
    });

    $('#email').blur(function () {
        check_email();
    });

    $('#allow').click(function () {
        if ($(this).is(':checked')) {
            error_check = false;
            $(this).siblings('span').hide();
        }
        else {
            error_check = true;
            $(this).siblings('span').html('请勾选同意');
            $(this).siblings('span').show();
        }
    });

    // function check_has_user() {
    //     // 获取用户名
    //     username = $('#user_name').val()
    //     // $('#user_name').next().html('用户名已经存在，请重新输入')
    //     // $('#user_name').next().show();
    //     // alert(username)
    //     // 发起ajax请求校验，把用户名传过去
    //
    //     // $.get("/user/has_username/?username="+ username, function (data) {
    //     $.get("/user/has_username/" + username, function (data) {
    //         // alert('data'+data.res)
    //         // {'res':0}用户名不存在
    //         if (parseInt(data.res) != 0) {
    //             // alert(1)
    //             $('#user_name').next().html('用户名已经存在，请重新输入')
    //             $('#user_name').next().show();
    //             error_name = true;
    //         }
    //         else {
    //             // alert(0)
    //             $('#user_name').next().hide();
    //             error_name = false;
    //         }

	// 用户名输入框失去焦点时调用
	// function check_user_name_exist() {
	// 	// 1.获取用户名
	// 	username = $('#user_name').val()
	// 	// 2.发起ajax请求，校验用户名是否存在，把username作为参数传过去
	// 	$.get('/user/check_user_exist/?username='+username, function (data) {
	// 		// {'res':0} 用户名已存在
	// 		// {'res':1} 用户名不存在
	// 		if (data.res == 0){
	// 			$('#user_name').next().show().text('用户名已注册')
	// 			error_name = true
	// 		}
	// 		else
	// 		{
	// 			error_name = false
	// 		}
     //    })
    // }


    function check_user_name() {
        var len = $('#user_name').val().length;
        // alert(len)
        if (len < 5 || len > 20) {
            $('#user_name').next().html('请输入5-20个字符的用户名')
            $('#user_name').next().show();
            error_name = true;
        }
        else {
            $('#user_name').next().hide();
            error_name = false;
        }
    }

    function check_pwd() {
        var len = $('#pwd').val().length;
        if (len < 8 || len > 20) {
            $('#pwd').next().html('密码最少8位，最长20位')
            $('#pwd').next().show();
            error_password = true;
        }
        else {
            $('#pwd').next().hide();
            error_password = false;
        }
    }


    function check_cpwd() {
        var pass = $('#pwd').val();
        var cpass = $('#cpwd').val();

        if (pass != cpass) {
            $('#cpwd').next().html('两次输入的密码不一致')
            $('#cpwd').next().show();
            error_check_password = true;
        }
        else {
            $('#cpwd').next().hide();
            error_check_password = false;
        }

    }

    function check_email() {
        var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;

        if (re.test($('#email').val())) {
            $('#email').next().hide();
            error_email = false;
        }
        else {
            $('#email').next().html('你输入的邮箱格式不正确')
            $('#email').next().show();
            error_check_password = true;
        }

    }

    function check_user_name_exist2(async) {
        username = $('#user_name').val()
        $.ajax({
            'url': '/user/check_user_exit/?username=' + username,
            'async': async,
            'success': function (data) {
                if (data.res == 0) {
                    $('#user_name').next().show().text('用户名已经注册')
                    error_name = true
                }
                else {
                    error_name = false
                }
            }

        })
    }

    $('#reg_form2').submit(function () {
        check_user_name();
        //发起同步的ajax请求
        check_user_name_exist2(false)
        // check_has_user();  //提交表单时也需校验用户名是否已经存在
        check_pwd();
        check_cpwd();
        check_email();


        if (error_name == false &&
            error_password == false &&
            error_check_password == false &&
            error_email == false &&
            error_check == false) {

            return true;
        }
        else {
            return false;
        }
    });
})
