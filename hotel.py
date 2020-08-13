import click
import pandas as pd
import helpers
import os
import shutil
# import sqlite3


INIT_CLIENT_INFO = 'client_id,state,start,end,reserved_room,payment_due,paid,curr_room\n'
INIT_CLIENT_SUPP = 'client_id,name,email\n'
INIT_RESERVATION_INFO = 'start,client_id\n'
INIT_INTERVAL_INFO = 'start,end\n,'

class Config(object):

    def __init__(self, hotel_path):

        cwd_path = os.path.dirname(__file__)
        self.cwd_path = cwd_path

        rel_path = hotel_path + '/client_list.csv'
        fp = os.path.join(cwd_path, rel_path)
        self.client_list = pd.read_csv(fp, index_col = 'client_id')

        rel_path = hotel_path + '/client_supp.csv'
        fp = os.path.join(cwd_path, rel_path)
        self.client_supp = pd.read_csv(fp, index_col = 'client_id')

        rel_path = hotel_path + '/hotel.json'
        fp = os.path.join(cwd_path, rel_path)
        self.hotel = pd.read_json(fp, typ='series')
            
        rel_path = hotel_path + '/rooms/reservations'
        fp = os.path.join(cwd_path, rel_path)
        self.reservations = helpers.get_reservations(fp)

        rel_path = hotel_path + '/rooms/intervals'
        fp = os.path.join(cwd_path, rel_path)
        self.intervals = helpers.get_intervals(fp)

@click.group()
@click.pass_context
def cli(ctx):
    """
    I am the hotel concierge.
    """

    if not os.path.exists('session.csv'):
        click.echo('No session in progress. Please run initialize/ Begin command')

    else:
        hotel_path = helpers.get_hotel_path()
        click.echo('Continuing session for Hotel ' + hotel_path.lstrip('data/hotel_'))
        ctx.obj = Config(hotel_path)
    
@cli.command()
@click.argument('hotel_file', type = click.File())
def initialize(hotel_file):
    """
    Initializes new hotel.json. Creates necessary files.

    """
    
    if os.path.isfile('session.csv'):
        print('Session already exists. Please Quit before use') 
    else:
        click.echo('Initializing...')

        script_dir = os.path.dirname(__file__)

        hotel_raw = pd.read_json(hotel_file, typ='series')
        dir_path = 'data/hotel_' + hotel_raw['hotel_name']
        os.makedirs(dir_path + '/rooms') 
        shutil.move('hotel.json', dir_path)

        rel_path = dir_path + '/client_list.csv'
        fp = os.path.join(script_dir, rel_path)
        with open(fp, 'w') as out_file:
            out_file.write(INIT_CLIENT_INFO)

        rel_path = dir_path + '/client_supp.csv'
        fp = os.path.join(script_dir, rel_path)
        with open(fp, 'w') as out_file:
            out_file.write(INIT_CLIENT_SUPP)

        os.mkdir(dir_path + '/rooms/reservations') 
        os.mkdir(dir_path + '/rooms/intervals')

        for room in hotel_raw['rooms']:
            
            rel_path = dir_path + '/rooms/reservations/' + str(room['number']) + '.csv'
            fp = os.path.join(script_dir, rel_path)
            with open(fp, 'w') as out_file:
                out_file.write(INIT_RESERVATION_INFO)

            rel_path = dir_path + '/rooms/intervals/' + str(room['number']) + '.csv'
            fp = os.path.join(script_dir, rel_path)
            with open(fp, 'w') as out_file:
                out_file.write(INIT_INTERVAL_INFO)


        helpers.create_temp(hotel_raw['hotel_name'])

        click.echo('Initialization complete.')


@cli.command()
@click.argument('name', type = click.STRING)
@click.argument('email', type = click.STRING)
@click.pass_obj
def register(config, name, email):
    """
    Add new client information to the DB.
    
    """
    hotel_path = helpers.get_hotel_path()
    full_path = os.path.join(config.cwd_path, hotel_path)

    config.client_supp = helpers.add_client_supp(config.client_supp, name, email)
    helpers.overwrite_client_supp(config.client_supp, full_path)

    config.client_list = helpers.add_client_list(config.client_list, 3, None, None, -1, None, False, -1)
    helpers.overwrite_client_list(config.client_list, full_path)

    click.echo('Registration successful!')

