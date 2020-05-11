jQuery(function($) {

	/*
	| ----------------------------------------------------------------------------------
	| Shopping cart - Remove Row on click Close button
	| ----------------------------------------------------------------------------------
	*/
    var post_flag = false;
	$('.add-cart').on('click', function() {
		var product_id = $(this).data('product-id');
		var qty=$('#id_quantity').val();
		if (qty==null){
			qty=1;
		}
		var var_data = {
                "csrfmiddlewaretoken":$("input[name='csrfmiddlewaretoken']").val(),"product_id":product_id,"quantity":qty
            }
         var url='/cart/cart_add_ajax/';
		 if(post_flag) return; //如果正在提交则直接返回，停止执行
		 post_flag = true;//标记当前状态为正在提交状态
         $.ajax({
                url:url ,
                type: "POST",
                data: var_data,
                cache: false,
                dataType: 'json',
                success: function (data) {
                	post_flag =false; //在提交成功之后将标志标记为可提交状态
                	if (data.flag == "201") {
						alert('成功加入购物车');
						window.location.reload();
					}
					else{
						alert('系统错误，请与管理员联系');
					}
				},
				error:function(xhr,errorText,errorType){//一般都直接用xhr对象
                	post_flag =false; //在提交成功之后将标志标记为可提交状态
					//alert("发生错误："+xhr.status);//返回错误状态码
					//alert(errorText+xhr);
				}

			});
         return false;
	})

});