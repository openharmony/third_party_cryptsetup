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
import sys
import requests
import json
from command import Command
from git_command import GitCommand
from error import GitError


class GiteePr(Command):
  common = True
  helpSummary = "Show gitee pull request list"
  helpUsage = """
%prog [<project>...]
"""

  # def _Options(self, p):
  #   p.add_option('--build',
  #                dest='build', action='store_true',
  #                help="To trigger ci with repo's config hook")

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
      all = self.GetProjects(args)
      for project in all:
          if project.revisionExpr:
             base_branch = project.revisionExpr
          else:
             base_branch = project.manifest.default.revisionExpr
          project_name = project.name
          branch_name = project.CurrentBranch

          if not branch_name:
              sys.stderr.write('CurrentBranch is None, Please set it, you need `repo start -h`\n')
              sys.exit(1)
          name_space = project._GiteeNamespace()
          token = self.manifest.manifestProject.config.GetString('repo.token')

          if not token:
              sys.stderr.write('repo.token is None, Please set it, you need `repo config -h`\n')
              sys.exit(1)
          p_list = {'project_name': project_name, 'base': base_branch, 'head': branch_name}
          url = 'https://gitee.com/api/v5/repos/%s/%s/pulls' % (name_space, project_name)
          payload = {'base': base_branch, 'head': branch_name, 'page': 0, 'access_token': token, 'state': 'open'}
          try:
              r = requests.get(url, params=payload, timeout=5)
              pr_url = [tmp['html_url'] for tmp in r.json()]
              p_list['pull_request'] = pr_url if pr_url else ['']
              # total_page = int(r.headers['total_page'])
              # for page in range(2, total_page+1):
              #     payload['page'] = int(page)
              #     r = requests.get(url, params=payload)
              #     p_list['pull_request'].extend([tmp['html_url'] for tmp in r.json()])
              result.append(p_list)
          except Exception as e:
              sys.stderr.write('ERROR: %s\n' % e)
              sys.exit(1)
      # if opt.build:
      #     hook_url = self.manifest.manifestProject.config.GetString('repo.hook')
      #     if not hook_url:
      #         sys.stderr.write('repo.hook is None, Please set it, you need `repo config -h`\n')
      #         sys.exit(1)
      #     try:
      #         response = requests.post(hook_url, json=json.dumps(result), timeout=5)
      #     except Exception as e:
      #         sys.stderr.write('POST HOOK ERROR: %s\n' % e)
      #         sys.exit(1)
      #     print('POST HOOK SUCCESS')
      #     print('STATUS: %s' % response.status_code)
      #     print('BODY: %s' % response.content)




      for project in result:
          print('%s        %s pr_url: %s' % (project['project_name'], project['head'], project['pull_request'][0]))



