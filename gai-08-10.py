import codecs

from bs4 import BeautifulSoup

import re

import ch2num

import os

import sys


# 公司简称模糊匹配

def fuzzyfinder(user_input, collection):
    if collection == None:
        return 0

    if len(re.findall(r'\(|\)|\）|\（', user_input)) > 0 or len(re.findall(r'“|”', user_input)) > 0 or len(
            re.findall(r'\*', user_input)) > 0:
        return 0

    is_match = 0

    pattern = '.*'.join(user_input)  # Converts 'djm' to 'd.*j.*m'

    try:

        regex = re.compile(pattern)  # Compiles a regex.

        match = regex.search(collection)  # Checks if the current item matches the regex.

        if match:
            is_match = 1

    except(Exception) as ex:

        print('error:', ex)

    finally:

        return is_match


# 该函数特别用于寻找表格标题，其他地方不适用

def find_previous_div(current_div):
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

    if len(div_previous_set) > 0 and div_previous_bool == 0:
        div_previous = div_previous_set[0]

    return div_previous


# 提取基本信息,  包括 会议期间,公司名称,股票代码和公司简称

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


def base_information_extract(html_filename):
    soup = BeautifulSoup(open(html_filename, 'rb'), "lxml", from_encoding="utf-8")

    pf = soup.findAll(class_='pf')

    # 会计期间

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

    # 公司名称

    company = None

    for i in range(10):

        company_temp = re.findall(r'[\u4e00-\u9fa5]{2,}?股份有限公司|[\u4e00-\u9fa5]{2,}?（集团）股份有限公司', str(pf[i].get_text()))

        # company_temp = re.findall(r'[\u4e00-\u9fa5]{1,}[^ ]*[\u4e00-\u9fa5]{1,}有限公司', str(pf[i].get_text()))

        if len(company_temp) > 0:
            company = company_temp[0];

            break

    # 股票简称

    short_name = None

    for i in range(10):

        pfTemp_text = str(pf[i].get_text())

        front = re.findall(r'股\s*票?\s*简\s*称|股\s*票?\s*名\s*称', pfTemp_text)

        if len(front) > 0:

            str_cursor = pfTemp_text.find(front[0])

            searchText_temp = pfTemp_text[str_cursor + 4:str_cursor + 80]

            if len(searchText_temp) < 76:
                searchText_temp = searchText_temp + str(pf[i + 1].get_text())

            searchText_temp = searchText_temp.replace('：', ' ')

            searchText_temp = searchText_temp.replace(':', ' ')

            searchText_temp = searchText_temp.replace(':', ' ')

            searchText_temp = searchText_temp.replace('、', ' ')

            searchText_temp = searchText_temp.replace('股票代码', ' ')

            each_text = re.findall(r'[^\s]+', searchText_temp)

            for j in range(len(each_text) - 2):

                if each_text[j] == "股" or each_text[j + 1][0] == '*':
                    continue

                if len(re.findall(r'.*ST', each_text[j])) > 0 and len(each_text[j]) > 3:
                    short_name = each_text[j]

                    break

                if len(re.findall(r'.*S', each_text[j])) > 0:

                    if fuzzyfinder(each_text[j + 1], company):

                        short_name = each_text[j] + each_text[j + 1]

                    else:

                        short_name = each_text[j]

                    break

                if fuzzyfinder(each_text[j + 1], 'AB') and each_text[j + 2] != '股' and fuzzyfinder(each_text[j][-2:],

                                                                                                   company):
                    short_name = each_text[j] + each_text[j + 1]

                    break

                if fuzzyfinder(each_text[j], company):

                    short_name = each_text[j]

                    if fuzzyfinder(each_text[j + 1], company):
                        short_name = short_name + each_text[j + 1]

                    break

            if len(each_text) < 3:

                for n in range(len(each_text)):

                    if fuzzyfinder(each_text[n], company):
                        short_name = each_text[n]

                        break

            if short_name == None:

                for k in range(len(each_text) - 2):

                    half = int((len(each_text[k]) + 1) / 2)

                    text_two = each_text[k][:half]

                    if fuzzyfinder(text_two, company):
                        short_name = each_text[k]

                        break

            if short_name == None:

                for m in range(len(each_text) - 2):

                    half = int((len(each_text[m]) + 1) / 2)

                    text_two = each_text[m][-half:]

                    if fuzzyfinder(text_two, company) and each_text[m] != 'A股':
                        short_name = each_text[m]

                        break

            break

    # 股票代码

    searchText_temp = None

    share_code = None

    ishave_bool = 0

    for i in range(10):

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

    # 基本信息总结输出

    # print("公司简称：" + str(short_name) + "\n")

    # print("会计期间：" + str(fiscal_period) + "\n")

    # print("股票代码：" + str(share_code) + "\n")

    # print("公司名称：" + str(company) + "\n")

    return str(short_name), str(fiscal_period), str(share_code), str(company)


