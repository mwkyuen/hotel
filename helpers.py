import math
from datetime import datetime, timedelta
import pandas as pd
import os
import numpy

def create_temp(hotel_name):
    hotel_dir = 'data/hotel_' + hotel_name + '\n'
    with open('session.csv', 'w') as out_file:
        out_file.write(hotel_dir)

def get_hotel_path():
    with open('session.csv', 'r') as fp:
        line = fp.readline().rstrip()

    return line

def get_reservations(r_path):

    num_files = os.listdir(r_path)
    # reservations = {int(os.path.splitext(num)[0]): [] for num in num_files}
    reservations = pd.DataFrame()

    for file in num_files:
        room = os.path.splitext(file)[0]

        real_file = os.path.join(r_path, file)
        df = pd.read_csv(real_file)

        datetime_series = pd.to_datetime(df['start'])
        datetime_index = pd.DatetimeIndex(datetime_series.values)

        df = df.set_index(datetime_index)
        df.drop('start',axis=1,inplace=True)
        df = df.rename(columns = {'client_id': room})
        reservations = pd.concat([reservations, df], axis = 1, sort=False)   

    return reservations


def get_intervals(i_path):

    num_files = os.listdir(i_path)
    intervals = pd.DataFrame()

    for file in num_files:
        room = os.path.splitext(file)[0]

        real_file = os.path.join(i_path, file)
                
        df = pd.read_csv(real_file)
        inf_intv = df.isnull().values.any()

        if inf_intv:
            df['start'] = datetime.now().date()
            df['end'] = pd.Timestamp.max.date()
        
        datetime_series = pd.to_datetime(df['start'])
        datetime_index = pd.DatetimeIndex(datetime_series.values)

        df['end'] = pd.to_datetime(df['end'])
        df = df.set_index(datetime_index)
        df.drop('start',axis=1,inplace=True)
        df = df.rename(columns = {'end': room})
        intervals = pd.concat([intervals, df], axis = 1, sort=False) 

    # df = pd.DataFrame.from_dict(intervals, orient='index')
    # return df.transpose()
    return intervals

def add_client_supp(client_supp, name, contact_info):

    temp_supp = pd.DataFrame({'name':[name],
                              'email':[contact_info]
                            }) 

    return client_supp.append(temp_supp, ignore_index = True)

def add_client_list(client_list, state, start, end, res_room, payment_due, paid, curr_room):

    temp_info = pd.DataFrame({'state':[state],
                              'start':[start],
                              'end':[end],
                              'reserved_room':[res_room],
                              'payment_due':[payment_due],
                              'paid':[paid],
                              'curr_room':[curr_room],
                            }) 

    return client_list.append(temp_info, ignore_index = True)

def overwrite_client_supp(client_supp, full_path):

    client_supp = client_supp.rename_axis('client_id').reset_index()
    client_supp.to_csv(os.path.join(full_path, 'client_supp.csv'), index=False)

def overwrite_client_list(client_list, full_path):

    client_list = client_list.rename_axis('client_id').reset_index()
    client_list.to_csv(os.path.join(full_path, 'client_list.csv'), index = False)

def get_room_of_type(hotel, room_type):

    room_list = []
    for room in hotel['rooms']:
        if room['type'] == room_type:
            room_list.append(str(room['number']))
    return room_list


def get_room_number_optimized(intervals, start, end):
    
    """
    Return list of available rooms, ordered by best room
    """
    mask = (intervals.index <= start) 
    df = intervals[mask].stack().swaplevel(0, 1).reset_index()
    df.columns = ['room', 'start', 'end']

    def filter(x):
        if (x['start'].date() < start.date() and end.date() < x['end'].date()):
            # return pd.DataFrame(x)
            return x
        else:
            return pd.Series(data = [None, None, None], index = x.index)

    df = df.apply(filter, axis = 1).dropna()
    overlap = df.set_index('room')
    ##################################################################
    # interval_overlap = []
    # for room_number in room_list:
    #     mask = (df.index <= start) 
    #     df = df.loc[mask]
    #     sr = df[str(room_number)].dropna()
    #     for index, value in sr.items():
    #         if index.date() < start.date() and end.date() < value:
    #             interval_overlap.append((index.date(), value.date()))
    ###################################################################
    
    room_order = get_smallest_left(overlap, start, end)
    return room_order.astype({'order': 'int64'})

def get_smallest_left(overlap, start, end):
    """
    Return room_number sorted by smallest_section_remaining
    """

    smallest_remaining = pd.DataFrame({'room': overlap.index, 'order': ([None] * overlap.index.size)})
    smallest_remaining.set_index('room', inplace=True)

    for index, row in overlap.iterrows():

        left = start.date() - row['start'].date()
        right = row['end'].date() - end.date()
        if (left.days < right.days):
            # print(type(left.days))
            # print(type(index))
            smallest_remaining.loc[index, 'order'] = int(left.days)
        else:
            # print(type(right.days))
            # print(type(index))
            smallest_remaining.loc[index, 'order'] = int(right.days)

    return smallest_remaining.reset_index().sort_values(by=['order'])


