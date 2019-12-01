#!/usr/bin/python
#-*-coding:utf-8-*-

import json
import string
import requests
import re
import pprint


class GH_Template( string.Template ):
    delimiter = ":"


CFG = {

    "GH-API" : {

        "ISSUES-REPO" : {
            "URL"  : "https://api.github.com/repos/:owner/:repo/issues",
            "TYPE" : "GET"
        },

        "SEARCH-REPO" : {
            "URL"  : "https://api.github.com/search/repositories?q=:q&sort=:sort&order=:order",
            "TYPE" : "GET"
        },

        "SEARCH-ISSUE" : {
            "URL"  : "https://api.github.com/search/issues?q=:q",
            "TYPE" : "GET"
        },

        "SEARCH-COMMIT" : {
            "URL"  : "https://api.github.com/search/commits?q=:q",
            "TYPE" : "GET"
        },

        "RELEASES-REPO" : {
            "URL"  : "https://api.github.com/repos/:owner/:repo/releases",
            "TYPE" : "GET"
        },

        "TAGS-REPO" : {
            "URL"  : "https://api.github.com/repos/:owner/:repo/tags",
            "TYPE" : "GET"
        },

        "CONTRIBUTORS-REPO" : {
            "URL"  : "https://api.github.com/repos/:owner/:repo/contributors",
            "TYPE" : "GET"
        },

    },


    "GH-CONTENTS-URL" : "https://raw.githubusercontent.com/:owner/:repo/:branch/README.md",


    # TOKEN 값이 없으면 연속으로 10번 이상 API 던지면 바로 아래와 같은 메시지 출력
    #{   u'documentation_url': u'https://developer.github.com/v3/#rate-limiting',
    #    u'message': u"API rate limit exceeded for 110.12.220.235. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)"}

    "TOKEN" : "",


    "PATH" : {
        "DATA" : "./data"
    }
}


WW_DEBUG = True



def GH_API( API, TEMPLATE, TOKEN, HEADERS=None ):

    (flag, msg, result) = (True, "", "")

    URL = GH_Template( API['URL'] ).safe_substitute( TEMPLATE )
    URL += "&" if ( "?" in URL ) else "?"
    if( TOKEN != "" ):
        URL = "%saccess_token=%s" % (URL, TOKEN)

    if( ("page" in TEMPLATE.keys()) and (TEMPLATE['page'] > 1) ):
        URL = "%s&page=%s" % (URL, TEMPLATE['page'])

    if( "per_page" in TEMPLATE.keys() ):
        URL = "%s&per_page=%s" % (URL, TEMPLATE['per_page'])

    if( WW_DEBUG ):
        print( "[DEBUG] (GH_API) URL = %s" % URL )



    # params 사용하는 것으로 고민 필요
    #requests.request('GET', url, params=params, headers=headers)

    try:

        if( API['TYPE'] == "GET" ):
            results = requests.get( URL, headers=HEADERS ) if( HEADERS ) else requests.get( URL )

        elif( API['TYPE'] == "POST" ):
            results = requests.post( URL, data=json.dumps(TEMPLATE['DATA']) )

        elif( API['TYPE'] == "PUT" ):
            results = requests.put( URL, data=json.dumps(TEMPLATE['DATA']) )

        elif( API['TYPE'] == "DELETE" ):
            results = requests.delete( URL )

        else:
            pass


        # status_code를 위의 if문에서 물고 여기까지 오는 것이 깔끔할 듯
        if( not results.status_code in [ 200, 201, 204 ] ):

            flag = False
            msg = "Recieved non 200 response : %s" % URL


        result = json.loads( results.text ) if (results.text != "") else ""



    except requests.exceptions.RequestException as e:

        if( results != None ):
            print( results.text )
        print( e )
        exit()

        flag = False
        msg = "Error: Exception in GH_API"


    return (flag, msg, result)




def GH_README( URL, TEMPLATE, TOKEN ):

    (flag, msg, result) = (True, "", "")

    URL = GH_Template( URL ).safe_substitute( TEMPLATE )
    URL += "&" if ( "?" in URL ) else "?"
    if( TOKEN != "" ):
        URL = "%saccess_token=%s" % (URL, TOKEN)

    if( WW_DEBUG ):
        print( "[DEBUG] (GH_README) URL = %s" % URL )


    try:

        results = requests.get( URL )

        result = re.sub('<.+?>', '', results.text, 0).strip()
        result = result.replace("\n", " ")
        result = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', " ", result)
        result = " ".join(result.split())


    except requests.exceptions.RequestException as e:

        if( results != None ):
            print( results.text )
        print( e )
        exit()

        flag = False
        msg = "Error: Exception in GH_README"


    return (flag, msg, result)