@cli.command()
@click.argument('client_id', type = click.INT)
@click.argument('room_type', type = click.INT)
@click.argument('start', type = click.DateTime(formats=["%Y-%m-%d"]))
@click.argument('end', type = click.DateTime(formats=["%Y-%m-%d"]))
@click.pass_obj
def reserve_dates(config, client_id, room_type, start, end):
    """
    Find available rooms. Reserve selected room.

    """
    hotel_path = helpers.get_hotel_path()
    full_path = os.path.join(config.cwd_path, hotel_path)
    
    room_matching_type = helpers.get_room_of_type(config.hotel, room_type)
    df_intervals = config.intervals[room_matching_type].dropna(axis = 0, how = 'all')
    
    available_rooms = helpers.get_room_number_optimized(df_intervals, start, end)
    delta = end - start

    if available_rooms.empty:
        click.echo('Sorry! There are no rooms available!')
    else:
        best_room = available_rooms['room'][0]

        payment = helpers.get_payment(config.hotel, best_room)
        payment_due = delta.days * payment
        paid = False

        helpers.add_reservation_client_list(config.client_list, client_id, 2, start, end, best_room, payment_due, paid) 
        helpers.overwrite_client_list(config.client_list, full_path)

        helpers.add_reservations(config.reservations, best_room, client_id, start) 
        helpers.overwrite_reservations(config.reservations, config.cwd_path, hotel_path, best_room)

        helpers.add_intervals(config.intervals, best_room, start, end, hotel_path)      
        helpers.overwrite_intervals(config.intervals, config.cwd_path, hotel_path, best_room)

        click.echo('Reservation successful!')
        

@cli.command()
@click.argument('client_id', type = click.INT)
@click.pass_obj
def delete_reservation(config, client_id):
    """
    Undo reserve_dates command

    """
    hotel_path = helpers.get_hotel_path()
    full_path = os.path.join(config.cwd_path, hotel_path)

    res_start = config.client_list.loc[client_id, 'start']
    res_end = config.client_list.loc[client_id, 'end']
    room_number = config.client_list.loc[client_id, 'reserved_room']
    
    helpers.remove_reservation_client_list(config.client_list, client_id)
    helpers.overwrite_client_list(config.client_list, full_path)
    
    helpers.remove_reservations(config.reservations, res_start) 
    helpers.overwrite_reservations(config.reservations, config.cwd_path, hotel_path, room_number)

    helpers.remove_intervals(config.intervals, res_start, res_end, room_number)
    helpers.overwrite_intervals(config.intervals, config.cwd_path, hotel_path, room_number)

    click.echo('The reservation has been deleted.')

@cli.command()
@click.argument('client_id', type = click.INT)
@click.pass_obj
def check_in(config, client_id):
    """
    Changes state of client in DB

    """
    # Should verify booking is true!
    hotel_path = helpers.get_hotel_path()
    full_path = os.path.join(config.cwd_path, hotel_path)

    res_start = config.client_list.loc[client_id, 'start']
    room_number = config.client_list.loc[client_id, 'reserved_room']

    helpers.checkin_client_list(config.client_list, client_id)
    helpers.overwrite_client_list(config.client_list, full_path)

    helpers.pop_reservation(config.reservations, res_start, room_number)
    helpers.overwrite_reservations(config.reservations, config.cwd_path, hotel_path, room_number)
    click.echo('You are now checked in!')

@cli.command()
@click.argument('client_id', type = click.INT)
@click.argument('paid', type = click.BOOL)
@click.pass_obj
def check_out(config, client_id, paid):
    """
    Reset client state 
    """
    hotel_path = helpers.get_hotel_path()
    full_path = os.path.join(config.cwd_path, hotel_path)

    helpers.checkout_client_list(config.client_list, client_id, paid)
    helpers.overwrite_client_list(config.client_list, full_path)

    click.echo('You are now checked out!')

@cli.command()
@click.argument('client_id', type = click.INT)
@click.pass_obj
def get_client_info(config, client_id):
    """
    Prints client info
    """
    client_info = config.client_list.iloc[client_id]
    click.echo(client_info)

@cli.command()
@click.pass_obj
def get_current_clients(config):
    """
    Return list of all currently checked in clients
    """
    curr_clients = config.client_list.loc[config.client_list['state'] == 1]

    click.echo(curr_clients)

@cli.command()
@click.argument('name', type = click.STRING)
@click.argument('email', type = click.STRING)
@click.pass_obj
def get_client_id(config, name, email):
    """
    """
    df = config.client_supp.reset_index()
    
    def find_id(x):
        if x['name'] == name and x['email'] == email:
            return x['client_id']

    client_id = df.apply(find_id, axis = 1).dropna().squeeze()

    click.echo(f'The client ID for {name} is {int(client_id)}')

@cli.command()
def quit():
    """
    """

    hotel_path = helpers.get_hotel_path()
    hotel = hotel_path.split('/')[1]

    shutil.move('session.csv', hotel_path)
    click.echo(f'The session for {hotel} is now closed.')

@cli.command()
@click.argument('hotel_path', type = click.Path())
def begin(hotel_path):
    """
    """
    hotel = hotel_path.split('/')[1]

    shutil.move(os.path.join(hotel_path, 'session.csv'), os.getcwd())
    click.echo(f'The session for {hotel} is now open!')

# @cli.command()
# @click.pass_obj
# def undo_last_command():
#     """
#     Prev command stored in sessions.csv
#     """
#     click.echo('Hello World!')

# @cli.command()
# @click.pass_obj
# def read_glacial_file():
#     """
#     Stores client previous stay data (start, end, payment_due, paid, prev_room)
#     """
#     click.echo('Hello World!')
