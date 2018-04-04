import csv

class Mapping_data:
    site_data = []
    loc_data = []

    #机构为二维数组，0 代表国家机构， 1 代表 企业， 2代表学校
    org_data = [[], [], []]

    site_mapping = {}
    loc_mapping = {}
    org_mapping = {}

    site_to_id = {}
    loc_to_id = {}
    org_to_id = {}

    #这里添加一种数据为了人工识别人民政府
    special_people = ['省长','副省长','省长助理','市长','副市长','市长助理','区长','副区长','区长助理','镇长','副镇长',
                      '镇长助理','乡长','副乡长','县长','副县长','州长','副州长','秘书长','副秘书长']

    def __init__(self):
        pass

    def init_site_data(self):
        for line in open('relative_data/more_work.txt', encoding='UTF-8'):
            line = line.split('\n')[0]
            self.site_data.append(line)

    def init_loc_data(self):

        temp_list = []

        self.loc_data.append('天津河北')
        self.loc_data.append('天津市河北区')

        self.loc_mapping['天津河北'] = '天津市河北区'
        self.loc_mapping['天津市河北区'] = '天津市河北区'

        with open('D:\projects\OfficerDataProcess\dict_data\地名.csv', 'r', encoding='utf_8') as my_csv_file:
            lines = csv.reader(my_csv_file)
            for item in lines:
                if item[0] == '天津市河北区':
                    continue

                # city_long_dict[]
                self.loc_data.append(item[0])
                self.loc_mapping[item[0]] = item[0]

                name1 = item[0].split('市')
                # print(name1)
                if len(name1) > 1 and name1[-1] != '':
                    new_name = name1[-1][:-1]
                    if len(new_name) > 1:
                        self.loc_data.append(name1[0] + new_name)
                        self.loc_mapping[name1[0] + new_name] = item[0]

                        #self.loc_data.append(new_name)
                        temp_list.append(new_name)
                        self.loc_mapping[new_name] = item[0]

                else:
                    if name1[0][-1] == '省' or name1[0][-1] == '市':
                        new_name = name1[0][:-1]
                    else:
                        new_name = name1[0]

                    if len(new_name) > 1:
                        #self.loc_data.append(new_name)
                        temp_list.append(new_name)
                        self.loc_mapping[new_name] = item[0]

        self.loc_data.extend(temp_list)

    def init_org(self):
        #初始化政府机构
        for line in open('relative_data/政府机构大全.txt', encoding='UTF-8'):
            line = line.split('\n')[0]
            self.org_data[0].append(line)

        for line in open('relative_data/企业名录.txt', encoding='UTF-8'):
            line = line.split('\n')[0]
            self.org_data[1].append(line)

        for line in open('relative_data/院校大全.txt', encoding='UTF-8'):
            line = line.split('\n')[0]
            self.org_data[2].append(line)


if __name__ == "__main__":
    data = Mapping_data()
    data.init_loc_data()
    print(data.loc_data)
    print(data.loc_mapping)
