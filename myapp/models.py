import pandas as pd
import os
import pickle
import re

# Create your models here.

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def time_to_int(time_str):
    time_split = time_str.split(':')
    hour = int(time_split[0])
    minute = int(time_split[1])
    hour += round(minute / 60, 2)
    return hour


def predict_data(file_path):
    with open(os.path.dirname(os.path.abspath(__file__)) + '/models/explanatory_clm.pickle', 'rb') as f:
        explanatory_clm = pickle.load(f)

    with open(os.path.dirname(os.path.abspath(__file__)) + '/models/str_clm.pickle', 'rb') as f:
        str_clm = pickle.load(f)

    with open(os.path.dirname(os.path.abspath(__file__)) + '/models/key_phrase.pickle', 'rb') as f:
        key_phrase = pickle.load(f)

    with open(os.path.dirname(os.path.abspath(__file__)) + '/models/frequency_clm.pickle', 'rb') as f:
        frequency_clm = pickle.load(f)

    with open(os.path.dirname(os.path.abspath(__file__)) + '/models/frequencys.pickle', 'rb') as f:
        frequencys = pickle.load(f)

    with open(os.path.dirname(os.path.abspath(__file__)) + '/models/oe1.pickle', 'rb') as f:
        oe1 = pickle.load(f)

    with open(os.path.dirname(os.path.abspath(__file__)) + '/models/oe2.pickle', 'rb') as f:
        oe2 = pickle.load(f)

    with open(os.path.dirname(os.path.abspath(__file__)) + '/models/final_clm.pickle', 'rb') as f:
        final_clm = pickle.load(f)

    with open(os.path.dirname(os.path.abspath(__file__)) + '/models/model.pickle', 'rb') as f:
        model = pickle.load(f)

    test_data = pd.read_csv(file_path, encoding="utf-8")
    job_num = pd.DataFrame(data=test_data['お仕事No.'], columns=['お仕事No.'])

    test_data = test_data[explanatory_clm]

    lack_sum = test_data.isnull().sum(axis=1)
    test_data["欠損値の合計数"] = lack_sum

    for i in range(len(test_data)):
        limited_salary = test_data['給与/交通費　給与上限'][i]
        if not pd.isnull(limited_salary):
            test_data['給与/交通費　給与上限'][i] = 1
        else:
            test_data['給与/交通費　給与上限'][i] = 0

    address = []
    for i in range(len(test_data)):
        adr = str(test_data['勤務地\u3000都道府県コード'][i]) + str(test_data['勤務地\u3000市区町村コード'][i])
        address.append(int(adr))
    test_data = test_data.drop(columns=['勤務地\u3000市区町村コード'])
    test_data['address_code'] = address

    test_data['掲載期間　開始日'] = pd.to_datetime(test_data['掲載期間　開始日'], format='%Y/%m/%d')
    test_data['掲載期間　開始日'] = test_data['掲載期間　開始日'].dt.month

    test_data['期間・時間　勤務開始日'] = pd.to_datetime(test_data['期間・時間　勤務開始日'], format='%Y/%m/%d')
    test_data['期間・時間　勤務開始日'] = test_data['期間・時間　勤務開始日'].dt.month

    a = []
    regex = re.compile('\d+')
    for i in range(len(test_data)):
        str1 = test_data['給与/交通費\u3000備考'][i]
        if pd.isnull(str1) == False and str1[1] + str1[2] + str1[3] == '月収例':
            match = regex.findall(str1)
            num = int(match[0]) / 10
            a.append(num)
        else:
            a.append(None)
    test_data['月収例'] = a

    st = []
    fin = []
    dts = []
    test_data['期間・時間\u3000勤務時間'] = test_data['期間・時間\u3000勤務時間']
    for i in range(len(test_data)):
        time_str = test_data['期間・時間\u3000勤務時間'][i].split('<BR>')
        time = time_str[0].split('〜')
        start_time = time_to_int(time[0])
        finish_time = time_to_int(time[1])
        st.append(start_time)
        fin.append(finish_time)
        if start_time >= finish_time:
            dt = 24 - (start_time - finish_time)
        else:
            dt = finish_time - start_time
        dts.append(dt)
    test_data['勤務開始時間'] = st
    test_data['勤務終了時間'] = fin
    test_data['勤務開始から終了時間までの時間'] = dts

    for clm in str_clm:
        a = []
        for i in range(len(test_data)):
            if not pd.isnull(test_data[clm][i]):
                a.append(1)
            else:
                a.append(0)
        test_data[clm] = a

    a = []
    for i in range(len(test_data)):
        if test_data['派遣会社のうれしい特典'][i] == key_phrase:
            a.append(1)
        else:
            a.append(0)
    test_data['派遣会社のうれしい特典'] = a

    test_data['勤務地\u3000最寄駅1（駅からの交通手段）'] = test_data['勤務地\u3000最寄駅1（駅からの交通手段）'].fillna(0).astype(int)

    for clm in frequency_clm:
        a = []
        for i in range(len(test_data)):
            bool_clm = test_data.at[test_data.index[i], clm] in frequencys[clm]
            if bool_clm:
                a.append(frequencys[clm][test_data.at[test_data.index[i], clm]])
            else:
                a.append(0)
        new_clm = '頻度（' + clm + '）'
        test_data[new_clm] = a

    cate_col_ordinal = ['職種コード', '会社概要　業界コード']
    oe_df_test_data = oe1.transform(test_data[cate_col_ordinal])
    test_data.drop(columns=cate_col_ordinal, inplace=True)
    test_data = pd.concat([test_data, oe_df_test_data], axis=1)

    cate_col_ordinal = ['拠点番号', 'address_code', '勤務地　最寄駅1（沿線名）']
    oe_df_test_data = oe2.transform(test_data[cate_col_ordinal])
    test_data.drop(columns=cate_col_ordinal, inplace=True)
    test_data = pd.concat([test_data, oe_df_test_data], axis=1)

    test_data = test_data[final_clm]

    result = model.predict(test_data)

    job_num['応募数 合計'] = result
    job_num.to_csv(CURRENT_DIR + '/uploads/result.csv', encoding='utf-8', index=False)

    os.remove(file_path)
