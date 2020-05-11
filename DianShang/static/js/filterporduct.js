jQuery(function($) {
    $("#id_supplier").change(function(){
        var supplierList= $('#id_supplier')
        var id= $(this).children('option:selected').val();
        if (id ) {
         FilterModels(id);
        }

      });
    
    function FilterModels(suplierid) {
        var productlList = $('#id_product');
        if (suplierid > 0) {
            //new Ajax.Request('/productbysuplier/' + suplierid + '/', {
            $.ajax('/productbysuplier/' + suplierid + '/', {
                method: 'get',
                cache: false,
                dataType: 'json',
                success: function(result,stutas,xhr){
                    //alert(typeof(result));
                    productlList.empty();
                    //productlList.append('<option selected="selected" value="">---------</option>');
                    //var jsondata = JSON.stringify(result);
                   // alert(jsondata);
                    //json返回数据是一个对象{"result":"[{\"id\": 9, \"name\": \"连衣裙女中长款03\"}]"}
                  
                    //取出result的值[{\"id\": 9, \"name\": \"连衣裙女中长款03\"}]，并用eval将此值转化object
                    productdata=eval(result['result'])
                   // alert(productdata);
                    //对jsondata 对象时行遍历，取出具体的id,name，填充option
                      for (p in productdata) {
                      //  alert(jsondata[p]);
                        option = '<option value="' + productdata[p].id + '">' + productdata[p].name + '</option>';
                        productlList.append(option);
                    }
                      
                },
                 error:function(xhr,errorText,errorStatus){
                  alert(xhr.status+' error: '+xhr.statusText);
                },
            });
        }

    }

    $("#id_product").change(function(){
     //   var id= $(this).children('option:selected').val();
      // alert($('#id_product option:selected').val());
        var id = $('#id_product option:selected').val();
        $("#id_product").find("option[val='+id+']").attr("selected",true);

      });
});