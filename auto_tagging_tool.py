# !/usr/bin/env python
"""
#File name:auto_tagging_tool
#Author:Zhenyu
#Description:Use GitLab's API for automatic tagging of multiple projects
#Version:1.0    :It can only be used under http://172.18.32.120:9601/pde_ate/
"""


import argparse
import time
# import requests
import json
import urllib.parse
import re
try:
    from colorama import Fore, Back, Style, init
    package_installed = True
    init(autoreset=True)
except ImportError:
    package_installed = False
try:
    import requests
except ImportError:
    print("pls import requests first!!!")
    exit()

class AUTO_TAG:
    def __init__(self):
        self.access_token=''
        self.gitlab_url='http://172.18.32.120:9601'
        self.headers = {'PRIVATE-TOKEN': self.access_token}
        self.tagname=''
        self.tagmessage=''
        self.branch='dev'
        self.file='tag_info.log'

    def check_url_is_good_return_project_id(self,project_url):
        project_name = '/'.join(project_url.split('/')[-3:]).replace('.git',
                                                                     '')  # include "pde_ate" , pde_ate/bpgxp/sidd
        encoded_name = urllib.parse.quote_plus(project_name)  # pde_ate/bpgxp/sidd -> pde_ate%2Fbpgxp%2Fsidd
        response = requests.get(f"{self.gitlab_url}/api/v4/projects/{encoded_name}", headers=self.headers)
        if response.status_code != 200:
            print(f"failed to connect: {encoded_name} url return: {response.content}")
            exit()
        else:
            project_id = response.json()['id']
            return project_id

    def create_tag(self,gitlab_url,project_id):
        tag_url = '{}/api/v4/projects/{}/repository/tags'.format(gitlab_url, project_id)
        tag_data = {
            'tag_name': self.tagname,
            'ref': self.branch,
            'message': self.tagmessage
        }

        response = requests.post(tag_url, headers=self.headers, data=tag_data)
        tag_info = response.json()
        if response.status_code != 201:
            print(f"failed to create tag {tag_url} url return:{tag_info.get('message')}")
            exit()
        else:
            return tag_info

    def write_push_log(self,info):
        ipinfo=AUTO_TAG.extract_info(self,info)
        try:
            with open(self.file, 'a') as f:
                f.write("================" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "================")
                f.write(json.dumps(info, indent=4))
                f.write(json.dumps(ipinfo,indent=4))
        except Exception as e:
            print(e)
            return ipinfo

    def extract_info(self,info):
        web_info = info.get('commit').get('web_url')
        ipinfo = {}
        pattern = r"http://172\.18\.32\.120:9601/([^/]+)/([^/]+)/([^/]+)/.*commit/(.*)"
        match = re.search(pattern, web_info)
        if match:
            part1, part2, part3, commit = match.groups()
            ipinfo[part1 +'-'+ part2 +'-'+ part3]=commit
            return ipinfo

    def find_the_last_commit_dict(self,filename, ipname):
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except Exception as e:
            print(e)

        start = len(content) - content[::-1].find('{') - 1
        end = len(content) - content[::-1].find('}') - 1

        while start >= 0 and end >= 0:
            try:
                obj = json.loads(content[start:end + 1])
                if isinstance(obj, dict) and ipname in obj:
                    return obj
            except json.JSONDecodeError:
                pass
            start = content.rfind('{', 0, start)
            end = content.rfind('}', 0, end)
        return None

    def diff_the_commit_history(self,old_dict,new_dict):
        if old_dict == new_dict:
            return False
        else:
            return True

    def process_args(self):
        url=[]
        parser = argparse.ArgumentParser()
        parser.add_argument("--url",'-u',default='',type=str,required=False,help='the *.git project url')
        parser.add_argument("--tag",'-t',default='',type=str,required=True,help='the tag name')
        parser.add_argument("--message",'-m',default='',type=str,required=False,help='the tag message')
        parser.add_argument("--file",'-f',default='',type=str,required=False,help='the file path of push log')
        parser.add_argument("--branch",'-b',default='dev',type=str,required=False,help='the tag of branch')
        # parser.add_argument("--accesstoken",'-a',default='',type=str,required=False,help='ur access token')
        args = parser.parse_args()
        self.tagname=args.tag
        self.tagmessage=args.message
        self.branch=args.branch
        if args.file != '':
            self.file=args.file
        if args.url != '':
            url.append(args.url)
        return url


if __name__ == "__main__":
    ############init personal info#####################################
    access_token=''
    gitlab_url=''

    ###########if only one project need process########################
    iurl=[]
    auto=AUTO_TAG()
    iurl=auto.process_args()

    ###########open the projects.txt，Prepare the project url list#####
    if not iurl:
        try:
            with open('projects.txt', 'r') as file:
                for line in file:
                    project_path = line.strip()
                    if not project_path.startswith("#"):
                        iurl.append(line)
        except Exception as e:
            print(e)
    ###########Traverse the project url list###########################
    for u in iurl:
        # print("This URL will be processed:",u)
        iprojectid = auto.check_url_is_good_return_project_id(u)#get the projectid from gitlab
        itaginfo = auto.create_tag(auto.gitlab_url, iprojectid)#push the tag to gitlab and dump the message

        current_ipinfo_dict=auto.extract_info(itaginfo)#get current ip info from url on message
        (ipname,commitvar),=current_ipinfo_dict.items()
        last_ipinfo_dict=auto.find_the_last_commit_dict(auto.file,ipname)#get the ip last commit info from local log
        the_ip_commit_if_change=auto.diff_the_commit_history(last_ipinfo_dict,current_ipinfo_dict)

        if package_installed:
            if the_ip_commit_if_change:
                print(Fore.GREEN + 'Some Change in this IP:'+str(current_ipinfo_dict))
                print(Style.RESET_ALL,end="")
            else:
                print(Fore.RED + 'No   Change in this IP:'+str(current_ipinfo_dict))
                print(Style.RESET_ALL,end="")
        else:
            if the_ip_commit_if_change:
                print("Some Change in this IP:", current_ipinfo_dict)
            else:
                print("No   Change in this IP:", current_ipinfo_dict)

        auto.write_push_log(itaginfo)#log logs
        # print("This URL has been processed successfully:", u)