def print_str_to_txt(has_all_table_str, has_short_pay_str, has_plan_pay_str):
    if has_all_table_str:
        # print("有应付职工薪酬列示的表格")

        fileflow.write(has_all_table_str + '\n')
    else:
        # if has_all_table_str == '':
        fileflow.write("没有应付职工薪酬列示的表格" + '\n')

    if has_short_pay_str:
        # print(has_short_pay_str)

        fileflow.write(has_short_pay_str + '\n')
        # if has_short_pay_str == '':
    else:
        fileflow.write("没有短期薪酬列示的表格" + '\n')

    if has_plan_pay_str:
        # print("有提存计划列示的表格")

        fileflow.write(has_plan_pay_str + '\n')
    else:
        # if has_plan_pay_str == '':
        fileflow.write("没有提存计划列示的表格" + '\n')

    fileflow.write("---------------------------------\n")


# 传入当前的current——div，返回值为最终的str

def find_the_table(currnet_div):
    first_td_div = find_first_td_div(currnet_div)

    build_original_table(first_td_div)

    make_the_table(first_td_div)

    return make_the_table(first_td_div)


# 参数为current——td-div，判断是否为 入口 参数，如果不是，继续往下找

def find_first_td_div(current_div):
    first_td_div = None  # 表格第一项的位置

    max_search_range = 20  # 最大查找范围，如果超过这个数仍然找不到表格，则可以认为待查表格不在附近

    div_bool = 0  # 判断表格标题是否为‘c’标签

    if current_div != None:

        current_div_class = current_div['class']

        if (current_div_class)[0] == 'c':
            div_bool = 1

    title_div = current_div

    while current_div and max_search_range != 0:

        # print(current_div.get_text() + "//")

        current_div_class = current_div['class']

        # 找到了表格的入口，又或者是找到了class= t但内容是项目，同样是入口

        if current_div_class[0] == 'c':
            first_td_div = current_div

            break

        if (current_div_class[0] == 't' and len(re.findall(r'项目', current_div.get_text())) > 0):
            first_td_div = current_div

            break

        current_div = find_next_div(current_div)

        max_search_range -= 1

        div_bool = 0

    return first_td_div


# 通过传入 入口 参数， 找出所有的表格，直到出口，输出 original——table

def build_original_table(current_td_div):
    original_table = ''

    begin_tag = 0

    paging_tag = 0

    refinish_tag = 0

    passed_tag = 0

    pre_div = current_td_div

    while current_td_div:

        begin_tag = 1

        # 其中，假如有合计了之后还有汉字，直接break

        if (refinish_tag == 1 and len(re.findall(r'[\u4e00-\u9fa5]+', current_td_div.get_text())) > 0):
            break

        if refinish_tag == 0 and len(re.findall(r'合\s*计|小\s*计', current_td_div.get_text())) > 0:
            refinish_tag = 1

        pre_div_class = pre_div['class']

        current_td_div_class = current_td_div['class']

        # 关键的一步，把表格中的空白项用0表示，只有连续两个class都是C的时候成立

        if current_td_div_class[0] == 'c' and pre_div_class[0] == 'c':  # c表示该项为表格项

            # print("跑过吗 ")

            contend = current_td_div.get_text()

            # if len(re.findall(r'\b\s+\b',contend)) != 0:

            if current_td_div.get_text() == ' ' or current_td_div.get_text() == '' or current_td_div.get_text() == '  ':
                current_td_div.string = '0'

                # 主要的输出来源

                # print(current_td_div)

        original_table += str(current_td_div)

        # if current_td_div_class[0] == 't' and len(re.findall(r''))

        pre_div = current_td_div

        # current_td_div = find_next_div(current_td_div)

        next_div = current_td_div.find_next_sibling('div')

        div_temp = current_td_div

        while next_div is None:
            next_div = div_temp.find_parent('div').find_next_sibling('div')

            div_temp = div_temp.find_parent('div')

        if (next_div['class'])[0] == 'pi' and passed_tag == 0:

            next_page = current_td_div.find_parent('div', class_='pf').find_next_sibling('div', class_='pf')

            if next_page:

                passed_tag = 1

                paging_tag = 1

                next_div_pc = next_page.find('div')

                next_div_set = next_div_pc.find_all('div')

                if not next_div_set[2].find_next_sibling('div'):

                    next_div = next_div_set[2].find_parent('div').find_next_sibling('div')

                else:

                    next_div = next_div_set[2]

        if (next_div['class'])[0] == 'pi' and passed_tag == 1:
            break

        current_td_div = next_div

    return original_table


