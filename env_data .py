import os
import numpy as np
import shutil
import cv2
import pandas as pd
import datetime
import math

'''
{year_tyname:{date:{wind:Float,intensity_class:onehot,move_velocity:float,month:onehot,location:matrix or(locx,locy),
                    history_direction12:onehot, history_direction24:onehot,future_direction24:onehot,
                    history_inte_change24:onehot, future_inte_change24:onehot}}}
'''


def get_intensity(wind):
    '''
    :param wind: float
    :return: intensity_class[0:10.8-17.1, 1:17.1-24.4, 2:24.4-32.6, 3:32.6-41.4, 4:41.4-50.9, 5:>50.9]
    '''
    intensity_class = 0
    if wind< 17.1:
        intensity_class=0
    elif wind>=17.1 and wind<24.4:
        intensity_class = 1
    elif wind>=24.4 and wind<32.6:
        intensity_class = 2
    elif wind>=32.6 and wind<41.4:
        intensity_class = 3
    elif wind>=41.4 and wind<50.9:
        intensity_class = 4
    elif wind>=50.9:
        intensity_class = 5
    intensity_onehot = np.zeros(6)
    intensity_onehot[intensity_class] = 1
    return intensity_onehot

def get_velocity(LONG,LAT):
    '''
    get moving velocity
    :param LONG: [last_float,now_float]
    :param LAT: [last_float,now_float]
    :return: velocity float
    '''

    Long_rel = LONG[1] - LONG[0]
    Lat_rel = LAT[1] - LAT[0]
    Long_distance = (Long_rel/10)*111 * math.cos((LAT[0]+LAT[1])/2/10*np.pi/180)
    Lat_distance = Lat_rel/10*111
    velocity = np.sqrt(Long_distance**2+Lat_distance**2)
    return velocity

