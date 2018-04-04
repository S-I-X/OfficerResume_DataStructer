#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re


def get_year_pos(mess_text):
    '''
    得到年的位置，用于分成单条履历
    :param mess_text: 分段后的履历
    :return: 该段年位置列表
    '''
    may_all_years = re.findall('\d\d\d\d', mess_text)
    all_years = []
    for year in may_all_years:
        if 1900 < int(year) <= 2018:
            all_years.append(str(year))

    if len(all_years) == 0:
        return

    may_pos = []
    last_pos = 0
    for year_item in all_years:
        pos = mess_text[last_pos:].index(year_item) + last_pos
        may_pos.append(pos)
        last_pos = pos + 1
    year_pos = [may_pos[0]]
    for i in range(1, len(may_pos)):
        if may_pos[i] - may_pos[i - 1] > 12:
            year_pos.append(may_pos[i])
    return year_pos


def get_segments(mess_text, year_pos):
    '''
    根据时间位置，将履历段分成单条履历
    :param mess_text: 履历段
    :param year_pos: 该履历段的年位置列表
    :return:
    '''
    segments = []
    for i in range(len(year_pos) - 1):
        segments.append(mess_text[year_pos[i]: year_pos[i + 1]])
    segments.append(mess_text[year_pos[len(year_pos) - 1]:])
    return segments


def process_segment(segment):
    """
    将单条履历分成：时间和履历内容
    :param segment: 单条履历
    :return: 时间，履历内容
    """
    if segment.find('，') >= 0:
        seg_split = segment.split('，')
        return seg_split[0], seg_split[1]
    else:
        if '日后' in segment:
            mark = segment.index("日后")
            return segment[:mark], segment[mark + 2:]
        elif '月后' in segment:
            mark = segment.index("月后")
            return segment[:mark], segment[mark + 2:]

        elif '日' in segment:
            mark = len(segment) - segment[::-1].index(re.findall('日', segment[::-1])[0])
            return segment[:mark], segment[mark:]
        elif '月' in segment:
            mark = len(segment) - segment[::-1].index(re.findall('月', segment[::-1])[0])
            return segment[:mark], segment[mark:]
        else:
            mark = len(segment) - segment[::-1].index(re.findall('\d', segment[::-1])[0])
            return segment[:mark], segment[mark:]


def process_last_segment(segment):
    '''
    处理最后一条单条履历
    :param segment:　最后一条履历（可能含没有时间划分开的履历部分）
    :return:　时间，履历内容，其他没有时间的履历
    '''
    if segment.find('；') > 0 or segment.find('。') > 0:
        seg_split_pos = segment.find('；')
        if seg_split_pos <= 0:
            seg_split_pos = segment.find('。')
        time, work = process_segment(segment[0: seg_split_pos])
        other_info = segment[seg_split_pos + 1:]
    else:
        time, work = process_segment(segment)
        other_info = ''
    return time, work, other_info


def get_divide_text(mess_text):
    '''
    将原始数据分段，分段依据是括号中的内容为单独一段，括号外的内容合起来为一段
    :paext: 原始履历
    :return: 段落列表
    '''
    pos = []
    right_poi = 0
    left_poi = 0
    while right_poi < len(mess_text) - 1:
        english_left_poi = mess_text[right_poi:].find('(') + right_poi
        chinese_left_poi = mess_text[right_poi:].find('（') + right_poi
        if english_left_poi < right_poi and chinese_left_poi < right_poi:
            break
        else:
            if english_left_poi < right_poi:
                left_poi = chinese_left_poi
            elif chinese_left_poi < right_poi:
                left_poi = english_left_poi
            else:
                left_poi = chinese_left_poi if chinese_left_poi < english_left_poi else english_left_poi

        # 找对应右括号
        right = 0
        for i in range(left_poi + 1, len(mess_text)):
            if mess_text[i] == '）' or mess_text[i] == ')':
                if right == 0:
                    right_poi = i
                    pos.append([left_poi, right_poi])
                    break
                else:
                    right -= 1
            if mess_text[i] == '（' or mess_text[i] == '(':
                right += 1
        if right_poi <= left_poi:
            right_poi = left_poi + 1

    divide_text = []
    for pos_item in pos:
        divide_text.append(mess_text[pos_item[0] + 1:pos_item[1]])

    base = 0
    for pos_item in pos:
        left = pos_item[0] - base
        right = pos_item[1] - base
        mess_text = mess_text[0:left] + mess_text[right + 1:]
        base += right - left + 1
    divide_text.append(mess_text)

    return divide_text


def process_introduce(mess_text):
    '''
    :param mess_text: 原始履历
    :return: 时间-单条履历列表
    '''
    divide_text = get_divide_text(mess_text)  # 把括号中的内容提出来

    segments = []
    for item in divide_text:
        year_pos = get_year_pos(item)
        if year_pos is None:
            continue
        part_segments = get_segments(item, year_pos)
        segments += part_segments

    time_and_work = []
    if len(segments) == 0:
        return
    for i in range(len(segments) - 1):
        time, work = process_segment(segments[i])
        time_and_work.append([time, work])
    last_time, last_work, other_info = process_last_segment(segments[-1])
    time_and_work.append([last_time, last_work])
    time_and_work.append(['', other_info]) if len(other_info) > 0 else ''

    return time_and_work


if __name__ == "__main__":
    text = '19４９年１月西海工商局税务科审计员；１９４９年１月-１９５５年３月省财政厅和税务局办事员、科员；１９５５年３月'
    structural_data = process_introduce(text)
    if structural_data is not None:
        for item in structural_data:
            print(item)
