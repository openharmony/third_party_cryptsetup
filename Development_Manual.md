## 开发手册

## 1、二开关键部分

```
.
├── command.py
├── git_command.py
├── error.py
├── manifest_xml.py
├── project.py
└── subcmds
    ├── __init__.py
    ├── config.py
    ├── gitee_pr.py
    ├── push.py
    ├── start.py
    ├── upload.py
    └── version.py

```

### command
subcmds目录下所有命令的父类

### git_command
对间接调用git命令的封装模块

### error
异常类

### manifest_xml
manifest_xml模块

### project
项目模型模块，与项目相关的基础操作模块

### subcmds
repo 的子命令都在此目录下

### __init__.py
from subcmds 时对all_commands字典初始化，完成repo command与subcmds下命令模块的映射

### config
repo config 命令对应模块

### gitee_pr
repo gitee-pr 命令对应模块

### push
repo push 命令对应模块

### ... 后面的子命令对应关系以此类推

## 2、具体开发案例

### repo psuh 举例
```python
def Execute(self, opt, args):
    project_list = self.GetProjects(args)  #获取repo push仓库列表

    if opt.branch:  # 判断是否传入了branch参数
        branch = opt.branch

    if opt.force:   # 判断是否传入force参数
      if len(project_list) != 1:
        print('error: --force requires exactly one project', file=sys.stderr)
        sys.exit(1)

    if branch:
        for project in project_list:  
          branch_tmp = branch
          if (not opt.new_branch and
                  project.GetUploadableBranch(branch) is None):  # 判断仓库是否有可推送的分支，当有new_branch参数时另外处理
            continue
          branch_tmp = project.GetBranch(branch_tmp)
          if branch_tmp.LocalMerge:
            rb = ReviewableBranch(project, branch_tmp, branch_tmp.LocalMerge)  # 推送分支实例
            pending.append((project, [rb]))  # 加入待推送队列
    if not pending:
      print("no branches ready for upload", file=sys.stderr)
    elif len(pending) == 1 and len(pending[0][1]) == 1:  #进行单个推送或是批量推送
      self._SingleBranch(opt, pending[0][1][0], reviewers)
    else:
      self._MultipleBranches(opt, pending, reviewers)
......
```
以上是我截取的repo push命令的主要逻辑，同时类比subcmds下的命令都是类似的逻辑  
1、通过args参数获取需要处理的project_list（获取需要处理的仓列表）  
2、通过opt参数，判断命令是否选择了相关的option进行进一步判断,进行数据处理（构造需要推送的分支）  
3、拿到构造好的的待处理的数据，进行命令的主要逻辑（开始推送）  