# first_td_div 判断是否找到表格

# make_the_table 输出original_table，并修改下格式

def make_the_table(first_td_div):
    table2str = ''

    if first_td_div:

        # print('查到表格！')

        # 大标签替换成空格，小标签去掉

        table2str_temp1P = re.compile(r'<[^>]*span[^>]*>', re.S)

        table2str_temp1 = table2str_temp1P.sub('', build_original_table(first_td_div))

        table2str_tempP = re.compile(r'<[^>]+>', re.S)

        table2str = table2str_tempP.sub(' ', table2str_temp1)


    else:

        print('查不到表格！')

        '''


        待补充代码：

        未查找计价货币


        '''

    return table2str


# 无目录的情况下，直接找

def find_the_current_div_else_inEX(html_filename):
    current_div = None

    has_all_table = 0

    has_short_pay_table = 0

    has_plan_pay_table = 0

    has_all_table_str = ''

    has_short_pay_str = ''

    has_plan_pay_str = ''

    soup = BeautifulSoup(open(html_filename, 'rb'), "lxml", from_encoding="utf-8")

    pf = soup.findAll(class_='pf')

    print("进入了没有目录的模式")

    for b in range(int(len(pf) * 0.6), int(len(pf) * 0.9), 1):

        # page_temp = pf[b].find_all('div', class_='t')

        page_temp_pc = pf[b].find('div')

        page_temp = page_temp_pc.find_all('div')

        for temp_div in page_temp:

            has_all_pay_title_len = len(re.findall(r'应付职工薪酬|应付职工薪酬情况|应付职工薪酬列示[：|:]?\b', temp_div.get_text()))

            has_short_pay_title_len = len(re.findall(r"短期薪酬情况|短期薪酬列示[：|:]?\b", temp_div.get_text()))

            has_plan_pay_title_len = len(re.findall(r'提存计划情况|提存计划列示[：|:]?\b', temp_div.get_text()))

            if len(re.findall(r'.*应付职工薪酬列示|应付职工薪酬|应付职工薪酬情况|应付职工薪酬|应付职工薪酬分类\b', temp_div.get_text())) > 0 and has_all_table == 0:
                current_div = temp_div

                has_all_table = 1

                # print(current_div)

                # print('找到应付职工薪酬列示的标题')

                has_all_table_str = find_the_table(current_div)

                continue

            if len(re.findall(r"短期薪酬情况|短期薪酬列示[：|:]?|短期薪酬\b", temp_div.get_text())) > 0 and has_short_pay_table == 0 and has_all_table:
                current_div = temp_div

                # print(current_div)

                # print('找到短期薪酬列示的标题')

                has_short_pay_table = 1

                has_short_pay_str = find_the_table(current_div)

                continue

            if len(re.findall(r'提存计划情况|提存计划列示[：|:]?\b', temp_div.get_text())) > 0 and has_plan_pay_table == 0:
                has_plan_pay_table = 1

                # print('找到提存计划列示的标题')

                # print(current_div)

                current_div = temp_div

                has_plan_pay_str = find_the_table(current_div)

                continue

        if has_all_table and has_short_pay_table and has_plan_pay_table:
            break

        if not (has_all_table and has_short_pay_table and has_plan_pay_table):

            page_temp_pc = pf[b + 1].find('div')

            staff_pay_page_next1_content = page_temp_pc.find_all('div')

            for temp_div in staff_pay_page_next1_content:

                if has_all_table == 0:

                    # print("没有职工薪酬的表格")

                    if len(re.findall(r'.*应付职工薪酬|应付职工薪酬情况|应付职工薪酬列示[：|:]?\b', temp_div.get_text())) > 0:
                        current_div = temp_div

                        has_all_table = 1

                        # print(current_div)

                        # print('找到应付职工薪酬列示的标题')

                        has_all_table_str = find_the_table(current_div)

                if has_short_pay_table == 0:

                    if len(re.findall(r"短期薪酬情况|短期薪酬列示[：|:]?\b", temp_div.get_text())) > 0:
                        current_div = temp_div

                        # print(current_div)

                        # print('找到短期薪酬列示的标题')

                        has_short_pay_table = 1

                        has_short_pay_str = find_the_table(current_div)

                        continue

                if has_plan_pay_table == 0:

                    if len(re.findall(r'提存计划情况|提存计划列示[：|:]?\b', temp_div.get_text())) > 0:
                        has_plan_pay_table = 1

                        # print('找到提存计划列示的标题')

                        # print(current_div)

                        current_div = temp_div

                        has_plan_pay_str = find_the_table(current_div)

                        continue

                if has_all_table and has_short_pay_table and has_plan_pay_table:
                    break

    return has_all_table_str, has_short_pay_str, has_plan_pay_str


