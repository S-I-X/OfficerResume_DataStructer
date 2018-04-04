import tensorflow as tf
import numpy as np
import os, argparse, time, random
from model import BiLSTM_CRF
from utils import str2bool, get_logger, get_entity, minEditDist, get_corelative
from data import read_corpus, read_dictionary, tag2label, random_embedding
from Mapping import Mapping_data
import re
import csv
import db_operator


class Arg:
    train_data = 'data_path'
    test_data = 'data_path'
    batch_size = 64
    epoch = 40
    hidden_dim = 300
    optimizer = 'Adam'
    CRF = True,
    lr = 0.001
    clip = 5.0
    dropout = 0.5
    update_embedding = True
    pretrain_embedding = 'random'
    embedding_dim = 300
    shuffle = True
    mode = 'demo'
    demo_model = '1521112368'
    #map_data = Mapping_data()


    def __init__(self):
        pass
        '''
        train_data='data_path'
        test_data='data_path'
        batch_size=64
        epoch=40
        hidden_dim=300
        optimizer='Adam'
        CRF=True,
        lr=0.001
        clip=5.0
        dropout=0.5
        update_embedding=True
        pretrain_embedding='random'
        embedding_dim=300
        shuffle=True
        mode='demo'
        demo_model='1521112368'
        '''

class Structer:
    model = None
    args = Arg()
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # default: 0
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    config.gpu_options.per_process_gpu_memory_fraction = 0.2  # need ~700MB GPU memory
    saver = None
    ckpt_file = None
    map_data = Mapping_data()

    def __init__(self):

        # os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        # os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # default: 0
        # config = tf.ConfigProto()
        # config.gpu_options.allow_growth = True
        # config.gpu_options.per_process_gpu_memory_fraction = 0.2  # need ~700MB GPU memory

        #args = Arg()
        word2id = read_dictionary(os.path.join('.', self.args.train_data, 'word2id.pkl'))
        if self.args.pretrain_embedding == 'random':
            embeddings = random_embedding(word2id, self.args.embedding_dim)
        else:
            embedding_path = 'pretrain_embedding.npy'
            embeddings = np.array(np.load(embedding_path), dtype='float32')

        paths = {}
        timestamp = str(int(time.time())) if self.args.mode == 'train' else self.args.demo_model
        output_path = os.path.join('.', self.args.train_data + "_save", timestamp)
        if not os.path.exists(output_path): os.makedirs(output_path)
        summary_path = os.path.join(output_path, "summaries")
        paths['summary_path'] = summary_path
        if not os.path.exists(summary_path): os.makedirs(summary_path)
        model_path = os.path.join(output_path, "checkpoints/")
        if not os.path.exists(model_path): os.makedirs(model_path)
        self.ckpt_prefix = os.path.join(model_path, "model")
        paths['model_path'] = self.ckpt_prefix
        result_path = os.path.join(output_path, "results")
        paths['result_path'] = result_path
        if not os.path.exists(result_path): os.makedirs(result_path)
        log_path = os.path.join(result_path, "log.txt")
        paths['log_path'] = log_path
        #get_logger(log_path).info(str(args))

        self.ckpt_file = tf.train.latest_checkpoint(model_path)
        print(self.ckpt_file)
        paths['model_path'] = self.ckpt_file
        self.model = BiLSTM_CRF(self.args, embeddings, tag2label, word2id, paths, config=self.config)
        self.model.build_graph()
        self.saver = tf.train.Saver()

        self.sess = tf.Session(config=self.config)
        self.saver.restore(self.sess, self.ckpt_file)

        self.map_data.init_loc_data()
        self.map_data.init_site_data()
        self.map_data.init_org()

    def close(self):
        self.sess.close()

    def get_long_org(self, str):
        demo_sent = list(str.strip())
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        tag = self.model.demo_one(self.sess, demo_data)
        PER, LOC, ORG = get_entity(tag, demo_sent)
        #print('PER: {}\nLOC: {}\nORG: {}'.format(PER, LOC, ORG))
        #print('this is loc', LOC)
        #print('this is org', ORG)
        return LOC, ORG

    def get_org(self):
        with tf.Session(config=self.config) as sess:
            print('============= demo =============')
            print('sdfsdfsdfsd...............',self.ckpt_file)
            self.saver.restore(sess, self.ckpt_file)
            while (1):
                print('Please input your sentence:')
                demo_sent = input()
                if demo_sent == '' or demo_sent.isspace():
                    print('See you next time!')
                    break
                else:
                    demo_sent = list(demo_sent.strip())
                    demo_data = [(demo_sent, ['O'] * len(demo_sent))]
                    tag = self.model.demo_one(sess, demo_data)
                    PER, LOC, ORG = get_entity(tag, demo_sent)
                    print('this is loc', LOC)
                    print('this is org', ORG)
                    #print('PER: {}\nLOC: {}\nORG: {}'.format(PER, LOC, ORG))
                    #return LOC, ORG


    def get_loc(self, str):
        loc_list = self.map_data.loc_data
        loc_map = self.map_data.loc_mapping
        for item in loc_list:
            if str.find(item) > -1:
                return loc_map[item]
        return -1

    def get_site(self, str):
        list = self.map_data.site_data
        for item in list:
            if str.find(item) > -1:
                return item
        return -1

    def get_time(self, data):
        searchObj = re.search(r'(\d{4}\.\d{1,2}(--)?(——)?—?-?-?－?至?)+|'
                              r'(\d{4}年\d{1,2}月(--)?(——)?—?-?-?－?至?)+|'
                              r'(\d{4}年?(--)?(——)?—?-?-?－?至?)+', data, re.M | re.I)
        if searchObj == None:
            return data
        time = searchObj.group()

        time = re.sub(r'月', '', time)
        time = re.sub(r'年', '.', time)
        time = re.sub(r'－－|－|——|--|—|－|至', '-', time)
        if time[-1] == '-':
            time = time[:-1]
        return time


    def standard_loc(self, str):
        pass

    def standard_org(self,words, loc, str, con, cur, csv):
        if str == -1:
            return  str
        #flag 用于判断是属于公司，政府机构， 还是 学校,默认政府机构
        # 0 代表 政府机构； 1 代表 公司  2 代表 学校
        flag = 0
        school_list  = ['学校', '党校', '师专', '中学', '小学', '研究院', '学院', '大学']
        company_list = ['公司','企业','厂','协会','学会', '集团']

        for item in school_list:
            pos = str.find(item)
            if pos > -1:
                flag = 2
                old_str = str
                str = str[:pos] + item
                #print('this is a school',old_str, str)
                break
        if flag == 0:
            for item in company_list:
                pos = str.find(item)
                if pos > -1:
                    flag = 1
                    old_str = str
                    str = str[:pos] + item
                    #print('this is a company',old_str, str)
                    break

        if flag > 0:
            return str
        #
        #处理str
        min_different = 1000
        likely_str = ''

        always_org = ['村委', '镇委', '区委', '县委', '市委', '省委', '州委']


        org_list = db_operator.get_org_list(loc, cur)
        #print(org_list)

        for item in org_list:
            differ = minEditDist(str, item, 1, 2, 3) + get_corelative(str, item)
            # if len(str) < len(item):
            #     differ = minEditDist(str, item, 1, 2, 4) + get_corelative(str, item)
            # elif len(str) == len(item):
            #     differ = minEditDist(str, item, 1, 1, 4) + get_corelative(str, item)
            # else:
            #     differ = minEditDist(str, item, 2, 1, 4) + get_corelative(str, item)

            if differ < min_different:
                min_different = differ
                likely_str = item

        if min_different <= min(abs(len(str) - len(likely_str)), len(likely_str)):
            if str != likely_str and likely_str + '党组' != str and likely_str + '党委' != str :
                rig = 1
                for item in always_org:
                    if likely_str.find(item) > -1 and str.find(item) == -1:
                        rig = -1
                        break
                if rig == 1:
                    print(words, '----------------------------->', loc, min_different, str, '---->', likely_str)
                    csv.writerow([words, loc, min_different, str, likely_str])
                #print(str, '--------------------->', likely_str)
            str = likely_str
        else:
            if str.find('市委') == -1 and str.find('省委') == -1 and len(str) > 1:
                db_operator.set_org_to_map(loc, str, con, cur)
        return str


        # for item in self.map_data.org_data[flag]:
        #     if len(str) < len(item):
        #         differ = minEditDist(str, item, 1, 2, 4) + 2 * get_corelative(str, item)
        #     elif len(str) == len(item):
        #         differ = minEditDist(str, item, 1, 1, 4) + 2 * get_corelative(str, item)
        #     else:
        #         differ = minEditDist(str, item, 2, 1, 4) + 2 * get_corelative(str, item)
        #
        #     if differ < min_different:
        #         min_different = differ
        #         likely_str = item
        #
        # if min_different < min(len(str), 4):
        #     if str != likely_str:
        #         print(str, '---------->', likely_str)
        #         csv_w.writerow([str, likely_str])
        # else:
        #     self.map_data.org_data[flag].append(str)


