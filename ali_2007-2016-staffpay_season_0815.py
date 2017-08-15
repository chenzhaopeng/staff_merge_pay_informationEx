from bs4 import BeautifulSoup
import re
import ch2num
import os
import sys
# -*- coding: utf-8 -*

def fuzzyfinder(user_input, collection):  #公司简称模糊匹配
    if collection == None:
        return 0
    if len(re.findall(r'\(|\)|\）|\（',user_input))>0 or len(re.findall(r'“|”',user_input)) > 0 or len(re.findall(r'\*',user_input)) > 0:
        return 0
    is_match = 0
    pattern = '.*'.join(user_input) # Converts 'djm' to 'd.*j.*m'
    try:
        regex = re.compile(pattern)     # Compiles a regex.
        match = regex.search(collection)  # Checks if the current item matches the regex.
        if match:
            is_match = 1
    except(Exception) as ex:
        print('error:',ex)
    finally:
        return is_match

def find_previous_div(current_div):  #该函数特别用于寻找表格标题，其他地方不适用
    div_previous = None
    div_previous_set = current_div.find_previous_siblings('div')
    div_temp = current_div
    div_previous_bool = 0
    while len(div_previous_set) == 0:
        div_temp = div_temp.find_parent('div')
        if (div_temp['class'])[0] == 'pc' or (div_temp['class'])[0] == 'pf':
            div_previous_bool = 1
            break
        else:
            div_previous_set = div_temp.find_previous_siblings('div')

    if len(div_previous_set)>0 and div_previous_bool == 0 :
        div_previous = div_previous_set[0]

    return div_previous





def find_next_div(current_div):  # 由于每一个内容项div都包括在外层的page div里，此函数可在到达页面底部时跳到下一个页面，并且自动略过页眉页脚div
    next_div = current_div.find_next_sibling('div')
    div_temp = current_div
    while next_div is None:
        next_div = div_temp.find_parent('div').find_next_sibling('div')
        div_temp = div_temp.find_parent('div')
    # if not next_div:
    #     if ((current_div.find_parent('div').find_next_sibling('div'))['class'])[0] == 'pi':
    #         next_page = current_div.find_parent('div', class_='pf').find_next_sibling('div', class_='pf')
    #         if next_page:
    #             next_div_pc = next_page.find('div')
    #             next_div_set = next_div_pc.find_all('div')
    #             if not next_div_set[2].find_next_sibling('div'):
    #                 next_div = next_div_set[2].find_parent('div').find_next_sibling('div')
    #             else:
    #                 next_div = next_div_set[2]
    #     else:
    #         next_div = current_div.find_parent('div').find_next_sibling('div')

    if (next_div['class'])[0] == 'pi':
        next_page = current_div.find_parent('div', class_='pf').find_next_sibling('div', class_='pf')
        if next_page:
            next_div_pc = next_page.find('div')
            next_div_set = next_div_pc.find_all('div')
            if not next_div_set[1].find_next_sibling('div'):
                next_div = next_div_set[1].find_parent('div').find_next_sibling('div')
            else:
                next_div = next_div_set[1]

    # next_div = current_div.find_next_sibling('div')
    # if not next_div:
    #     next_page = current_div.find_parent('div', class_='pf').find_next_sibling('div', class_='pf')
    #     if next_page:
    #         next_div_pc = next_page.find('div')
    #         next_div_set = next_div_pc.find_all('div')
    #         if not next_div_set[2].find_next_sibling('div'):
    #             next_div = next_div_set[2].find_parent('div').find_next_sibling('div')
    #         else:
    #             next_div = next_div_set[2]
    #         # next_div = next_page.find('div', class_='t').find_next_sibling('div').find_next_sibling('div')

    return next_div