# 职工薪酬 staff_pay

def staff_pay_information_extract(html_filename):
    index_div = None

    has_all_table = 0

    has_short_pay_table = 0

    has_plan_pay_table = 0

    has_all_table_str = ''

    has_short_pay_str = ''

    has_plan_pay_str = ''

    soup = BeautifulSoup(open(html_filename, 'rb'), "lxml", from_encoding="utf-8")

    current_div = ''  # 从此处开始查找目标表格

    index_div = soup.find('div', id='outline')  # 目录。如果没有这部分，则直接在页面中查找

    # print(index_div)

    if index_div:

        staff_pay_page = None

        staff_pay_a = index_div.find('a', text=re.compile(r'.*应付职工薪酬\b'))

        if staff_pay_a:

            print("找到目录")

            staff_pay_page_number = staff_pay_a['href'].replace('#', '')

            if staff_pay_page_number:

                staff_pay_page = soup.find('div', id=str(staff_pay_page_number))

                # print(staff_pay_page)

                staff_pay_page_next1 = staff_pay_page.find_next('div', class_='pf')

                # print(staff_pay_page_next1)

                # staff_pay_page_next2 = staff_pay_page_next1.find_next('div',class_= 'pf')

                staff_pay_page_content = soup.find('div', id=str(staff_pay_page_number)).find_all('div', class_='t')

                staff_pay_page_next1_content = staff_pay_page_next1.find_all('div', class_='t')

                # staff_pay_page_next2_content = staff_pay_page_next2.find_all('div', class_='t')

                # 找三个项目，第一页开始找，找三页，找到后，设为current-div

                for temp_div in staff_pay_page_content:

                    has_all_pay_title_len = len(re.findall(r'.*应付职工薪酬|应付职工薪酬情况|应付职工薪酬列示[：|:]?\b', temp_div.get_text()))

                    has_short_pay_title_len = len(re.findall(r"短期薪酬情况|短期薪酬列示[：|:]?\b", temp_div.get_text()))

                    has_plan_pay_title_len = len(re.findall(r'提存计划情况|提存计划列示[：|:]?\b', temp_div.get_text()))

                    if len(re.findall(r'.*应付职工薪酬|应付职工薪酬情况|应付职工薪酬列示[：|:]?\b',
                                      temp_div.get_text())) > 0 and has_all_table == 0:
                        current_div = temp_div

                        has_all_table = 1

                        # print(current_div)

                        # print('找到应付职工薪酬列示的标题')

                        has_all_table_str = find_the_table(current_div)

                        continue

                    if len(re.findall(r"短期薪酬情况|短期薪酬列示[：|:]?\b", temp_div.get_text())) > 0 and has_short_pay_table == 0:
                        current_div = temp_div

                        # print(current_div)

                        # print('找到短期薪酬列示的标题')

                        has_short_pay_table = 1

                        has_short_pay_str = find_the_table(current_div)

                        continue

                    if len(re.findall(r'提存计划情况|提存计划列示[：|:]?\b', temp_div.get_text())) > 0 and has_plan_pay_table == 0:
                        has_plan_pay_table = 1

                        # print('找到提存计划列示的标题')

                        # print(current_div)

                        current_div = temp_div

                        has_plan_pay_str = find_the_table(current_div)

                        continue

                    if has_all_table and has_short_pay_table and has_plan_pay_table:
                        break

                if not (has_all_table and has_short_pay_table and has_plan_pay_table):

                    for temp_div in staff_pay_page_next1_content:

                        if has_all_table == 0:

                            # print("没有职工薪酬的表格")

                            if len(re.findall(r'.*应付职工薪酬|应付职工薪酬情况|应付职工薪酬列示[：|:]?\b', temp_div.get_text())) > 0:
                                current_div = temp_div

                                has_all_table = 1

                                # print(current_div)

                                # print('找到应付职工薪酬列示的标题')

                                has_all_table_str = find_the_table(current_div)

                        if has_short_pay_table == 0:

                            if len(re.findall(r"短期薪酬情况|短期薪酬列示[：|:]?\b", temp_div.get_text())) > 0:
                                current_div = temp_div

                                # print(current_div)

                                # print('找到短期薪酬列示的标题')

                                has_short_pay_table = 1

                                has_short_pay_str = find_the_table(current_div)

                                continue

                        if has_plan_pay_table == 0:

                            if len(re.findall(r'提存计划情况|提存计划列示[：|:]?\b', temp_div.get_text())) > 0:
                                has_plan_pay_table = 1

                                # print('找到提存计划列示的标题')

                                # print(current_div)

                                current_div = temp_div

                                has_plan_pay_str = find_the_table(current_div)

                                continue

                        if has_all_table and has_short_pay_table and has_plan_pay_table:
                            break




        else:  # 没有目录的处理

            print("没有目录！")

            '''


            待补充代码：

            没有目录的处理


            '''

            has_all_table_str, has_short_pay_str, has_plan_pay_str = find_the_current_div_else_inEX(html_filename)


    else:  # 没有目录的处理

        print("没有目录！")

        '''


        待补充代码：

        没有目录的处理


        '''

        has_all_table_str, has_short_pay_str, has_plan_pay_str = find_the_current_div_else_inEX(html_filename)

    return has_all_table_str, has_short_pay_str, has_plan_pay_str


