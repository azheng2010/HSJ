# HSJ

#### 介绍
HSJ辅助工具
当前版本: 0.1.5

#### 软件架构
软件架构说明


#### 安装教程

1. 安装手机版python3运行环境Pydroid3，可参考简书  [[Pydroid3配置安装教程](https://www.jianshu.com/p/5d9abd6f1405)]
2. 设置Pydroid3，并安装必要的模块
3. 下载本脚本程序
    首次下载，可用一键下载程序脚本：
    wget https://gitee.com/wzh2018/HSJ/repository/archive/master.zip -O HSJ-master.zip && unzip -o HSJ-master.zip && rm HSJ-master.zip
    或者
    wget https://github.com/azheng2010/HSJ/archive/master.zip -O HSJ-master.zip && unzip -o HSJ-master.zip && rm HSJ-master.zip
4. 加载并运行脚本程序

#### 使用说明

1. 主机开启热点
2. pydroid3加载main.py脚本，运行
3. 考试机连接热点，并设置手动http代理
4. 正常考试即可

#### 参考资料

1. [Pydroid3配置安装教程](https://www.jianshu.com/p/5d9abd6f1405)
2. [MitmProxy的安装与使用](https://www.jianshu.com/p/7b0ea91c081c)
3. 提交代码
4. 新建 Pull Request

#### 版本更新日志

##### version 0.0.1 更新日期：2018-10-21
1. 实现基本功能，PC端本地查询题库
2. PC端简单UI界面

##### version 0.0.2 更新日期：2018-11-24
1. 转移到安卓移动端，适配Pydroid3环境
2. 使用中间人代理工具，抓取手机端信息，通过qid搜索实现答案自动匹配

##### version 0.0.3 更新日期：2018-11-27
1. 增加文字匹配答案功能（文本相似度）

##### version 0.0.4 更新日期：2018-12-04
1. 实现自动修改答案功能
2. 放弃PC端脚本开发工作

##### version 0.0.5 更新日期：2019-01-05
1. 增加设定正确率范围功能，实现机器答题与人工答题补充

##### version 0.0.7 更新日期：2019-01-07
1. HSJapp对提交数据加密，紧急增加人工答题模式，暂时放弃自动修改答案功能

##### version 0.0.8 更新日期：2019-01-09
1. HSJapp提交答案数据采用加密方式，脚本做相应升级，恢复自动修改答案功能

##### version 0.0.9 更新日期：2019-02-28
1. 全新改版HSJ辅助工具，功能模块化装配
2. 增加账号控制功能

##### version 0.1.0 更新日期：2019-03-31
1. 进行了一些调整，修复一些bug
2. 在Github上开源部署项目

##### version 0.1.1 更新日期：2019-04-02
1. 增加在线验证用户和有效期功能

##### version 0.1.2 更新日期：2019-04-13
1. 增加检查版本和更新脚本功能

##### version 0.1.3 更新日期：2019-04-15
1. 增加一键更新题库功能

##### version 0.1.4 更新日期：2019-04-28
1. HSJapp升级提交答案加密方式，脚本程序做相应升级，恢复修改答案功能
2. 调整登录和功能选择的顺序

##### version 0.1.5 更新日期：2019-04-28
1. 更改更新源为国内源
2. 调用地址进行加密处理