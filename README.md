# Hotel concierge software

## How to use
### Setup

1) Clone the repo: `git clone https://github.com/mwkyuen/hotel.git`

2) Enter the repo directory: `cd hotel/`

3) Set up and launch your virtual environment (optional). Instructions can be found [here.](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/)

4) Install the Hotel library by running: `pip install .`

You are now READY to proceed!

### Description

The Hotel Concierge Library comes with 11 functions. A general description of each function can be viewed using the command `hotel --help`. Moreover, a more detailed description of each function can be viewed by using the command `hotel COMMAND --help`.

#### Initialize & Session information

In order to get started, it is necessary to first initialize a hotel to which the library will be working with. This initialization also sets up a `session.csv` file. The Concierge is able to handle multiple hotels, and the `session.csv` file keeps track of which hotel is currently being administered. Once a session is over the command `hotel quit` can be used to close the ongoing Hotel Concierge. Before new commands can be accepted, the command `hotel begin path/to/session.csv` will need to be called, pointing to the sessions of the hotel which is to be administered.

A hotel can be initialized by calling `hotel initialize *.json`. The `*.json` file must be present in the same directory as the `.py` files. You can use a custom `*.json` file or you can use the ones supplied in the `samples/` folder, simply copy over one of the `*.json` files from the `samples/` folder into your current directory. 

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

#### Clients
The clients of each hotels are stored in the `client_list.csv` and the `client_supp.csv` files. Each client is assigned a unique client ID which is used to index additional information about the clients. Each client can exist in three possible states. 

* State 1 is a client who is currently checked-in at the hotel. 
* State 2 is a client with an existing reservation at the hotel.
* State 3 is a client who has neither a reservation nor currently checked-in (default state)

As commands are issued to the Concierge the state and information of the clients are updated. `client_supp.csv` is updated only during the registration of a new client, where name and contact information is used to generate a unique client ID which will index all the additional information about the client in `client_list.csv`

#### Rooms
The rooms information of the hotels are stored as Reservations and Intervals. Each room has a list of incoming reservations, indexed by their start dates. Each room also has a list of available intervals, indexed by their start dates.

#### Algorithm

### Using the Hotel Concierge (example)
Hello world!