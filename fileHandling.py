import json


class FileHandling:
    def __init__(self):
        # File names
        self.USERS_FILE = "database/users.txt"
        self.AUCTIONS_FILE = "database/auctions.txt"
        self.BIDS_FILE = "database/bids.txt"

        # Data structures
        self.users = {}
        self.auctions = {}
        self.bids = {}

    def save_files_users(self, new_data):
        try:
            with open(self.USERS_FILE, "w") as u_file:
                json_string_user_data = json.dumps(new_data)
                u_file.write(json_string_user_data)
        except Exception as user_file_err:
            print("user save file error: ", user_file_err)
        # self.load_data()

    def save_files_auction(self, new_data):
        try:
            with open(self.AUCTIONS_FILE, "w") as a_file:
                json_string_auction_data = json.dumps(new_data)
                a_file.write(json_string_auction_data)
        except Exception as auction_file_err:
            print("auction save file error: ", auction_file_err)
        # self.load_data()

    def save_files_bids(self, new_data):
        try:
            with open(self.BIDS_FILE, "w") as b_file:
                json_string_bid_data = json.dumps(new_data)
                b_file.write(json_string_bid_data)
        except Exception as bid_file_err:
            print("bid save file error: ", bid_file_err)
        # self.load_data()

    # Show data from file
    def show_data(self, datas):
        if datas:
            for key, value in datas.items():
                print("--> ", value)
                # print("show data: ", value['username'], value['email'])
        else:
            print("No Data found.", datas)
            return

    def create_files(self):
        try:
            with open(self.USERS_FILE, "a") as user_file:
                print("user text file created.")
            with open(self.AUCTIONS_FILE, "a") as auction_file:
                print("auction text file created.")
            with open(self.BIDS_FILE, "a") as bid_file:
                print("bid text file created.")

        except Exception as err:
            print("text file database creation fail: ", err)

    # Load data from files / read data from database
    def load_data(self):
        try:
            with open(self.USERS_FILE, "r") as u_file:
                data = u_file.read()
                if len(data) != 0:
                    content = json.loads(data)  # json_dict_data type
                    self.users.update(content)
                    # self.show_data(self.users)
                else:
                    print('user data is empty.')
                    # print(type(data), len(data) == 0)

            with open(self.AUCTIONS_FILE, "r") as a_file:
                data = a_file.read()
                if len(data) != 0:
                    content = json.loads(data)  # json_dict_data type
                    self.auctions.update(content)
                    # self.show_data(self.auctions)
                else:
                    print('auction data is empty.')

            with open(self.BIDS_FILE, "r") as b_file:
                data = b_file.read()
                if len(data) != 0:
                    content = json.loads(data)  # json_dict_data type
                    self.bids.update(content)
                    # self.show_data(self.bids)
                else:
                    print('bid data is empty.')

        except json.JSONDecodeError as json_err:
            print(f"Error decoding JSON: {json_err}")
            # Handle the JSON decoding error, to log it or take specific actions.

        except FileNotFoundError as file_err:
            print(f"File does not exit: {file_err}")
            # Handle the file not found error, check if the files exist or create default data.

        except Exception as e:
            print(f"Unexpected error: {e}")
            # Handle other unexpected errors.

        # print('userdata: ', self.users)
        # print('auctiondata: ', self.auctions)
        # print('biddata: ', self.bids)


file1 = FileHandling()
# file1.load_data()
