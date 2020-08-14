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
    Hello, I am Jeeves, the hotel concierge. How can I help you?
    """

    if not os.path.exists('session.csv'):
        click.echo('No session in progress. Please run initialize/ Begin command')

    else:
        hotel_path = helpers.get_hotel_path()
        click.echo('Continuing session for Hotel ' + hotel_path.lstrip('data/hotel_'))
        ctx.obj = Config(hotel_path)
    
@cli.command()
@click.argument('hotel_file', type = click.Path())
def initialize(hotel_file):
    """
    Initializes new hotel.json, starts new session.

    Usage:\n
    hotel initialize *.json\n

    Arguments:\n
    *.json must be a valid JSON filepath and located in the same directory as the downloaded *.py files\n

    Description:\n
    This commmand takes a new *.json file and creates necessary files and folders.\n
    Creates session.csv (start new session; must call Quit at the end of session) in current directory\n
    Renames *.json to hotel.json in new subdirectory.\n
    *.json should have this format:\n

    {"hotel_name": "B",
     "address": {"streetAddress": "56 7nd Street", "city": "New York", "state": "NY", "postalCode": "50065-7500"},
     "phoneNumber": "656 888-1234",
     "email": "b_hotel@gmail.com",
     "rooms": [
        {"number":1, "type":1, "cost":10},
        {"number":2, "type":2, "cost":20},
        {"number":3, "type":3, "cost":30},
        ]
    }

    """
    
    if os.path.isfile('session.csv'):
        print('Session already exists. Please Quit before use') 
    else:
        click.echo('Initializing...')

        script_dir = os.path.dirname(__file__)

        hotel_raw = pd.read_json(hotel_file, typ='series')
        dir_path = 'data/hotel_' + hotel_raw['hotel_name']
        os.makedirs(dir_path + '/rooms') 
        shutil.move(hotel_file, os.path.join(dir_path, 'hotel.json'))

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

    Usage:\n
    hotel register name email\n

    Arguments:\n
    name is type STRING\n
    email is type STRING\n

    Description:\n
    This commmand adds new clients to the DB, starting state = 3\n
    Client_supp.csv saves new client info, assigns a client ID\n
    Client_list.csv uses client ID to track relevent informtion

    """
    id_list = helpers.unique_client(config.client_supp, name, email)

    if id_list.empty:
        hotel_path = helpers.get_hotel_path()
        full_path = os.path.join(config.cwd_path, hotel_path)

        config.client_supp = helpers.add_client_supp(config.client_supp, name, email)
        helpers.overwrite_client_supp(config.client_supp, full_path)

        config.client_list = helpers.add_client_list(config.client_list, 3, None, None, -1, None, False, -1)
        helpers.overwrite_client_list(config.client_list, full_path)

        click.echo('Registration successful!')
    
    else:
        click.echo(f'The a client already exists with name: {name} and email: {email}')

@cli.command()
@click.argument('client_id', type = click.INT)
@click.argument('room_type', type = click.INT)
@click.argument('start', type = click.DateTime(formats=["%Y-%m-%d"]))
@click.argument('end', type = click.DateTime(formats=["%Y-%m-%d"]))
@click.pass_obj
def reserve_dates(config, client_id, room_type, start, end):
    """
    Find ideal rooms based on criteria given.

    Usage:\n
    hotel reserve-dates client_id room_type start_date end_date\n

    Arguments:\n
    client_id is type INT\n
    room_type is type INT\n
    start_date is format %Y-%m-%d\n
    end_date is format %Y-%m-%d\n

    Description:\n
    This commmand returns a list of rooms that match the criteria given\n
    Rooms are ordered by the minimal disruption of free intervals\n
    Creates new reservation in rooms/reservations/{best_room}.csv\n
    Splits and adds new interverl in rooms/interval/{best_rom}.csv\n
    Updates client_list.csv with new informtion, reserved state = 2

    """

    if client_id in config.client_list.index:

        if config.client_list.loc[client_id, 'state'] == 3:

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
        else:
            click.echo(f'The client ID {client_id} is currently unable to accept a new reservation. Please verify the current client state')
    else:
        click.echo(f'The client ID {client_id} does not exist. Please use a valid client ID')

@cli.command()
@click.argument('client_id', type = click.INT)
@click.pass_obj
def delete_reservation(config, client_id):
    """
    Undo reserve-dates command.

    Usage:\n
    hotel delete-reservation client_id\n

    Arguments:\n
    client_id is type INT\n

    Description:\n
    This commmand removes reservation in rooms/reservations/{best_room}.csv for client_id, state = 3\n
    Removes and rejoins old interverl in rooms/interval/{best_rom}.csv\n
    Updates client_list.csv with new informtion

    """
    if client_id in config.client_list.index:

        if config.client_list.loc[client_id, 'state'] == 2:
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

        else:
            click.echo(f'The client ID {client_id} does not have a reservation.')
    else:
        click.echo(f'The client ID {client_id} does not exist. Please use a valid client ID')


