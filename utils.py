import logging, sys, argparse


def str2bool(v):
    # copy from StackOverflow
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_entity(tag_seq, char_seq):
    PER = get_PER_entity(tag_seq, char_seq)
    LOC = get_LOC_entity(tag_seq, char_seq)
    ORG = get_ORG_entity(tag_seq, char_seq)
    return PER, LOC, ORG


def get_PER_entity(tag_seq, char_seq):
    length = len(char_seq)
    PER = []
    flag = 0
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-PER':
            if 'per' in locals().keys():
                PER.append(per)
                del per
                flag = 0
            per = char
            flag = 1
            if i+1 == length:
                PER.append(per)
        if tag == 'I-PER':
            if flag == 0:
                per = ''
                flag = 1
            per += char
            if i+1 == length:
                PER.append(per)
        if tag not in ['I-PER', 'B-PER']:
            if 'per' in locals().keys():
                PER.append(per)
                del per
                flag = 0
            continue
    return PER


def get_LOC_entity(tag_seq, char_seq):
    length = len(char_seq)
    LOC = []
    flag = 0
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-LOC':
            if 'loc' in locals().keys():
                LOC.append(loc)
                del loc
                flag = 0
            loc = char
            flag = 1
            if i+1 == length:
                LOC.append(loc)
        if tag == 'I-LOC':
            if flag == 0:
                loc = ''
                flag = 1
            loc += char
            if i+1 == length:
                LOC.append(loc)
        if tag not in ['I-LOC', 'B-LOC']:
            if 'loc' in locals().keys():
                LOC.append(loc)
                del loc
                flag = 0
            continue
    return LOC


def get_ORG_entity(tag_seq, char_seq):
    length = len(char_seq)
    ORG = []
    flag = 0
    for i, (char, tag) in enumerate(zip(char_seq, tag_seq)):
        if tag == 'B-ORG':
            if 'org' in locals().keys():
                ORG.append(org)
                del org
                flag = 0
            org = char
            flag = 1
            if i+1 == length:
                ORG.append(org)
        if tag == 'I-ORG':
            if flag == 0:
                org = ''
                flag = 1
            org += char
            if i+1 == length:
                ORG.append(org)
        if tag not in ['I-ORG', 'B-ORG']:
            if 'org' in locals().keys():
                ORG.append(org)
                del org
                flag = 0
            continue
    return ORG


def get_logger(filename):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)
    return logger

# 编辑距离算法
# w1 means delete
# w2 means add
# w3 means change
def minEditDist(sm,sn, w1, w2, w3):
    m,n = len(sm)+1,len(sn)+1
    # create a matrix (m*n)
    matrix = [[0]*n for i in range(m)]
    matrix[0][0]=0
    for i in range(1,m):
        matrix[i][0] = matrix[i-1][0] + w1

    for j in range(1,n):
        matrix[0][j] = matrix[0][j-1]+w2

    #cost = 0
    for i in range(1,m):
        for j in range(1,n):
            if sm[i-1]==sn[j-1]:
                cost = 0
            else:
                cost = w3
            matrix[i][j]=min(matrix[i-1][j]+w1, matrix[i][j-1]+w2, matrix[i-1][j-1]+cost)
    return matrix[m-1][n-1]

def get_corelative(str1, str2):
    len1 = len(str1)
    len2 = len(str2)
    #print(len1, len2)
    set1 = set(list(str1))
    set2 = set(list(str2))
    #print(set1, set2)
    len3 = len(set1 & set2)
    #print(len3)
    different = int((1- (len3 + 0.0)/min(len1, len2))*10)
    #print("44444")
    #print(different)
    return different


if __name__ == "__main__":
    print(minEditDist('组织部', '市委组织部', 2, 1, 4))
    print(minEditDist('组织部', '市委组织部', 1, 2, 4))
    print(minEditDist('组织部', '市委组织部', 1, 2, 3))
    differ = get_corelative('中南大学',"中山大学")
    print(minEditDist('abcde', 'abcdf', 1, 1, 1) + 2*get_corelative('abcde', 'abcdf'))