def information_extract(html_filename):
    soup = BeautifulSoup(open(html_filename,'rb'), "lxml", from_encoding="utf-8")
    pf = soup.findAll(class_='pf')

    # 未读到表格的处理
    # 先从目录中找合并利润表或利润表的大标题
    # 若目录中未找到或是没有目录，页面中找利润表或合并利润表的大标题

    def else_inEX_else():
        find_bool = 0
        startpf = -1
        for i in range(3, int(len(pf))):
            if find_bool == 1:
                break
            page_temp_pc = pf[i].find('div')
            page_temp = page_temp_pc.find_all('div')
            for div_temp in page_temp:
                div_temp_cursor_str = re.findall(r'合\s*并\s*资\s*产\s*负\s*债\s*表', div_temp.get_text())
                div_temp_cursor_str2 = re.findall(r'\b负\s*债\s*表\b', div_temp.get_text())
                div_temp_cursor_str1 = re.findall(r'资\s*产\s*负\s*债\s*表', div_temp.get_text())
                div_temp_cursor_str3 = re.findall(r'\b[^、]*负\s*债\s*表\b', div_temp.get_text())
                div_temp_cursor_str4 = re.findall(r'\b[^、]*\s*资\s*产\s*负\s*债\s*表\b', div_temp.get_text())
                countlen = len(div_temp_cursor_str)
                countlen1 = len(div_temp_cursor_str1)
                countlen2 = len(div_temp_cursor_str2)
                countlen3 = len(div_temp_cursor_str3)
                countlen4 = len(div_temp_cursor_str4)
                if countlen > 0:
                    div_temp_cursor = (div_temp.get_text()).find(div_temp_cursor_str[0])
                    div_temp_str = (div_temp.get_text())[0:div_temp_cursor]
                    div_temp_str2 = (div_temp.get_text())[div_temp_cursor:]
                    if (len(re.findall(r'[^\s]', div_temp_str2)) - len(re.findall(r'[\u4e00-\u9fa5]',div_temp_cursor_str[0]))) == 0 and (len(re.findall(r'[^\s]', div_temp_str)) == 0):
                       startpf = i
                       find_bool = 1
                       break
                if countlen1 > 0:
                    div_temp_cursor = (div_temp.get_text()).find(div_temp_cursor_str1[0])
                    div_temp_str = (div_temp.get_text())[0:div_temp_cursor]
                    div_temp_str2 = (div_temp.get_text())[div_temp_cursor:]
                    if (len(re.findall(r'[^\s]', div_temp_str2)) - len(re.findall(r'[\u4e00-\u9fa5]',div_temp_cursor_str1[0]))) == 0 and (len(re.findall(r'[^\s]', div_temp_str)) == 0):
                       startpf = i
                       find_bool = 1
                       break
                if countlen2 > 0:
                    div_temp_cursor = (div_temp.get_text()).find(div_temp_cursor_str2[0])
                    div_temp_str = (div_temp.get_text())[0:div_temp_cursor]
                    div_temp_str2 = (div_temp.get_text())[div_temp_cursor:]
                    if (len(re.findall(r'[^\s]', div_temp_str2)) - len(re.findall(r'[\u4e00-\u9fa5]', div_temp_cursor_str2[0]))) == 0 and (len(re.findall(r'[^\s]', div_temp_str)) == 0):
                        startpf = i
                        find_bool = 1
                        break
                if countlen3 > 0:
                    div_temp_cursor = (div_temp.get_text()).find(div_temp_cursor_str3[0])
                    div_temp_str = (div_temp.get_text())[0:div_temp_cursor]
                    div_temp_str2 = (div_temp.get_text())[div_temp_cursor:]
                    if (len(re.findall(r'[^\s]', div_temp_str2)) - len(re.findall(r'[\u4e00-\u9fa5]', div_temp_cursor_str3[0]))) == 0 and (len(re.findall(r'[^\s]', div_temp_str)) == 0):
                        startpf = i
                        find_bool = 1
                        break
                if countlen4 > 0:
                    div_temp_cursor = (div_temp.get_text()).find(div_temp_cursor_str4[0])
                    div_temp_str = (div_temp.get_text())[0:div_temp_cursor]
                    div_temp_str2 = (div_temp.get_text())[div_temp_cursor:]
                    if (len(re.findall(r'[^\s]', div_temp_str2)) - len(re.findall(r'[\u4e00-\u9fa5]', div_temp_cursor_str4[0]))) == 0 and (len(re.findall(r'[^\s]', div_temp_str)) == 0):
                        startpf = i
                        find_bool = 1
                        break

        # print(startpf)

        #如果找到了大标题，向下搜索4页
        current_div = None
        if startpf != -1:
            is_end = 0
            for i in range(startpf, min(startpf+3,len(pf))):
                if is_end == 1:
                    break
                page_temp_pc = pf[i].find('div')
                page_temp = page_temp_pc.find_all('div')
                for i in range(len(page_temp) - 1):
                    div_temp = page_temp[i]

                    div_temp_cursor_str = re.findall(r'\b\s*应\s*付\s*职\s*工\s*薪\s*酬\s*[0-9|,|.]*\b', div_temp.get_text())
                    countlen = len(div_temp_cursor_str)

                    if countlen > 0:
                        current_div = div_temp;
                        is_end = 1
        table2str = ''
        max_search_range = 6  # 最大查找范围，如果超过这个数仍然找不到结束标志，则可以结束查找
        while (current_div != None) and (len(re.findall(r'(应\s*交\s*税\s*费)|(\b应\s*交\s*（\s*税\s*费\s*）)|(\b应\s*交\s*\(\s*税\s*费\s*\))|(\b应\s*交\s*税\s*费\b)',current_div.get_text())) == 0 )and (max_search_range != 0):
            table2str += str(current_div)
            current_div = find_next_div(current_div)
            max_search_range -= 1
        # return str(table2str)

        current_div2 = None
        if table2str == '':
            is_end = 0

            for i in range(3, int(len(pf))):
                if is_end == 1:
                    break
                page_temp_pc = pf[i].find('div')
                page_temp = page_temp_pc.find_all('div')
                # for div_temp in page_temp:
                for i in range(len(page_temp)-1):
                    div_temp = page_temp[i]

                    div_temp_cursor_str = re.findall(r'\b\s*应\s*付\s*职\s*工\s*薪\s*酬\s*[0-9|,|.]*\b', div_temp.get_text())
                    countlen = len(div_temp_cursor_str)

                    if countlen > 0:
                        # next_div_temp = div_temp.find_next_sibling()
                        # if next_div_temp is not None:
                        #     if len(re.findall(r'[0-9|,|.|-]',next_div_temp.get_text())) > 4 or len(re.findall(r'应\s*交\s*税\s*费', next_div_temp.get_text())) > 0:
                        current_div2 = div_temp;
                        is_end = 1
        max_search_range2 = 6  # 最大查找范围，如果超过这个数仍然找不到结束标志，则可以结束查找
        while (current_div2 != None) and (len(re.findall(r'(应\s*交\s*税\s*费)|(\b应\s*交\s*（\s*税\s*费\s*）)|(\b应\s*交\s*\(\s*税\s*费\s*\))', current_div2.get_text())) == 0)  and (max_search_range2 != 0):
            table2str += str(current_div2)
            current_div2 = find_next_div(current_div2)
            max_search_range2 -= 1

        return str(table2str)


    #会计期间
    fiscal_period = None
    year = None
    report_type_temp = None

    # for i in range(5):
    #     str_temp = str(ch2num.chinese2digits(pf[i].get_text())).replace(' ', '')
    #     year_temp = re.findall(r'2\d*?年度报告|2\d*?年年度报告|2\d*?半年度报告|2\d*?第1季度报告|2\d*?第3季度报告', str_temp)
    #     if len(year_temp) > 0:
    #         report_type_temp = re.findall(r'(?:[半]? *年 *度 *报 *告|第 *(?:1|3) *季 *度 *报 *告)', str_temp)
    #         year = year_temp[0].replace("年年度报告", '')
    #         year = year.replace("年度报告", '')
    #         year = year.replace("半年度报告", '')
    #         year = year.replace("第1季度报告", '')
    #         year = year.replace("第3季度报告", '')
    #         year = year[-4:]
    #         fiscal_period_map = {"年度报告": str(year) + "-12-31", "半年度报告": str(year) + "-06-31",
    #                              "第1季度报告": str(year) + "-03-31", \
    #                              "第3季度报告": str(year) + "-09-31"}
    #         report_type_temp2 = report_type_temp[0]
    #         fiscal_period = fiscal_period_map[report_type_temp2]
    #         break
    #公司名称
    company = None
    for i in range(int(len(pf))-1):
        company_temp = re.findall(r'[\u4e00-\u9fa5]{2,}?股份有限公司|[\u4e00-\u9fa5]{2,}?（集团）股份有限公司', str(pf[i].get_text()))
        # company_temp = re.findall(r'[\u4e00-\u9fa5]{1,}[^ ]*[\u4e00-\u9fa5]{1,}有限公司', str(pf[i].get_text()))
        if len(company_temp) > 0:
            company = company_temp[0];
            break
    #股票简称
    short_name = None
    for i in range(int(len(pf))-1):
        pfTemp_text = str(pf[i].get_text())
        front = re.findall(r'股\s*票?\s*简\s*称|股\s*票?\s*名\s*称',pfTemp_text)
        if len(front) > 0:
            str_cursor = pfTemp_text.find(front[0])
            searchText_temp = pfTemp_text[str_cursor+4:str_cursor+80]
            if len(searchText_temp) < 76:
                searchText_temp = searchText_temp+str(pf[i+1].get_text())
            searchText_temp = searchText_temp.replace('：', ' ')
            searchText_temp = searchText_temp.replace(':', ' ')
            searchText_temp = searchText_temp.replace(':', ' ')
            searchText_temp = searchText_temp.replace('、', ' ')
            searchText_temp = searchText_temp.replace('股票代码', ' ')
            each_text = re.findall(r'[^\s]+',searchText_temp)
            for j in range(len(each_text) - 2):
                if each_text[j] == "股" or each_text[j+1][0] == '*':
                    continue
                if len(re.findall(r'.*ST',each_text[j])) > 0 and len(each_text[j]) > 3:
                    short_name = each_text[j]
                    break
                if len(re.findall(r'.*S',each_text[j])) > 0:
                    if fuzzyfinder(each_text[j+1], company):
                        short_name = each_text[j]+each_text[j+1]
                    else:
                        short_name = each_text[j]
                    break
                if fuzzyfinder(each_text[j+1], 'AB') and each_text[j+2] != '股' and fuzzyfinder(each_text[j][-2:], company):
                    short_name = each_text[j]+each_text[j+1]
                    break
                if fuzzyfinder(each_text[j], company):
                    short_name = each_text[j]
                    if fuzzyfinder(each_text[j+1], company):
                        short_name = short_name+each_text[j+1]
                    break
            if len(each_text) < 3:
                for n in range(len(each_text)):
                    if fuzzyfinder(each_text[n], company):
                        short_name = each_text[n]
                        break
            if short_name == None:
                for k in range(len(each_text) - 2):
                    half =int((len(each_text[k])+1)/2)
                    text_two = each_text[k][:half]
                    if fuzzyfinder(text_two, company):
                        short_name = each_text[k]
                        break
            if short_name == None:
                for m in range(len(each_text) - 2):
                    half =int((len(each_text[m])+1)/2)
                    text_two = each_text[m][-half:]
                    if fuzzyfinder(text_two, company) and each_text[m] != 'A股':
                        short_name = each_text[m]
                        break
            break

    #股票代码
    searchText_temp = None
    share_code = None
    ishave_bool = 0
    for i in range(int(len(pf))-1):
        pfTemp_text = str(pf[i].get_text())
        pfTemp_text0 = pfTemp_text.replace(' ', '')
        str_cursor = pfTemp_text0.find("代码")
        if str_cursor > 0:
            local_str = pfTemp_text[:str_cursor]
            empty = local_str.count(" ")
            searchText_temp = pfTemp_text[str_cursor + empty:] + str(pf[i + 1].get_text());
            ishave_bool = 1;
            break
    if ishave_bool == 1:
        share_code_temp = re.findall(r"\b\d{6}\b", searchText_temp)
        if len(share_code_temp) > 0:
            share_code = share_code_temp[0]

    #销售费用合计提取

    table2str = None
    else_inEX_else_str = else_inEX_else()
    if else_inEX_else_str != '':
        table2str_temp1P = re.compile(r'<[^>]*span[^>]*>', re.S)
        table2str_temp1 = table2str_temp1P.sub('', else_inEX_else_str)
        table2str_tempP = re.compile(r'<[^>]+>', re.S)
        table2str = table2str_tempP.sub(' ', table2str_temp1)

    #基本信息总结输出
    # print("公司简称：" + str(short_name) + "\n")
    # print("会计期间：" + str(fiscal_period) + "\n")
    # print("股票代码：" + str(share_code) + "\n")
    # print("销售费用表格:" + str(table2str) + "\n")
    # print("------------------------------------------")
    return str(short_name),str(fiscal_period),str(share_code),str(table2str),str(company)