if __name__ == "__main__":

    pp = pprint.PrettyPrinter(indent=4)



    ###
    # 이슈 검색하는 것 테스트 코드

    template = {
        "owner" : "whatwant",
        "repo"  : "whatwant"
    }

    #(flag, msg, result) = GH_API( CFG['GH-API']['ISSUES-REPO'], template, CFG['TOKEN'] )






    ###
    # Search API 테스트 코드


    # 일단 star 많은 순서 위주로 검색을 해봤음
    template = {
        "q"        : "",
        "sort"     : "stars",
        "order"    : "desc",
        "page"     : 1,
        "per_page" : 100
    }


    topics = [
        "Artificial Intelligence",
        "Deep Learning",
        "Machine Learning",
        "Natural Language Processing",
        "Computer Vision",
        "Machine Reasoning"
    ]

    for topic in topics:

        # topic으로 검색을 할 것인지, 그냥 검색어로 검색을 할 것인지에 대한 선택
        #template['q'] = "topic:%s" % topic.replace(" ", "%20")
        template['q'] = "%s" % topic.replace(" ", "%20")

        # 한 번의 API에 30(per_page)개 결과밖에 안들어오기에, page에 대한 처리 로직 추가
        template['page'] = 1


        while True:

            HEADER = { "Accept" : "application/vnd.github.mercy-preview+json" }
            (flag, msg, result) = GH_API( CFG['GH-API']['SEARCH-REPO'], template, CFG['TOKEN'], HEADER )

            if( template['page'] == 1 ):
                print( "topic : %s" % topic )
                print( "total_count: %s" % result['total_count'] )
                print( "incomplete results: %s" % "True" if( result['incomplete_results'] ) else "False" )

            if( not "items" in result.keys() ):
                pp.pprint( result )
                exit()

            for idx, item in enumerate(result['items']):

                print( "    [%s/%s] : (%s) %s" % ( ((idx+1)+((template['page']-1)*template['per_page'])), result['total_count'], item['stargazers_count'], item['html_url'] ) )

                temp = {
                    "q"        : "repo:%s+type:issue+state:closed" % item['full_name'],
                    "per_page" : 1
                }
                (flag2, msg2, result2) = GH_API( CFG['GH-API']['SEARCH-ISSUE'], temp, CFG['TOKEN'] )
                item['closed_issues_count'] = result2['total_count']


                temp = {
                    "q"        : "repo:%s+type:pr+state:closed" % item['full_name'],
                    "per_page" : 1
                }
                (flag3, msg3, result3) = GH_API( CFG['GH-API']['SEARCH-ISSUE'], temp, CFG['TOKEN'] )
                item['open_pr_count'] = result3['total_count']

                temp = {
                    "q"        : "repo:%s+type:pr+state:open" % item['full_name'],
                    "per_page" : 1
                }
                (flag4, msg4, result4) = GH_API( CFG['GH-API']['SEARCH-ISSUE'], temp, CFG['TOKEN'] )
                item['closed_pr_count'] = result4['total_count']


                temps = item['full_name'].split("/")
                item['owner'] = temps[0]
                item['repo'] = temps[1]


                temp = {
                    "owner"    : item['owner'],
                    "repo"     : item['repo'],
                    "per_page" : 100,
                    "page"     : 1
                }
                releases = []
                while True:
                    (flag5, msg5, result5) = GH_API( CFG['GH-API']['RELEASES-REPO'], temp, CFG['TOKEN'] )
                    releases.extend( result5 )

                    if( len(result5) < temp['per_page'] ): break
                    temp['page'] += 1

                item['releases_count'] = len(releases)
                print( "releases_count : %s" % item['releases_count'] )



                temp = {
                    "owner"    : item['owner'],
                    "repo"     : item['repo'],
                    "per_page" : 100,
                    "page"     : 1
                }
                tags = []
                while True:
                    (flag6, msg6, result6) = GH_API( CFG['GH-API']['TAGS-REPO'], temp, CFG['TOKEN'] )
                    tags.extend( result6 )

                    if( len(result6) < temp['per_page'] ): break
                    temp['page'] += 1

                item['tags_count'] = len(tags)
                print( "tags_count : %s" % item['tags_count'] )


                temp = {
                    "owner"    : item['owner'],
                    "repo"     : item['repo'],
                    "branch"   : item['default_branch']
                }
                (flag7, msg7, result7) = GH_README( CFG['GH-CONTENTS-URL'], temp, CFG['TOKEN'] )
                item['readme'] = result7


                temp = {
                    "owner"    : item['owner'],
                    "repo"     : item['repo'],
                    "per_page" : 100,
                    "page"     : 1
                }
                contributors = []
                item['commits_count'] = 0
                while True:
                    (flag8, msg8, result8) = GH_API( CFG['GH-API']['CONTRIBUTORS-REPO'], temp, CFG['TOKEN'] )

                    for tmp in result8:
                        contributors.append(  { 'login' : tmp['login'], 'contributions' : tmp['contributions'] } )
                        item['commits_count'] += tmp['contributions']


                    if( len(result8) < temp['per_page'] ): break
                    temp['page'] += 1

                print( "commits_count : %s" % item['commits_count'] )


                #pp.pprint( result6 )
                exit()




            if( len(result['items']) < template['per_page'] ): break
            template['page'] += 1
            #if( template['page'] > 5 ): break




    #pp.pprint( result )

    exit()
