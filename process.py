from Structer import Structer
from Mapping import Mapping_data
import csv
from process_introduce import process_introduce
import re

def process():

    relativ_data = Mapping_data()
    relativ_data.init_site_data()
    relativ_data.init_loc_data()

    stucter = Structer()

    print('start..')
    sv_reader = csv.reader(open('relative_data/data_from_db.csv', encoding='gbk'))

    out = open('relative_data/data_from_db_structed_ai.csv', 'w', newline='')
    csv_writer = csv.writer(out, dialect='excel')

    out1 = open('relative_data/dirty_data_from_db_structed_ai.csv', 'w', newline='')
    csv_writer1 = csv.writer(out1, dialect='excel')

    # 人工职位库表
    #work_list = data_structe.get_list('../data/work.txt')
    # 代码生成职位库
    work_list = relativ_data.loc_data

    for row in sv_reader:
        # print(row)
        if len(row) == 0:
            continue
        if row[0] == '':
            continue

        print(row)
        structural_data = process_introduce(row[0])

        if structural_data is not None:
            for item in structural_data:
                process_one_item(item, relativ_data, stucter, csv_writer, csv_writer1)
                #struct(item, work_list, csv_writer, csv_writer1)


        # lines = info.split('\n')
        # for item in lines:
        #    if item == '':
        #        continue
        #    data_structe.get_info(row[0], item, work_list, csv_writer)

    out.close()
    out1.close()
    stucter.close()


def process_one_item(item, data_class, structer, csv_w, dir_csv_w):
    time = structer.get_time(item[0])
    data = item[1]
    loc_map = data_class.loc_mapping

    # 此处预处理，将句子分成多个履历原句
    # data = data_structe.delete(data, '\(.*\)?|\(.*\）?|\（.*\）?')
    # data = data_structe.delete(data, '加入|曾前后|当选|被聘为|在|担任|调任|曾任|作为|历任|先后任|任聘|\+|\-|\?')
    data = re.sub('兼', ',', data)
    data_list = re.split('、|，|,', data)

    # 使用old_ 系列来记录旧的记录，方便下延
    # old_time = -1
    old_loc = -1
    old_work = -1
    old_dep = -1
    for data_item in data_list:
        loc = -1
        org = -1

        # 淘汰没用的信息
        if data_item == '' or data_item == ' ':
            continue
        print(data_item)
        #直接使用模型抽取地名和组织结构名
        loc_list, org_list = structer.get_long_org(data_item)
        #使用字典抽取职位
        work = structer.get_site(data_item)
        #一旦模型抽取不出地名，使用预先生成的字典抽取
        # 最后将地名并标准化
        if len(loc_list) == 0:
            loc = structer.get_loc(data_item)
        else:
            loc = loc_list[0]
            if loc in loc_map.keys():
                loc = loc_map[loc]
        '''
        if len(site_list) == 0:
            dir_csv_w.writerow([data_item, time, loc, site_list, work])
            continue
        elif not work:
            dir_csv_w.writerow([data_item, time, loc, site_list, work])
            continue
        else:
        '''
        #如果这一句里面没有地名，那么可能是是 上海市书记，副省长这种，使用上一地名即可
        if  loc == -1 and old_loc != -1:
            loc = old_loc

        #判断部门有没有抽取到，没有的话，可能是：
        # 1. 上海市书记，副省长
        # 2. 上海市省长
        # 3. 真的没有
        if len(org_list) > 0:
            org = org_list[0]
            #解决模型把教师也放进部门的问题
            if len(org) > 2 and org[-2] == '教' and org[-1] == '师':
                org = org[:-2]
            #解决抽取模型把总工程师误认为是部门的问题
            if org == '总工程师':
                org = -1
        else:
            if old_dep != -1 and work != -1:
                org = old_dep
            #解决模型不能识别人民政府的问题
            if loc != -1 and work != -1 and work in data_class.special_people:
                org = '人民政府'
            '''
            if old_dep != -1 and work != -1:
                org = old_dep
            else :
                org = None
            '''

        org = structer.standard_org(loc, org)
        if org != -1:
            old_dep = org
        if loc != -1:
            old_loc = loc
        old_work = work

        if time != -1 and org != -1 and work != -1:
            print([data_item, time, loc, org, work])
            csv_w.writerow([data_item, time, loc, org, work])
        else:
            dir_csv_w.writerow([data_item, time, loc, org, work])









if __name__ == "__main__":
    process()