# path = "html/2016/YEAR/"
# inFile = input("读取文件：")
# information_extract(path+inFile)


# path = ["html/2015/YEAR/","html/2016/YEAR/"]
# fiscal_period_dict = {"html/2016/YEAR/":"2016-12-31","html/2015/YEAR/":"2015-12-31","html/2007/YEAR/":"2007-12-31", \
#                       "html/2008/YEAR/":"2008-12-31"}

# path = ["/Volumes/My Passport/管院合作项目/十年年报HTML/季报和半年报/2016/SEASON1/","/Volumes/My Passport/管院合作项目/十年年报HTML/季报和半年报/2016/SEASON3/"]
# fiscal_period_dict = {"/Volumes/My Passport/管院合作项目/十年年报HTML/季报和半年报/2016/SEASON1/":"2016-3-31","/Volumes/My Passport/管院合作项目/十年年报HTML/季报和半年报/2016/SEASON3/":"2016-9-30"}

path = ["/home/czp/08-11/季报和半年报/2007/SEASON1/","/home/czp/08-11/季报和半年报/2007/SEASON3/",
        "/home/czp/08-11/季报和半年报/2008/SEASON1/","/home/czp/08-11/季报和半年报/2008/SEASON3/",
        "/home/czp/08-11/季报和半年报/2009/SEASON1/","/home/czp/08-11/季报和半年报/2009/SEASON3/",
        "/home/czp/08-11/季报和半年报/2010/SEASON1/","/home/czp/08-11/季报和半年报/2010/SEASON3/",
        "/home/czp/08-11/季报和半年报/2011/SEASON1/","/home/czp/08-11/季报和半年报/2011/SEASON3/",
        "/home/czp/08-11/季报和半年报/2012/SEASON1/","/home/czp/08-11/季报和半年报/2012/SEASON3/"]
        # "/home/czp/08-11/季报和半年报/2013/SEASON1","/home/czp/08-11/季报和半年报/2013/SEASON3",