def get_payment(hotel, best_room):
    for room in hotel['rooms']:
        if room['number'] == int(best_room):
            return room['cost']
        
def add_reservations(reservations, room_number, client_id, start):    

    reservations.loc[start, str(room_number)] = client_id

def add_intervals(intervals, room_number, start, end, hotel_path):

    old_intv = get_old_interval(intervals, room_number, start, end)
    new_intv = split_interval(old_intv, start, end)
    update_intervals(intervals, new_intv, room_number)

def get_old_interval(intervals, room_number, start, end):
    df = intervals[str(room_number)].dropna()
    mask = (df.index <= start) 
    df = df.loc[mask]
    for index, value in df.items():
            if index.date() < start.date() and end.date() < value:
                return (index.date(), value.date())

def split_interval(old_intv, start, end):
    data = [(old_intv[0], start.date() + timedelta(-1)), (end.date() + timedelta(1), old_intv[1])]
    df = pd.DataFrame(data, columns = ['start', 'end'])

    datetime_series = pd.to_datetime(df['start'])
    datetime_index = pd.DatetimeIndex(datetime_series.values)

    df['end'] = pd.to_datetime(df['end'])
    df = df.set_index(datetime_index)
    
    return df.drop('start', axis = 1)

def update_intervals(intervals, new_intervals, room_number):
    old_start = new_intervals.index[0]
    new_start = new_intervals.index[1]

    intervals.loc[old_start, str(room_number)] = new_intervals.loc[old_start, 'end']
    intervals.loc[new_start, str(room_number)] = new_intervals.loc[new_start, 'end']
    
    intervals.sort_index(inplace = True)


def add_reservation_client_list(client_list, client_id, state, start, end, best_room, payment_due, paid):
    client_list.loc[client_id, 'start'] = start.date()
    client_list.loc[client_id, 'end'] = end.date()
    client_list.loc[client_id, 'reserved_room'] = best_room
    client_list.loc[client_id, 'payment_due'] = payment_due
    client_list.loc[client_id, 'paid'] = paid
    client_list.loc[client_id, 'state'] = state


def remove_reservation_client_list(client_list, client_id):
    client_list.loc[client_id, 'start'] = None
    client_list.loc[client_id, 'end'] = None
    client_list.loc[client_id, 'reserved_room'] = -1
    client_list.loc[client_id, 'payment_due'] = None
    client_list.loc[client_id, 'paid'] = False
    client_list.loc[client_id, 'state'] = 3

def remove_reservations(reservations, res_start):    

    reservations.drop(datetime.strptime(res_start, '%Y-%m-%d'), inplace = True)

def remove_intervals(intervals, start, end, room_number):
    old_intv_end = datetime.strptime(start, '%Y-%m-%d') + timedelta(-1)
    old_intv_start = datetime.strptime(end, '%Y-%m-%d') + timedelta(1)

    new_intv_start = intervals.loc[intervals[str(room_number)] == old_intv_end].index.date[0]
    new_intv_end = intervals.loc[old_intv_start, str(room_number)]

    intervals.loc[new_intv_start, str(room_number)] = new_intv_end
    intervals.loc[old_intv_start, str(room_number)] = None

    intervals.dropna(axis = 0, how = 'all', inplace = True)

def checkin_client_list(client_list, client_id):

    client_list.loc[client_id, 'state'] = 1
    client_list.loc[client_id, 'curr_room'] = client_list.loc[client_id, 'reserved_room']

def pop_reservation(reservations, res_start, room_number):

    reservations.loc[res_start, str(room_number)] = None
   
def checkout_client_list(client_list, client_id, paid):

    client_list.loc[client_id, 'state'] = 3
    client_list.loc[client_id, 'start'] = None
    client_list.loc[client_id, 'end'] = None
    client_list.loc[client_id, 'reserved_room'] = -1
    client_list.loc[client_id, 'payment_due'] = None
    client_list.loc[client_id, 'paid'] = paid
    client_list.loc[client_id, 'curr_room'] = -1

def overwrite_intervals(intervals, script_dir, hotel_path, room_number):
    df = intervals[str(room_number)].dropna()

    rooms_path = os.path.join(hotel_path, 'rooms/intervals')
    full_path = os.path.join(script_dir, rooms_path)
    file_name = str(room_number)  + '.csv'
    with open(os.path.join(full_path, file_name), 'w') as file:
        file.write('start,end\n')
        df.to_csv(file, header=False, index=True)

def overwrite_reservations(reservations, script_dir, hotel_path, room_number):

    df = reservations[str(room_number)].dropna()
    rooms_path = os.path.join(hotel_path, 'rooms/reservations')
    full_path = os.path.join(script_dir, rooms_path)
    file_name = str(room_number)  + '.csv'
    with open(os.path.join(full_path, file_name), 'w') as file:
        file.write('start,client_id\n')
        df.to_csv(file, header=False, index=True)
