# Corona

#### 介绍
Corona 是一个开源项目，用于帮助开发者快速搭建fastapi项目,并且自带了一个admin应用（前后端分离），参考django-admin设计，使用tortoise-orm作为数据库操作框架，支持多种数据库，支持mysql,sqlite,postgresql,等数据库。实现RBAC权限管理模式。

#### 软件架构
python3.13,Tortoise-orm


#### 安装教程

前后端依赖安装
```bash
# 事先安装python3.13

# 克隆源码
git clone https://github.com/

# 进入到项目目录
# 安装python环境依赖,如果依赖下载慢，请自行更换pip镜像源
pip install -r requirements.txt

# 前端安装
# 进入到/front目录
cd front
pnpm install

# 初始化数据库
aerich upgrade

```
### 运行
```bash
# 1、运行后端
# 请先激活虚拟环境 conda activate [python_env_name]
# 进入到项目目录下,如果是python虚拟环境，
python run.py


# 2、运行前端
# 进入到前端目录下
cd front
pnpm run dev


# 3、访问
# 访问后端接口文档
http://localhost:3014/udadmin/docs

# 访问前端页面
http://localhost:1992/
```

```


#### 使用说明

1.  xxxx
2.  xxxx
3.  xxxx

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
