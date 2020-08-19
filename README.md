# Hotel concierge software

## Setup

1) Clone the repo: `git clone https://github.com/mwkyuen/hotel.git`

2) Enter the repo directory: `cd hotel/`

3) Set up and launch your virtual environment (optional). Instructions can be found [here.](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/)

4) Install the Hotel Concierge library by running: `pip install .`

**The current working directory should be /path/to/hotel/**

You are now READY to proceed!

## Description

The Hotel Concierge Library comes with 12 functions. A general description of each function can be viewed using the command `hotel --help`. Moreover, a more detailed description of each function can be viewed by using the command `hotel COMMAND --help`.

#### Initialize & Session information

In order to get started, it is necessary to first initialize a Hotel object which the library will be working with. This initialization also sets up a `session.csv` file. The Concierge is able to handle multiple hotels, and the `session.csv` file keeps track of which hotel is currently being administered. Once a session is over the command `hotel quit` can be used to close the Hotel Concierge. Before new commands can be accepted, the command `hotel begin /path/to/session.csv` will need to be called, pointing to the hotel session to be administered.

A hotel can be initialized by calling `hotel initialize *.json`. The `*.json` file must be present in the same directory as the current working directory. You can use a custom `*.json` file or you can use the ones supplied in the `samples/` folder, simply copy over one of the `*.json` files from the `samples/` folder into your current working directory. 

If using a custom `*.json` file, the `*.json` file must meet the minimal schema described below:

```
schema = {  'type': 'object',
                'properties': {
                    'hotel_name': {
                        'type': 'string',
                        'description': 'Name of hotel'
                    },
                    'rooms': {
                        'type': 'array',
                        'items': {'$ref': '#/definitions/room'}
                    }
                },
                'definitions': {
                    'room': {
                        'type': 'object',
                        'required': ['number', 'type', 'cost'],
                        'properties': {
                            'number': {
                                'type': 'integer',
                                'description': 'Room number'
                            },
                            'type': {
                                'type': 'integer',
                                'description': 'Room type'
                            },
                            'cost': {
                                'type': 'integer',
                                'description': 'Cost of room per night'
                            }
                        }
                    }
                },
                'required': ['hotel_name', 'rooms']
    }  
```

The schema dictates that the hotels have at least a name and an array of rooms. However, additional information can be added (as seen in the `samples/*.json`) which can be utilized in functions under future developments.

The Initialize command creates a new `data/hotel_{name}` directory which will hold all the information of the hotel state. Inbetween sessions, the `session.csv` file will also be stored under this directory.

#### Clients
The clients of each hotels are stored in the `client_list.csv` as a client_list object, and the `client_supp.csv` files as a client_supp object. Each client is assigned a unique client ID which is used to index additional information about the clients. Each client can exist in three possible states. 

* State 1 is a client who is currently checked-in at the hotel. 
* State 2 is a client with an existing reservation at the hotel.
* State 3 is a client who has neither a reservation nor currently checked-in (default state)

As commands are issued to the Concierge the client objects and the relevant `*.csv` files are updated. 

![client_state_change](/images/client_state.png)

#### Rooms
Room of the hotel are represented with Reservations and Intervals objects.

Each room has a list of incoming reservations, which will be removed once a client has either checked-in or decided to cancel the reservation. The Concierge holds the Reservations object as a sorted pandas Dataframe with DatetimeIndex (start), rooms as columns names, and client ID as values. Values are sorted by DatetimeIndex (i.e the next reservation for Room X will be at the top)

Each room also has a list of available intervals, to which a new reservation can be added to, splicing the interval into two remaining interval segments. The Concierge holds the Intervals object as a sorted pandas Dataframe with DatetimeIndex (start), rooms as column names, and Datatime (end) as values.

As commands are issued to the Concierge the room objects and the relevant `*.csv` files are updated. 

## Using the Hotel Concierge (example)

First setup the Hotel Concierge library as detailed in Setup above.

In `samples/`, Hotel A has three rooms, all of type 1, while Hotel B has six rooms, room 1-2 of type 1, room 3-4 of type 2, and room 5-6 of type 3

Room types represent the luxury and amenities provided to each room 

#### Initializing new hotel
```
cp samples/hotel_B.json ./ #Copy a sample hotel to your hotel directory

hotel initialize hotel_B.json #Initialize, creating new directories and starting new session for Hotel B

hotel register t.king tiger.king@gmail.com #Register new client

hotel get-client-id t.king tiger.king@gmail.com #Check client ID

hotel reserve-dates 0 3 2020-08-22 2020-08-28 #Reserve dates for Client_0, room Type_3

hotel quit #Close current session
```
#### Starting from a previous session

```
hotel begin data/hotel_B/session.csv #Open session for Hotel B

hotel register s.beast sexy.beast@gmail.com #Register new client

hotel register a.possum awesome.possum@gmail.com #Register new client

hotel get-client-id s.beast sexy.beast@gmail.com #Check client ID

hotel get-client-id a.possum awesome.possum@gmail.com #Check client ID

hotel reserve-dates 1 2 2020-09-14 2020-09-18 #Reserve dates for Client_1, room Type_2

hotel reserve-dates 2 3 2020-08-22 2020-08-28 #Reserve dates for Client_2, room Type_3

hotel get-all-clients #Print all clients

hotel delete-reservation 2 #Delete reservation for Client_2

hotel get-some-clients 2 #Print clients which are in State_3

hotel get-one-client 2 #Print the details of Client_2

hotel get-one-client 1 #Print the details of Client_1

hotel check-in 0 #Check in for Client_0

hotel check-out 0 yes #Check out for Clent_0, boolean if they have paid

hotel quit #Close current session
```

## Future directions
Currently all files are written into `*.csv` files. Objects are seperated across multiple files (i.e Rooms object), and files were designed to accommodate manual inputs and easy viewing. However, this approach is prone to mistakes and corruption of data files. 

Moving forward, I plan to use the `sqlite3` python library to handle the hotel database information in a single `.db` file and disallow manual inputs. 

I also plan to add additional functions which will be helpful to the Concierge in performing its duties. If you have suggestions of additional function you would like to see, let me know and I will try to accommadate them. Thank you for reading these docs. 