# path = "html/2016/YEAR/"

# inFile = input("读取文件：")

# information_extract(path+inFile)


path = ["test/"]
# path = ["/home/czp/tenyear-html/2015/YEAR/"]
# path = ["/home/czp/tenyear-html/2016/","/home/czp/tenyear-html/2013/YEAR/","/home/czp/tenyear-html/2014/YEAR/","/home/czp/tenyear-html/2015/YEAR/","/home/czp/tenyear-html/2010/YEAR/","/home/czp/tenyear-html/2011/YEAR/","/home/czp/tenyear-html/2012/YEAR/"]

# path = ["html/2011/YEAR/","html/2012/YEAR/","html/2013/YEAR/","html/2014/YEAR/","html/2015/YEAR/","html/2016/YEAR/","html/2010/YEAR/"]
fiscal_period_dict = {"test/": "2016-12-31"}
# fiscal_period_dict = {"/home/czp/tenyear-html/2016/": "2016-12-31", "/home/czp/tenyear-html/2015/YEAR/": "2015-12-31", \
#  \
#                        "/home/czp/tenyear-html/2010/YEAR/": "2010-12-31", \
#  \
#                       "/home/czp/tenyear-html/2011/YEAR/": "2011-12-31", "/home/czp/tenyear-html/2012/YEAR/": "2012-12-31", "/home/czp/tenyear-html/2013/YEAR/": "2013-12-31", \
#  \
#                       "/home/czp/tenyear-html/2014/YEAR/": "2014-12-31"}


def print_base_information_extract(short_name, fiscal_period, share_code, company):
    if share_code == 'None' or share_code != filename[0:pos]:
        share_code = filename[0:pos]

    if fiscal_period == 'None':
        fiscal_period = fiscal_period_dict[path[x]]

    fileflow.write(share_code + "\n" + short_name + "\n" + fiscal_period + "\n" + company + "\n")


# 输出内容

for x in range(len(path)):

    files = os.listdir(path[x])

    if os.path.exists(path[x] + 'payBaseInformation.txt'):
        os.remove(path[x] + 'payBaseInformation.txt')

    fileflow = open(path[x] + 'payBaseInformation.txt', 'a+', encoding='utf-8')

    for filename in files:

        pos = filename.find(".")

        if filename[pos + 1:] == "html":
            print(path[x] + filename + "正在提取...")

            short_name, fiscal_period, share_code, company = base_information_extract(path[x] + filename)

            print_base_information_extract(short_name, fiscal_period, share_code, company)

            # print(short_name,fiscal_period,share_code,company)


            has_all_table_str, has_short_pay_str, has_plan_pay_str = staff_pay_information_extract(path[x] + filename)

            print_str_to_txt(has_all_table_str, has_short_pay_str, has_plan_pay_str)

            print(path[x] + filename + "已提取完成！")

    print(path[x] + "已提取完成！")

    fileflow.close()


