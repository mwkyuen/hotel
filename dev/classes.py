"""
import os
import pandas as pd

Upgrade config file using list of Clients (instead of client + client_supp)
                      and list of Rooms (instead of hotel + reservation_df + interval_df)?

class Client:

	def __init__(self, client_id, name, contact_info, state):
		self.client_id = client_id
		self.name = name
		self.contact_info = contact_info
		self.start = None
		self.end = None
		self.state = state
		self.payment_owed = None
		self.payment_paid = False
		self.curr_room = None
		self.prev_room = None

class Room:

    def __init__(self, room_number, room_type, curr_client, cost, r_list, i_list):
        self.room_number = room_number
        self.room_type = room_type
        self.curr_client = curr_client
        self.cost = cost
        self.reservation_list = r_list
        self.free_intervals = i_list


class Reservation:

	def __init__(self, client_id, start):
		self.client_id = client_id
		self.start = start


class Interval:

	def __init__(self, start, end):
		self.start = start
		self.end = end
"""