@cli.command()
@click.argument('client_id', type = click.INT)
@click.pass_obj
def check_in(config, client_id):
    """
    Update client list after check-in.

    Usage:\n
    hotel check-in client_id\n

    Arguments:\n
    client_id is type INT\n

    Description:\n
    This commmand pops reservation from reservation in rooms/reservations/{best_room}.csv\n
    Popped reservation is updated in client_list.csv\n
    State = 1

    """
    # Should verify booking is true!

    if client_id in config.client_list.index:

        if config.client_list.loc[client_id, 'state'] == 2:

            hotel_path = helpers.get_hotel_path()
            full_path = os.path.join(config.cwd_path, hotel_path)

            res_start = config.client_list.loc[client_id, 'start']
            room_number = config.client_list.loc[client_id, 'reserved_room']

            helpers.checkin_client_list(config.client_list, client_id)
            helpers.overwrite_client_list(config.client_list, full_path)

            helpers.pop_reservation(config.reservations, res_start, room_number)
            helpers.overwrite_reservations(config.reservations, config.cwd_path, hotel_path, room_number)
            click.echo('You are now checked in!')
        else:
            click.echo(f'The client ID {client_id} does not have a reservation. Please first make a reservation')
    else:
        click.echo(f'The client ID {client_id} does not exist. Please use a valid client ID')

@cli.command()
@click.argument('client_id', type = click.INT)
@click.argument('paid', type = click.BOOL)
@click.pass_obj
def check_out(config, client_id, paid):
    """
    Update client list after check-out.

    Usage:\n
    hotel check-out client_id paid\n

    Arguments:\n
    client_id is type INT\n
    paid is stype BOOL\n

    Description:\n
    This commmand updates client_list.csv with new informtion, state = 3
    """
    if client_id in config.client_list.index:

        if config.client_list.loc[client_id, 'state'] == 1:

            hotel_path = helpers.get_hotel_path()
            full_path = os.path.join(config.cwd_path, hotel_path)

            helpers.checkout_client_list(config.client_list, client_id, paid)
            helpers.overwrite_client_list(config.client_list, full_path)

            click.echo('You are now checked out!')

        else:
            click.echo(f'The client ID {client_id} is not currently checked-in. Please first ensure client is checked-in')
    else:
        click.echo(f'The client ID {client_id} does not exist. Please use a valid client ID')

@cli.command()
@click.argument('client_id', type = click.INT)
@click.pass_obj
def get_client_info(config, client_id):
    """
    Print client info.

    Usage:\n
    hotel get-client-info client_id\n

    Arguments:\n
    client_id is type INT\n

    Description:\n
    This commmand prints the info of client_id from client_list.csv
    """
    if client_id in config.client_list.index:

        client_info = config.client_list.iloc[client_id]
        click.echo(client_info)
    
    else:
        click.echo(f'The client ID {client_id} does not exist. Please use a valid client ID')

@cli.command()
@click.argument('state', type = click.INT)
@click.pass_obj
def get_current_clients(config, state):
    """
    Print all checked-in clients.

    Usage:\n
    hotel get-current-clients state\n

    Arguments:\n
    state is type INT\n

    Description:\n
    This commmand prints the info of all clients (based on state values) from client_list.csv

    States:\n
    registered client = 1\n
    client with reservation = 2\n
    client while checked-in = 3\n
    """
    curr_clients = config.client_list.loc[config.client_list['state'] == state]
    click.echo(curr_clients)

@cli.command()
@click.argument('name', type = click.STRING)
@click.argument('email', type = click.STRING)
@click.pass_obj
def get_client_id(config, name, email):
    """
    Print client ID.

    Usage:\n
    hotel get-client-id name email\n

    Arguments:\n
    name is type STRING\n
    email is type STRING\n

    Description:\n
    This commmand prints the client ID from client_supp.csv
    """

    id_list = helpers.unique_client(config.client_supp, name, email)
    if id_list.empty:
        click.echo(f'The name: {name} and email: {email} does not match any known client ID')
    
    else:
        client_id = int(id_list.squeeze())
        click.echo(f'The client ID for {name} is {client_id}')

@cli.command()
def quit():
    """
    Quit current session.

    Usage:\n
    hotel quit\n

    Arguments:\n
    None\n

    Description:\n
    This commmand ends the current session.\n
    Moves the session.csv file to data/hotel_*/session.csv for storage
    """

    hotel_path = helpers.get_hotel_path()
    hotel = hotel_path.split('/')[1]

    shutil.move('session.csv', hotel_path)
    click.echo(f'The session for {hotel} is now closed.')

@cli.command()
@click.argument('hotel_session', type = click.Path())
def begin(hotel_session):
    """
    Continue from previous session.

    Usage:\n
    hotel begin data/hotel_*/session.csv\n

    Arguments:\n
    hotel_session is filepath to the session.csv of the hotel of interest\n

    Description:\n
    This commmand starts a session.\n
    Moves the session.csv file from data/hotel_*/ to current working directory
    """
    hotel = hotel_session.split('/')[1]
    
    shutil.move(hotel_session, os.getcwd())
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