fiscal_period_dict = {"/home/czp/08-11/季报和半年报/2007/SEASON1/": "2007-3-31",
                      "/home/czp/08-11/季报和半年报/2008/SEASON1/": "2008-3-31",
                      "/home/czp/08-11/季报和半年报/2009/SEASON1/": "2009-3-31",
                      "/home/czp/08-11/季报和半年报/2010/SEASON1/": "2010-3-31",
                      "/home/czp/08-11/季报和半年报/2011/SEASON1/": "2011-3-31",
                      "/home/czp/08-11/季报和半年报/2012/SEASON1/": "2012-3-31",
                      "/home/czp/08-11/季报和半年报/2013/SEASON1/": "2013-3-31",
                      "/home/czp/08-11/季报和半年报/2007/SEASON3/": "2007-9-30",
                      "/home/czp/08-11/季报和半年报/2008/SEASON3/": "2008-9-30",
                      "/home/czp/08-11/季报和半年报/2009/SEASON3/": "2009-9-30",
                      "/home/czp/08-11/季报和半年报/2010/SEASON3/": "2010-9-30",
                      "/home/czp/08-11/季报和半年报/2011/SEASON3/": "2011-9-30",
                      "/home/czp/08-11/季报和半年报/2012/SEASON3/": "2012-9-30",
                      "/home/czp/08-11/季报和半年报/2013/SEASON3/": "2013-9-30",}

import time
for x in range(len(path)):
     files = os.listdir(path[x])
     start = time.clock()

     if os.path.exists(path[x] + 'season_payInformation.txt'):
         os.remove(path[x] + 'season_payInformation.txt')
     fileflow = open(path[x] + 'season_panInformation.txt','a+',encoding='utf-8')
     for filename in files:
         pos = filename.find(".")
         if filename[pos + 1:] == "html":
             print(path[x] + filename + "正在提取...")
             short_name,fiscal_period,share_code,table2str,company = information_extract(path[x] + filename)
             if share_code == 'None' or share_code != filename[0:pos]:
                 share_code = filename[0:pos]
             fiscal_period = fiscal_period_dict[path[x]]
             fileflow.write(share_code+"\n"+short_name+"\n"+fiscal_period+"\n"+company+"\n"+table2str+"\n")
             fileflow.write("---------------------------------\n")
             print(path[x] + filename + "已提取完成！")
     print(path[x]+"已提取完成！")
     fileflow.close()
     end = time.clock()
     print('Running time: %s Seconds' % (end - start))


