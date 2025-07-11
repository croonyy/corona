# Cameo
<p align="center">
  <a href="#"><img src="static/images/account-logo.png" alt="FastAPI"></a>
</p>


#### 介绍
cameo是一个开源项目(fastapi-admin/fastapiadmin/fastapi_admin)，用于帮助开发者快速搭建fastapi项目,并且自带了一个admin应用（前后端分离,前端使用vue3的开源框架naive-ui-admin），参考django-admin设计，使用tortoise-orm作为数据库操作框架，支持mysql,sqlite,postgresql等多种数据库，实现RBAC权限管理模式，增删改查api自动生成。

#### 项目地址
- [__github__ https://github.com/croonyy/cameo](https://github.com/croonyy/cameo)
- [__gitee__ https://gitee.com/croonyy/cameo](https://gitee.com/croonyy/cameo)

#### 版本依赖
- __python__ --version:3.13.0
- __vue3__ 
- __Node__ -v:v22.14.0
- __npm__ -version:10.9.2

#### 安装教程

前后端依赖安装
```bash
# 事先安装python3.13

# 克隆源码
git clone https://gitee.com/croonyy/cameo.git

# 进入到项目目录 cd cameo
# 安装python环境依赖,如果依赖下载慢，请自行更换pip镜像源
pip install -r requirements.txt
# 初始化数据库
aerich upgrade
#执行脚本，创建admin用户（密码可后续自行更改），和模型权限
python init_data.py

# 前端安装
# 进入到/front目录
cd front
pnpm install


```
#### 运行
```bash
# 1、运行后端服务
# 如果是python虚拟环境，请先激活虚拟环境 conda activate [python_env_name]
# 进入到项目目录下，执行
python run.py

# 2、运行前端服务
# 进入到前端目录下
cd front
pnpm run dev

# 3、访问
# 访问后端接口文档
http://localhost:3014/udadmin/docs
# 访问前端页面
http://localhost:1992/
# 登录账号/密码,预置两个用户，一个管理员和一个普通用户，可自行编辑用户修改密码
admin/admin
test_user/123456
```

#### 项目图片展示
###### 接口文档
![api_doc](static/images/api_doc.png)
###### 控制台
![console](static/images/console.png)
###### 用户列表
![user](static/images/user.png)
###### 编辑用户
![edit_user](static/images/edit_user.png)
###### 权限实例
![permission](static/images/permission.png)
###### 编辑权限
![edit_permission](static/images/edit_permission.png)
###### 创建角色
![create_role](static/images/create_role.png)

#### 项目结构
```shell
├── apps  # app目录，推荐一个app创建一个文件夹,可参考源码样例，也可自行组织app代码结构
  ├── app1  # 样例app
    ├── ...
  ├── udadmin  # admin应用
    ├── ...
├── config
  ├── settings.py  # 项目配置文件
├── db
  ├── db.sqlite3  # 默认数据库为sqlite3，此为数据库文件
  ├── init
├── front  # 前端根目录
  ├── ...
├── migrations  # 数据库迁移文件，如若更换数据库，需要重新生成
  ├── app1  # 一个app会生成一个文件夹
  ├── udadmin
├── notes  # 笔记
  ├── ...
├── static  # 静态文件
  ├── docs-ui  # 为了swagger文档从本地加载，文件本地化
  ├── images  # 项目展示图片
  ├── favicon.ico
├── test  # 测试代码
  ├── ...
├── tools  # 工具代码
  ├── locate_print.py
  ├── objdoc.py
  ├── timer.py
├── .gitignore
├── cert.pem
├── init_data.py  # 初始化数据库的用户和权限的脚本
├── key.pem
├── main.py
├── pyproject.toml
├── README.en.md
├── README.md
├── requirements.txt  # python环境依赖
├── run.py  # 主入口，python run.py 启动项目
├── vscode_extensions.txt  # vscode 插件
```


#### 使用说明 （请按步骤参考样例app1，熟悉步骤之后可删除app1目录，并创建自己的app）

1.  创建app1目录
2.  创建app1/app.py,定义app路由实例
3.  创建app1/models.py
4.  在app1/models.py里面定义模型
5.  创建app1/ui.py，定义前端模型显示配置
6.  在app1/app.py注册模型和ui
7.  如果需要开发其他api，可创建view文件夹（推荐），或者自行组织文件结构书写代码

###### 上述步骤结束后，前端会自动生成模型的增删改查页面，管理员可直接看到，其他用户需要定义权限并赋权才看得到，权限格式参考admin应用已有的模型权限

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request
