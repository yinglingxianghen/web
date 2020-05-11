
$(function () {
	
	jQuery.support.placeholder = false;
	test = document.createElement('input');
	if('placeholder' in test) jQuery.support.placeholder = true;
	
	if (!$.support.placeholder) {
		
		$('.field').find ('label').show ();
		
	}
	
});

$(document).ready(function() {

    $("#submitid").click(
        function(){
            var v = $("#submitform").serialize();
            alert(v);
            //loginvalid(v);

    });
});

function loginvalid(v)
{
    $.ajax({
        type: "post",
        dataType: "text/html",
        url: "<%=appPath%>/user/signin",
        data: v,
        success: function(data) {
            if (data.success == "true") {
                alert("登录成功");
            } else {
                alert("失败");
            }
        },
        error: function() {
            alert("0失败");
        }

    });
}