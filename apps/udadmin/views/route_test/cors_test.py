from fastapi import Request, Query
from fastapi.responses import RedirectResponse, Response, JSONResponse
from ...utils.urls import api

@api(
    methods=["GET"],
    tags=["Test"],
)
def cors_test(request: Request):
    print(f"request.cookies:{request.cookies}")
    headers = {
        # "Access-Control-Allow-Origin": "http://172.9.50.223:1718",
        # "Access-Control-Allow-Credentials": "true",  # 如果要带cookie跨域请求本接口，需要设置这个头
    }
    response = JSONResponse({"msg": "test"}, headers=headers)
    return response


# 另外一个服务上的页面如下,用于测试跨域请求本服务上的这个路径函数
'''
<!-- html基本结构 -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Title</title>
  </head>
  <body>
    <h1>跨域请求测试</h1>
    <input type="text" id="url" placeholder="请输入url" />
    <button id="cors">跨域请求</button>
    <script>
      // 获取按钮元素
      var corsBtn = document.getElementById("cors");
      // 为按钮添加点击事件
      // http://172.9.50.223:1001/udadmin/api/v1/cors_test
      corsBtn.onclick = function () {
        var url = document.getElementById("url").value;
        console.log(url);
        // 不带cookie请求，服务端只需要设置Access-Control-Allow-Origin
        // fetch(url, { mode: "cors"}).then((response) =>    
        // 带cookie跨域请求 前端要（credentials: "include"），服务端设置头Access-Control-Allow-Credentials: true，否则报错
        fetch(url, { mode: "cors", credentials: "include" }).then((response) => 
          console.log(response.json())
        );

        // // 创建XMLHttpRequest对象
        // var xhr = new XMLHttpRequest();
        // // 设置请求方法和URL
        // xhr.open('GET', url, true);
        // // 设置请求头
        // xhr.setRequestHeader('Content-Type', 'application/json');
        // // 设置响应类型
        // xhr.responseType = 'json';
        // // 监听请求状态变化
        // xhr.onreadystatechange = function () {
        //     // 请求完成且响应成功
        //     if (xhr.readyState === 4 && xhr.status === 200) {
        //         // 获取响应数据
        //         var response = xhr.response;
        //         // 在控制台输出响应数据
        //         console.log(response);
        //     }
        // };
        // // 发送请求
        // xhr.send();
      };
    </script>
  </body>
</html>
'''

