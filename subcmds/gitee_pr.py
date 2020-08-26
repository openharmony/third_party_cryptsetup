# -*- coding: UTF-8 -*-
#
# Copyright (C) 2010 JiangXin@ossxp.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import unicode_literals
from __future__ import print_function

import sys
import requests
from command import Command
from git_config import GitConfig

class GiteePr(Command):
  common = True
  helpSummary = "Show gitee pull request list"
  helpUsage = """
%prog [<project>...]
"""

  def _Options(self, p):
    # p.add_option('--build',
    #              dest='build', action='store_true',
    #              help="To trigger ci with repo's config hook")
    p.add_option('--br',
                 type='string', action='store', dest='branch',
                 help='branch to push.')

  def Execute(self, opt, args):
      """
      1.获取project_list的信息，
      2.获取openapi中pr的信息
      3.整合project与pr的关键信息
      4.向配置的hook发送post请求
      :param opt:
      :param args:
      :return:
      [{
      project:name
      project_pr:
        branch of current_branch:[{
        }]
      },{},{}]
      """
      result = []
      if opt.branch:
          branch = opt.branch
      else:
          print('error: need --br option', file=sys.stderr)
          sys.exit(1)
      all = self.GetProjects(args)
      for project in all:
          if project.revisionExpr:
             base_branch = project.revisionExpr
          else:
             base_branch = project.manifest.default.revisionExpr
          project_name = project.name
          branch_tmp = project.GetBranch(branch)
          if not branch_tmp.LocalMerge:
              continue
          branch_name = branch

          # if not branch_name:
          #     sys.stderr.write('CurrentBranch is None, Please set it, you need `repo start -h`\n')
          #     sys.exit(1)

          name_space = project._GiteeNamespace()
          token = self.manifest.manifestProject.config.GetString('repo.token')
          if not token:
              token = GitConfig.ForUser().GetString('repo.token')
              if not token:
                  sys.stderr.write('repo.token is None, Please set it, you need `repo config -h`\n')
                  sys.exit(1)
          p_list = {'project_name': project_name, 'base': base_branch, 'head': branch_name}
          url = 'https://gitee.com/api/v5/repos/%s/%s/pulls' % (name_space, project_name)
          payload = {'base': base_branch, 'head': branch_name, 'page': 0, 'access_token': token, 'state': 'open'}
          try:
              r = requests.get(url, params=payload, timeout=5)
              pr_url = [tmp['html_url'] for tmp in r.json()]
              if pr_url:
                p_list['pull_request'] = pr_url
              else:
                continue
              result.append(p_list)
          except Exception as e:
              sys.stderr.write('ERROR: %s\n' % e)
              sys.exit(1)




      for project in result:
          print('%s        %s pr_url: %s' % (project['project_name'], project['head'], project['pull_request'][0]))



