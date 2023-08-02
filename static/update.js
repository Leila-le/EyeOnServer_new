setInterval(function (){
    //发送Ajax请求
    $.ajax({
        url:'/api',//Ajax 请求的URL
        type:'GET',
        dataType:'json',
        success:function (data){
            $('#data-container').html(data);
        }
    });
},5000);//间隔5秒执行一次