def get_location(long,lat):
    '''
    80-200,0-60xxxxxx

    :param LONG: [Long_float]
    :param LAT: [Long_float]
    :return: location numpy_6*12
    '''
    x = int((long//10-80)//10)
    y = int(lat//100)
    if x < 0:
        x =0
    elif x > 11:
        x =11

    if y < 0:
        y =0
    elif y > 5:
        y =5

    location_x = np.zeros(12)
    location_y = np.zeros(6)
    location_x[x] = 1
    location_y[y] = 1

    return location_x,location_y

def get_location_for_all(long,lat):
    '''
    80-200,0-60xxxxxx

    0-360,-60-60

    :param LONG: [Long_float]
    :param LAT: [Long_float]
    :return: location numpy_6*12
    '''
    x = int((long//10)//10)
    y = int((lat+600)//100)
    if x < 0:
        x =0
    elif x > 35:
        x =35

    if y < 0:
        y =0
    elif y > 11:
        y =11

    location_x = np.zeros(36)
    location_y = np.zeros(12)
    location_x[x] = 1
    location_y[y] = 1

    return location_x,location_y

def get_direction(LONG,LAT):
    '''
    get moving direction
    :param LONG: [first_float,...,last_float]
    :param LAT: [first_float,...,last_float]
    :return: direction 8类
    '''
    LONG = list(LONG)
    LAT = list(LAT)
    Long_rel = LONG[-1] - LONG[0]
    Lat_rel = LAT[-1] - LAT[0]
    Long_distance = (Long_rel / 10) * 111 * math.cos((LAT[0] + LAT[1]) / 2 / 10 * np.pi / 180)   #x
    Lat_distance = Lat_rel / 10 * 111      #y
    velocity = np.sqrt(Long_distance ** 2 + Lat_distance ** 2)
    if velocity == 0:
        return np.array([1,0,0,0,0,0,0,0])
    sin_angle = Lat_distance/velocity
    cos_angle = Long_distance/velocity
    if sin_angle>=0 and cos_angle>=0:
        angle = math.asin(sin_angle)
    elif sin_angle>=0 and cos_angle<=0:
        angle = np.pi-math.asin(sin_angle)
    elif sin_angle<=0 and cos_angle<=0:
        angle = np.pi-math.asin(sin_angle)
    elif sin_angle<=0 and cos_angle>=0:
        angle = 2*np.pi + math.asin(sin_angle)
    else:
        print(sin_angle,cos_angle)
    if angle < 0 or angle >2*np.pi:
        print(angle)
        exit()

    angleList = [(np.pi * (1 / 8), 2 * np.pi - np.pi * (1 / 8)),
                 (2 * np.pi - np.pi * (1 / 8), 2 * np.pi - np.pi * (3 / 8)),
                 (2 * np.pi - np.pi * (3 / 8), 2 * np.pi - np.pi * (5 / 8)),
                 (2 * np.pi - np.pi * (5 / 8), 2 * np.pi - np.pi * (7 / 8)),
                 (2 * np.pi - np.pi * (7 / 8), 2 * np.pi - np.pi * (9 / 8)),
                 (2 * np.pi - np.pi * (9 / 8), 2 * np.pi - np.pi * (11 / 8)),
                 (2 * np.pi - np.pi * (11 / 8), 2 * np.pi - np.pi * (13 / 8)),
                 (2 * np.pi - np.pi * (13 / 8), 2 * np.pi - np.pi * (15 / 8))]
    angleClass = 0
    for classid, anclass in enumerate(angleList):
        if classid == 0:
            if angle > anclass[1] or angle <= anclass[0]:
                angleClass=classid
                break
        else:
            if angle > anclass[1] and angle < anclass[0]:
                angleClass=classid
                break
    class_onehot = np.zeros((8))
    class_onehot[angleClass] = 1
    return class_onehot

def get_inten_change(WND):
    '''
    :param WND:
    :return: 4类
    '''
    WND = list(WND)
    grad = []
    for i in range(len(WND) - 1):
        grad.append(WND[i + 1] - WND[i])
    if (np.array(grad) == 0).all():
        InteClass = 3
    elif (np.array(grad) >= 0).all():
        InteClass = 0
    elif (np.array(grad) <= 0).all():
        InteClass = 2
    elif grad[np.nonzero(np.array(grad))[0][0]] > 0 and grad[np.nonzero(np.array(grad))[0][-1]] < 0:
        InteClass = 1
    else:
        if np.sum(np.array(grad)) > 0:
            InteClass = 0
        elif np.sum(np.array(grad)) < 0:
            InteClass = 2
        elif np.sum(np.array(grad)) == 0:
            InteClass = 3
    class_onehot = np.zeros((4))
    class_onehot[InteClass] = 1
    return class_onehot


def get_env_from_informer():
    saveroot = r'G:\data\evn_data\all_area_correct_location_includeunder15_2023'
    root = r'G:\data\informer_dataset\TY_BST_ALL_area_2023'
    area_list = os.listdir(root)
    area_ = ['EP','NA','NI','SI','SP','WP']
    for area in area_list:
        if area == 'SA':
            continue
        area_path = os.path.join(root, area)
        year_list = os.listdir(area_path)
    # year_list = os.listdir(root)
        evn = {}
        wind_list = []
        move_list = []
        for year in year_list:
            # if year != '2019':
            #     continue
            year_path = os.path.join(root,area,year)
            ty_list = os.listdir(year_path)
            for ty in ty_list:
                year = ty.split('.')[0][2:6]
                tyname = ty.split('.')[0][9:]
                year_ty_key = year+'_'+tyname
                evn[year_ty_key] = {}
                ty_path = os.path.join(year_path,ty)
                print(ty_path)
                excel_data = pd.read_excel(ty_path)
                for data_i, date in enumerate(list(excel_data['date'])):
                    time1 = datetime.datetime.strptime(date, '%Y/%m/%d %H:%M:%S')
                    date_key = time1.strftime('%Y%m%d%H')
                    evn[year_ty_key][date_key] = {}

                    area_onehot = np.zeros(6)
                    area_onehot[[i for i,x in enumerate(area_) if x == area][0]] = 1
                    evn[year_ty_key][date_key]['area'] =area_onehot

                    evn[year_ty_key][date_key]['wind'] = excel_data['WND'][data_i]/110
                    wind_list.append(evn[year_ty_key][date_key]['wind'])
                    evn[year_ty_key][date_key]['intensity_class'] = get_intensity(excel_data['WND'][data_i])
                    if data_i == 0:
                        evn[year_ty_key][date_key]['move_velocity'] = 0
                    else:
                        evn[year_ty_key][date_key]['move_velocity'] = get_velocity(list(excel_data['LONG'][data_i-1:data_i+1]),
                                                                                           list(excel_data['LAT'][data_i-1:data_i+1]))/1219.8387650082498
                        move_list.append(evn[year_ty_key][date_key]['move_velocity'])
                    month_onehot = np.zeros(12)
                    month_onehot[int(date_key[4:6])-1] = 1
                    evn[year_ty_key][date_key]['month'] = month_onehot
                    location_long,location_lat = get_location_for_all(excel_data['LONG'][data_i],
                                                                                  excel_data['LAT'][data_i])
                    evn[year_ty_key][date_key]['location'] = (excel_data['LONG'][data_i],excel_data['LAT'][data_i])
                    evn[year_ty_key][date_key]['location_long'] = location_long
                    evn[year_ty_key][date_key]['location_lat'] = location_lat

                    # direction change class
                    if data_i-2 <0:
                        evn[year_ty_key][date_key]['history_direction12'] = -1
                    else:
                        evn[year_ty_key][date_key]['history_direction12'] = get_direction(excel_data['LONG'][data_i-2:data_i+1],
                                                                          excel_data['LAT'][data_i-2:data_i+1])
                    if data_i - 4 < 0:
                        evn[year_ty_key][date_key]['history_direction24'] =-1
                    else:
                        evn[year_ty_key][date_key]['history_direction24'] = get_direction(excel_data['LONG'][data_i-4:data_i+1],
                                                                          excel_data['LAT'][data_i-4:data_i+1])
                    if data_i+5 > excel_data.shape[0]:
                        evn[year_ty_key][date_key]['future_direction24'] = -1
                    else:
                        evn[year_ty_key][date_key]['future_direction24'] = np.argmax(get_direction(excel_data['LONG'][data_i:data_i+5],
                                                                          excel_data['LAT'][data_i:data_i+5]))
                    # intensity change class
                    if data_i - 4 < 0:
                        evn[year_ty_key][date_key]['history_inte_change24'] =-1
                    else:
                        evn[year_ty_key][date_key]['history_inte_change24'] = get_inten_change(excel_data['WND'][data_i-4:data_i+1])
                    if data_i+5 > excel_data.shape[0]:
                        evn[year_ty_key][date_key]['future_inte_change24'] = -1
                    else:
                        evn[year_ty_key][date_key]['future_inte_change24'] = np.argmax(get_inten_change(excel_data['WND'][data_i:data_i+5]))
                    save_path = os.path.join(saveroot,area,year,tyname)
                    os.makedirs(save_path,exist_ok=True)
                    np.save( os.path.join(save_path,date_key+'.npy'),evn[year_ty_key][date_key])
    wind_list = np.array(wind_list)
    move_list = np.array(move_list)
    print(np.max(wind_list),np.min(wind_list))
    print(np.max(move_list), np.min(move_list))
#     110.0 0.0  wind
# 1219.8387650082498  0.0   move

def get_mmaction_from_informer():
    import random
    random.seed = 8
    obs_len = 8
    pre_len = 4
    saveroot = r'G:\data\mmaction'
    os.makedirs(saveroot,exist_ok=True)
    root = r'G:\data\informer_dataset\TY_BST_72'
    all_year_list = [str(x) for x in range(1950,2020)]
    year_list = [str(x) for x in range(1950,2017)]
    random.shuffle(year_list)
    evn = {}
    train_len = int(len(year_list)*0.8)
    anotation_list_train = year_list[:train_len]
    anotation_list_val = year_list[train_len:]
    anotation_list_test = ['2017','2018','2019']
    anotation_train = []
    anotation_val = []
    anotation_test = []
    for year_i in all_year_list:
        year_path = os.path.join(root, year_i)
        ty_list = os.listdir(year_path)
        for ty in ty_list:
            year = ty.split('.')[0][2:6]
            tyname = ty.split('.')[0][9:]
            year_ty_key = year + '_' + tyname
            evn[year_ty_key] = {}
            ty_path = os.path.join(year_path, ty)
            print(ty_path)
            excel_data = pd.read_excel(ty_path)
            for data_i, date in enumerate(list(excel_data['date'])):
                if data_i+obs_len+pre_len>=len(list(excel_data['date'])):
                    break
                else:
                    one_anotation = {}
                    one_anotation['year'] = year
                    one_anotation['tyname'] = tyname
                    date_list = []
                    for sub_data_i  in range(data_i,data_i+obs_len):
                        time1 = datetime.datetime.strptime(list(excel_data['date'])[sub_data_i], '%Y/%m/%d %H:%M:%S')
                        date_key = time1.strftime('%Y%m%d%H')
                        date_list.append(date_key)
                    one_anotation['date_list'] = date_list
                    if year in anotation_list_train:
                        anotation_train.append(one_anotation)
                    elif year in anotation_list_val:
                        anotation_val.append(one_anotation)
                    else:
                        anotation_test.append(one_anotation)
    np.save(os.path.join(saveroot,'train.npy'),anotation_train)
    np.save(os.path.join(saveroot, 'val.npy'), anotation_val)
    np.save(os.path.join(saveroot, 'test.npy'), anotation_test)



def add_area_onehot():
    saveroot = r'G:\data\evn_data\all_area'
    root = r'G:\data\evn_data\all_area'
    area_list = os.listdir(root)
    area_ = ['EP', 'NA', 'NI', 'SI', 'SP', 'WP']
    for area in area_list:
        if area != 'WP':
            continue
        area_path = os.path.join(root, area)
        year_list = os.listdir(area_path)
        # year_list = os.listdir(root)
        for year in year_list:
            # if year != '2019':
            #     continue
            year_path = os.path.join(root, area, year)
            ty_list = os.listdir(year_path)
            for ty in ty_list:
                ty_path = os.path.join(year_path,ty)
                date_list = os.listdir(ty_path)
                for date in date_list:
                    ty_dic = np.load(os.path.join(ty_path,date),allow_pickle=True).item()
                    ty_dic['area'] = np.array([0,0,0,0,0,1.])
                    np.save(os.path.join(ty_path,date),ty_dic)
                    print(ty_dic)



if __name__ == '__main__':
    get_env_from_informer()
    # get_mmaction_from_informer()
    # add_area_onehot()
#制作informer数据集 在这个文件夹下的trajectory——prediction