setInterval(function (){
    //发送Ajax请求
    $.ajax({
        url:'/home',//Ajax 请求的URL
        type:'GET',
        dataType:'html',
        success:function (info){
            $('#data-container').html(info);
        }
    });
},5000);//间隔5秒执行一次