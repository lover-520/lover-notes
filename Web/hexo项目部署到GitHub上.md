---
title: hexo部署到GitHub
tags: Web
categories: Web
---

在完成了整个项目之后，可以通过localhost在浏览器上查看效果，但那只是在本地上查看，可以尝试将代码部署到GitHub上从而别人也可以通过这个网址看到效果。<!--more-->

## 条件准备

默认下列条件已经满足：

* 一个完整的hexo项目文件；
* 有着配置好的git和GitHub账号；

## 配置过程

1. 在GitHub上新建一个项目，像我的用户名是lover-520，那么我的项目名取为lover-520.github.io，至于其他的readme，license等随便；

2. 复制GitHub上项目文件的ssh，比如我的是git@github.com:lover-520/lover-520.github.io.git；

3. 在hexo项目配置文件\_config.yml中找到deploy改为下面这样：

   ```yaml
   deploy:
     type: git
     repo:
       github: git@github.com:lover-520/lover-520.github.io.git
     branch:  main
   ```

4. 在项目工程目录中执行：

```shell
$ hexo g
```

然后

```shell
$ hexo d
```

按照正常情况嘛，项目文件应该上传到GitHub上去了，然后浏览器中输入https://lover-520.github.io/就能看到效果了，但是我在部署时，没有报错，也创建了.deploy_git文件夹，但是却并没有上传到GitHub上去，所以打开那个网站是404界面。（你要是添加了readme文件的话就不是404）

## 问题解决

好嘛，没有上传到GitHub上去，那肯定就不能正常显示啊，搜了网上的方法，没有找到方法。然后试了下自己的想法，结果可以行得通，于是在这里记录一下：

可以发现.deploy_git文件夹里面其实是一个git仓库，那么其实hexo d命令应该是自动把我们的文件上传到GitHub上，那么我们也可以考虑自己将这个文件夹直接上传；

进入.deploy_git文件夹

```shell
$ cd .deploy_git
```

先将这个master分支改成main分支：

```shell
$ git checkout -b main
$ git merge master
```

然后添加远程仓库：

```shell
$ git remote add origin git@github.com:lover-520/lover-520.github.io.git
```

拉取远程

```shell
$ git pull origin main
```

提交

```shell
$ git add .
$ git commit -m 'XXX'
```

与远程同步

```shell
$ git push
```

若是出现Updates were rejected 错误，可先执行

```shell
$ git pull origin main --allow-unrelated-histories
```

然后

```shell
$ git push origin main
```

就这样，我们可以发现GitHub上出现了文件，网站也就能正常访问了。那么在添加新博客时，需要执行

```shell
$ hexo g
$ hexo d
```

然后再将.deploy_git文件夹的更改同步到GitHub上。