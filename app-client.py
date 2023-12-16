import datetime
from datetime import datetime, timedelta
import json
import random
import socket
import sys
import threading

import encry_decrypt
import my_modules
from my_modules import time_remaining
import my_validation


class Client:

    def __init__(self):
        self.a3E = encry_decrypt.A3Encryption()
        self.a3D = encry_decrypt.A3Decryption()
        self.default_key = "myatmyat"
        self.target_ip = "localhost"
        self.target_port = 9191
        self.userKey = self.getting_key()
        self.r2 = my_validation.Validation()
        # self.auth_user = {"68861114141": {"uuid": "6447101397", "username": "myat1",
        #                                   "email": "myat1@gmail.com",
        #                                   "password": "passworD123",
        #                                   "address": "somewhere",
        #                                   "phone_number": "0919771218",
        #                                   "content": "aaaaa"}}
        self.auth_user = {}
        self.auction_list = {}
        self.user_list = {}
        self.bids_list = {}
        self.bids_update_flag = False
        # self.client_menu()

    def getting_key(self):
        userKey: str = self.default_key
        return userKey

    def client_runner(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.target_ip, self.target_port))
        return client  # to send and received data

    def client_menu(self):
        self.print_menu()
        client = self.client_runner()
        try:

            choice = str(input("enter your choice: "))
            if choice == '1':
                self.register(client)
            elif choice == '2':
                if self.auth_user:
                    self.profile_info(self.auth_user)
                else:
                    self.login(client)
            elif choice == '3':
                if self.auth_user != {}:
                    self.placing_bids(client)
                else:
                    print("unauthenticated.Please Login first.")
            elif choice == '4':
                if self.auth_user != {}:
                    self.auction_creation(client)
                else:
                    print("unauthenticated.Please Login first.")
            elif choice == '5':
                self.exit_program(client)
            elif choice == '6':
                self.auction_status(client)
            elif choice == '9':
                if self.auth_user != {}:
                    self.user_delete_acc(client)
                else:
                    print("unauthenticated.Please Login first.")
            elif choice == '8':
                if self.auth_user != {}:
                    self.auctions_delete(client)
                else:
                    print("unauthenticated.Please Login first.")
            elif choice == '7':
                if self.auth_user != {}:
                    self.auth_user.clear()
                    print('Credential Clear.')
                else:
                    print("unauthenticated.Please Login first.")
            else:
                print("Invalid choice: ")

        except Exception as err:
            print("client menu error: ", err)
        finally:
            print("finally;;;;;")
            client.close()
        # json -> encrypt -> encode -> send
        # json -> decrypt -> decode -> recv

    def register(self, client):
        try:
            name: str = str(input("Enter username: "))
            email: str = str(input("Enter email: "))
            password: str = str(input("Enter password: "))
            c_password: str = str(input("Enter password to confirm: "))
            address: str = str(input("Enter address: "))
            phone_number: str = str(input("Enter phone_number: "))
            content: str = str(input("Enter something you want: "))
            uuid: str = str(random.randint(1111, 99999)) + str(my_modules.current_time_milliseconds())[-5:]  # for user
            data_form = [name, email, password, address, phone_number, content, uuid]
            new_data = {"type": "register", "data": data_form}
            if password != c_password:
                return self.register(client)
            else:
                print(new_data)
                for i in data_form:
                    print(i)
                # print(f"name: {0}\nemail: {1}\npassword: {2}\naddress: {3}\nphone: {4}\ncontent: {5}\n".format(
                # name,email,password,address,phone_number,content))
                self.sendServer(client, new_data)
                data = self.recvServer(client)
                print(data['content'])
        except Exception as err:
            print("register error: ", err)

    def login(self, client):
        try:
            email: str = str(input("Enter email: "))
            password: str = str(input("Enter password: "))

            data_form = [email, password]
            new_data = {"type": "login", "data": data_form}
            # print(new_data)
            self.sendServer(client, new_data)
            result = self.recvServer2(client)
            # print(result)
            if 'content' in result:
                # print(result['content'])
                if result['content']['status'] is False:
                    print(result['content']['message'])
                else:
                    print("Login success.")
                    # print(result['content']['bid_data'])
                    auth_info = result['content']['auth_info']
                    auction_data = result['content']['auction_data']
                    bid_data = result['content']['bid_data']
                    self.auth_user.clear()
                    self.auth_user.update(auth_info)
                    self.auction_list.update(auction_data)
                    self.bids_list.update(bid_data)

            else:
                print(">>>unauthenticated user-info.")

            if self.auth_user:
                # print("authenticated info: ", self.auth_user)
                self.profile_info(self.auth_user)
            else:
                print(">>>auth user-info not found; ")

        except Exception as err:
            print("login error: ", err)

    def auth_user_data_refine(self, data):
        if data:
            first_key = next(iter(data.keys()), None)
            # Access the 'uuid' from the nested dictionary
            uuid_value = data.get(first_key, {}).get('uuid', None)
            email = data.get(first_key, {}).get('email', None)
            phone_number = data.get(first_key, {}).get('phone_number', None)
            username = data.get(first_key, {}).get('username', None)
            result = {"user_id": uuid_value, "email": email, "phone_number": phone_number, "username": username}
            return result
        else:
            return {}

    def auction_creation(self, client):
        print("this is auction creation.")
        try:
            auth_user = self.auth_user_data_refine(self.auth_user)
            user_id: str = auth_user['user_id']
            email: str = auth_user['email']

            while True:
                try:
                    item_name: str = str(input("Enter item name (at least 3 words): "))
                    description: str = str(input("Enter description (at least 3 words): "))
                    print(">>> item name: ", item_name, len(''.join(item_name.split())))
                    print(">>> description: ", description, len(''.join(description.split())))

                    if len(''.join(item_name.split())) > 2 and len(''.join(description.split())) > 2:
                        print("Pass length test: ")
                        break
                    else:
                        print("Please enter at least 3 words for both item name and description.")

                except Exception as err:
                    print("ValueError: ", err)

            end_time = self.get_end_time_from_user()

            data_form = [item_name, description, end_time, email]
            new_data = {"type": "auction_creation", "data": data_form}

            self.sendServer(client, new_data)
            auction_info = self.recvServer2(client)
            if auction_info['content']['status'] is True:
                print(auction_info['content']['message'])
                self.auction_list.update(auction_info['content']['data'])
                # break
            elif auction_info['content']['status'] is False:
                print(auction_info['content']['message'])
            else:
                print("pass here....")
                pass
        # print('---->', auction_info['content']['data'])

        except Exception as err:
            print("auction_creation error:client: ", err)

    def auction_status(self, client):
        print("Auction status.")
        data = {'type': 'auction_status'}
        self.sendServer(client, data)
        try:
            result = self.recvServer2(client)
            # print(result)
            self.auction_list.clear()
            self.bids_list.clear()
            self.auction_status_show(result)
        except json.JSONDecodeError as json_err:
            print("JSON decoding error:", json_err)
        except Exception as e:
            print("Error processing server response:", e)

    def placing_bids(self, client):
        print("Placing bids")
        auth_info = self.auth_user_data_refine(self.auth_user)
        username = auth_info['username']
        email = auth_info['email']

        try:
            while True:
                auction_name = str(input("Enter Item Id or Item name: "))
                price_give = int(input("Enter Price (Note: price must be higher than current price): "))
                if auction_name and len(auction_name) > 3 or price_give > 0:
                    # print("auction name: ", auction_name, "price: ", price_give)
                    data_form = [username, email, auction_name, str(price_give)]
                    data = {"type": "placing_bids", "data": data_form}
                    self.sendServer(client, data)

                    result = self.recvServer2(client)
                    if 'content' in result:
                        if result['content']['status'] is True:
                            auction_update_data = result['content']['auction_data']
                            bids_update_data = result['content']['bid_data']
                            self.auction_list.update(auction_update_data)
                            self.bids_list.update(bids_update_data)
                            self.item_data_detail(data_form)
                            self.bids_data_show(data_form)
                            # break
                        else:
                            print(result['content']['message'])
                            # client.close()
                    break
                else:
                    print("Invalid auction name and price: ")
        except ValueError as err:
            print("Invalid input. Please enter a valid number.", err)

    def exit_program(self, client):
        new_data = {"type": "exit", "data": ["Bye Bye ...."]
                    # ,"auction_update": self.auction_list,
                    # "bids_update": self.bids_list
                    }

        self.sendServer(client, new_data)
        # print(self.recvServer2(client))
        client.close()
        sys.exit(0)

    def sendServer(self, client, data):
        json_string = json.dumps(data)
        encrypted_data = self.a3E.start_encryption(json_string, self.getting_key())
        content = bytes(encrypted_data, "utf-8")
        client.send(content)

    def recvServer(self, client):
        from_client = client.recv(1024)
        encrypted_data = from_client.decode("utf-8")
        decrypted_data = self.a3D.startDecryption(encrypted_data)
        result = json.loads(decrypted_data)
        # print('result: ', result, 'type: ', type(result))
        return result

    def recvServer2(self, client):
        try:
            # Initialize an empty string to store the received data
            received_data = ""
            while True:
                # Receive data in chunks
                chunk = client.recv(4096)
                # Break the loop if no more data is received
                if not chunk:
                    break
                # Decode and append the chunk to the received data
                received_data += chunk.decode("utf-8")
            # Decrypt the received data
            decrypted_data = self.a3D.startDecryption(received_data)
            # Parse the decrypted data as JSON
            result = json.loads(decrypted_data)
            return result
        except Exception as e:
            print("Error receiving data from the server:", e)
            return None

    def print_menu(self):
        print("1. Register User")
        if self.auth_user:
            print("2. Profile")
        else:
            print("2. Login")
        print("3. Place Bid")
        print("4. Create Auction")
        print("5. Exit")
        print("6. Auction Status")
        if self.auth_user != {}:
            print("7. Logout")
        if self.auth_user != {}:
            print("8. Delete Auctions")
        if self.auth_user != {}:
            print("9: Deactivate and remove account.")

    def get_end_time_from_user(self):
        while True:
            try:
                end_time_date = input(
                    "Enter the end date (YYYY-MM-DD, or press Enter for default today): ")
                end_time_min = input(
                    "Enter the end time (H:M, or press Enter for default current time + 1 hour): ")

                # Set default date to current date if not provided
                end_time_date = end_time_date if end_time_date else datetime.now().strftime("%Y-%m-%d")

                # Set default time to current time + 1 hour if not provided
                current_time = datetime.now()
                default_time = current_time + timedelta(hours=1)
                end_time_min = end_time_min if end_time_min else default_time.strftime("%H:%M")

                end_time = f"{end_time_date} {end_time_min}"

                end_time_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

                # Validate if end time is not earlier than the current time
                if end_time_dt < datetime.now():
                    print(end_time_dt, datetime.now())
                    print(
                        "Error: Please enter an end date and time that is not earlier than the current date and time.")
                    continue  # Ask the user to input again

                return end_time_dt.strftime("%Y-%m-%d %H:%M:%S")  # Return the format string
            except ValueError:
                print("Invalid date or time format. Please use YYYY-MM-DD for the date and H:M for the time.")

    def item_data_detail(self, data):
        username = data[0]
        email = data[1]
        auction_name = data[2]
        price_give = data[3]
        for k, v in self.auction_list.items():
            if auction_name == v['item_name'] or auction_name == v['item_id']:
                print("Found Item.")
                end_time = v['end_time']
                user_bid = v['username_bid']
                email_bid = v['email_bid']  # current owner email
                current_price = '$' + str(v['highest_price_bid']) if v['highest_price_bid'] else 0
                end_time = str('Event Expire' if not time_remaining(end_time) else time_remaining(end_time))

                print("+----------------------------------------------------------+")
                print(f"| >>>>{'Item Detail':<52} |")
                print("+----------------------------------------------------------+")
                print(f"| Item Id:                  {v['item_id']:<30} |")
                print("+----------------------------------------------------------+")
                print(f"| Item Name:                {v['item_name']:<30} |")
                print("+----------------------------------------------------------+")
                print(f"| Description :             {v['description']:<30} |")
                print("+----------------------------------------------------------+")
                print(f"| Current price (highest):  {current_price:<30} |")
                print("+----------------------------------------------------------+")
                print(f"| Current person (owner):   {user_bid:<30} |")
                print("+----------------------------------------------------------+")
                print(f"| Expire In:                {end_time:<30} |")
                print("+----------------------------------------------------------+")

                # print("\n", "--" * 50, "\n")

    def bids_data_show(self, data):
        username = data[0]
        email = data[1]
        auction_name = data[2]
        price_give = data[3]
        print("+-----------------------Bids History-----------------------+")
        for k, v in self.bids_list.items():
            if auction_name == v['auction_name']:
                history = f"| [{v['username_bid']}] give price [${v['highest_price_bid']}] for [{v['auction_name'] + ']':<27}  "
                print(history)
        print("+----------------------------------------------------------+")

    def auction_status_show(self, result):
        if 'content' in result:
            user_data = result['content']['user_data']
            auction_data = result['content']['auction_data']
            bid_data = result['content']['bid_data']

            self.auction_list.update(auction_data)
            self.bids_list.update(bid_data)

            # self.auction_list.update(result['content'])
            print("\n", "--" * 85)
            print(f"|{'ItemId':<30} | "
                  f"{'item_name':<30} | {'end_time':<30} | {'current price(highest)':<30} | {'current person(owner)':<30} ")
            print("--" * 85)

            if self.auction_list:
                for k, v in self.auction_list.items():
                    item_id, item_name, end_time, username_bid, email_bid, price = \
                        (v['item_id'], v['item_name'], v['end_time'], v['username_bid'], v['email_bid'],
                         v['highest_price_bid'])
                    price = '$' + str(price)
                    end_time = str(time_remaining(end_time) if time_remaining(end_time) else 'Event Expire.')
                    username_bid = username_bid if username_bid else "unavailable user"
                    email_bid = email_bid if email_bid else "unavailable address"

                    print(f"| {item_id:<30} | {item_name:<30} | {end_time:<30} | {price:<30} | {username_bid:<30}")
            else:
                print(f"{'':<60} Empty Data {'':<60}")

            print("--" * 85, "\n")
        else:
            print("Error: Empty or invalid response from the server.")

    def profile_info(self, data):
        try:
            data = self.auth_user
            if data:
                for k, v in data.items():
                    print("\n")
                    print("+", "-" * 50, "+")
                    print(f"| {'Profile Info':>30}")
                    print("+", "-" * 50, "+")
                    print(f"| username:         {v['username']:<30} ")
                    print("+", "-" * 50, "+")
                    print(f"| email:            {v['email']:<30} ")
                    print("+", "-" * 50, "+")
                    print(f"| address:          {v['address']:<30} ")
                    print("+", "-" * 50, "+")
                    print(f"| phone number:     {v['phone_number']:<30} ")
                    print("+", "-" * 50, "+")
                    print(f"| content:          {v['content']:<30} ")
                    print("+", "-" * 50, "+")
                self.auctions_of_creator(self.auction_list)
        except Exception as profile_err:
            print("Profile err: ", profile_err)

    def auth_each_info(self):
        result = []
        if self.auth_user:
            for k, v in self.auth_user.items():
                result = v
        return result

    def auctions_of_creator(self, data):
        try:
            data = self.auction_list
            aoc_flag = False
            boc_flag = False
            flag_1 = False

            for k, v in data.items():
                if self.auth_each_info().get('email') == v['email']:
                    flag_1 = True

            print("--" * 85)
            print(f"{'':<70} Your Auction Lists And Its Bidders {'':<60}")
            print("--" * 85)
            if flag_1 is True:
                print(f"|{'ItemId':<25} | "
                      f"{'item_name':<25} | "
                      f"{'end_time':<25} | "
                      f"{'auction owner':<25} | "
                      f"{'current price(highest)':<25} | "
                      f"{'current person(owner)':<25} ")
                print("--" * 85)
                for k, v in data.items():
                    if self.auth_each_info().get('email') == v['email']:
                        item_id, item_name, end_time, owner_auction_mail, username_bid, email_bid, price = \
                            (v['item_id'], v['item_name'], v['end_time'], v['email'], v['username_bid'], v['email_bid'],
                             v['highest_price_bid'])
                        price = '$' + str(price)
                        end_time = str(time_remaining(end_time) if time_remaining(end_time) else 'Event Expire.')
                        username_bid = username_bid if username_bid else "unavailable user"
                        email_bid = email_bid if email_bid else "unavailable address"
                        print(
                            f"| {item_id:<25} | {item_name:<25} | {end_time:<25} | {owner_auction_mail:<25} | {price:<25} | {username_bid:<25}")

                        print("+-----------------------Bids History-----------------------+")
                        for a, b in self.bids_list.items():
                            if 'auction_name' in b:
                                auction_name = b['auction_name']
                                if item_name == auction_name or item_id == auction_name:
                                    # print(b)
                                    history = f"| [{b['username_bid']}] give price [${b['highest_price_bid']}] for {auction_name:<27}  "
                                    print(history)
                                    print("+----------------------------------------------------------+")
                                    boc_flag = False
                                else:
                                    boc_flag = True

                        print(f">>>not up to data..? [Please Refresh Auction Status]")
                        aoc_flag = False
                        print("--" * 85)
                        # break
                    else:
                        aoc_flag = True
            else:
                print(f"{'':<70} Empty Data. Please Reload(auction status) or Create new Auction {'':<60}")
                print("--" * 85, "\n")

            if aoc_flag is True:
                pass
                # print(f"{'':<70} Create Auctions First. {'':<60}")
                # print("--" * 85, "\n")

            if boc_flag is True:
                pass
                # print(f"{'':<70} No Bidders here. {'':<60}")
                # print("--" * 85, "\n")

        except Exception as acerror:
            print("auction creator: ", acerror)

    def auctions_delete(self, client):
        print("work delete 2.")
        while True:
            auction_name = str(input("Enter auction name or id to remove: "))
            if len(''.join(auction_name.split())) > 2:
                break
            else:
                print("Invalid auction name.")

        email = self.auth_each_info().get('email')
        data_form = [auction_name, email]
        data = {"type": "auction_delete", "data": data_form}
        self.sendServer(client, data)
        result = self.recvServer2(client)
        if 'content' in result:
            if result['content']['status'] is True:
                print(result['content']['message'])
                auction_data = result['content']['auction_data']
                bid_data = result['content']['bid_data']

                self.auction_list.clear()
                self.bids_list.clear()
                self.auction_list.update(auction_data)
                self.bids_list.update(bid_data)
            else:
                print(result['content']['message'])

    def user_delete_acc(self, client):
        try:
            while True:
                email = self.auth_each_info().get('email')
                data_form = [email]
                confirm = str(input("Confirm to delete acc.(yes/no)"))
                if confirm.lower() == 'yes':
                    data = {"type": "user_delete", "data": data_form}
                    self.sendServer(client, data)
                    result = self.recvServer2(client)
                    if 'content' in result:
                        if result['content']['status'] is True:
                            print(result['content']['message'])
                            self.auth_user.clear()
                        else:
                            print(result['content']['message'])
                    break
                elif confirm.lower() == 'no':
                    print("user account deletion cancel.")
                    break
                else:
                    print("invalid choice.")

        except Exception as udaErr:
            print("user delete error: ", udaErr)


if __name__ == "__main__":
    auction_client: Client = Client()
    while True:
        auction_client.client_menu()