if __name__=="__main__":

    st = Structer()
    dict = {}

    out = open('relative_data/org_standard_data_ai.csv', 'w', newline='')
    csv_writer = csv.writer(out, dialect='excel')

    con, cur = db_operator.get_con_cur()

    with open('relative_data/data_from_db_structed_ai.csv', 'r', encoding='gbk') as my_csv_file:
        lines = csv.reader(my_csv_file)
        for line in lines:
            words = line[0]
            loc = line[2]
            org = line[3]
            st.standard_org(words, loc, org, con, cur, csv_writer)
    db_operator.db_close(con, cur)
    #         if org in dict.keys():
    #             dict[org] = dict[org] +1
    #         else:
    #             dict[org] = 1
    #
    # new_list = sorted(dict.items(), key=lambda d:d[1], reverse= True)
    # for i in range(300):
    #     print(new_list[i][0])
    #print(new_list[:10])
            #print(org)

    #st.get_org()
    #loc, org = st.get_long_org("小明任广州市委书记")
    # print(st.get_time('1983年09月至1988年09月在北极'))
    # print(st.get_time('1983年09月至在北极'))
    # print(st.get_time('1999-2002年博罗县委副书记2002-2003年博罗县委书记2003-2003'))
    # print(st.get_time('2012.01——2016.04'))
    # print(st.get_time('1996.12—1997.09'))
    # print(st.get_time(''))
    #print(loc, org)
    out.close()
    st.close()


