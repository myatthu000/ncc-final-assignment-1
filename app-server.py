import json
import random
import socket
import sys
import threading

import fileHandling
from fileHandling import *
import s_encrypt_and_decrypt
import my_validation
import my_modules
from my_modules import time_remaining


class Server:

    def __init__(self):
        self.a3E = s_encrypt_and_decrypt.A3Encryption()
        self.a3D = s_encrypt_and_decrypt.A3Decryption()

        self.r2 = my_validation.Validation()

        self.file_use = fileHandling.FileHandling()
        self.file_use.create_files()
        self.file_use.load_data()

        self.users = self.file_use.users
        self.auctions = self.file_use.auctions
        self.bids = self.file_use.bids

        self.default_key = "myatmyat"
        self.server_ip = "localhost"
        self.server_port = 9191
        self.index = 1

    def getting_key(self):
        # userKey: str = input("Enter your encryption key for the whole process:")
        userKey: str = self.default_key
        return userKey

    def main(self):
        auction_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        auction_server.bind((self.server_ip, self.server_port))
        auction_server.listen()
        print("Server listen on port:{} and ip{}".format(self.server_port, self.server_ip))
        try:
            while True:
                client, address = auction_server.accept()
                print("Accepted Connection from -{} : {}".format(address[0], address[1]))

                # self.client_control(client)
                # Create a new thread for each client
                client_thread = threading.Thread(target=self.client_control, args=(client,))
                client_thread.start()

        except Exception as err:
            print(err)

    def client_control(self, client):
        to_client = None
        with client as sock:
            try:
                data = self.recvClient(sock)
                print("----->", data)

                if 'type' in data:

                    if data['type'] == 'register':
                        to_client = self.register_server(sock, data)
                    elif data['type'] == 'login':
                        to_client = self.login_server(sock, data)
                        # print("to_client: ", to_client)
                    elif data['type'] == 'auction_creation':
                        to_client = self.auction_creation_server(sock, data)
                    elif data['type'] == 'auction_status':
                        to_client = self.auction_status_server()
                        # print("to_client: ", to_client)
                    elif data['type'] == 'placing_bids':
                        to_client = self.placing_bids_server(sock, data)
                    elif data['type'] == 'auction_delete':
                        to_client = self.auctions_delete_server(sock, data)
                    elif data['type'] == 'user_delete':
                        to_client = self.user_delete_acc_server(sock, data)
                    elif data['type'] == 'exit':
                        # print("Exit program.")
                        self.exit_program(sock, data)
                        sock.close()
                        if threading.active_count() == 2:  # Only the main thread and the server thread are active
                            print("Last client has exited. Shutting down the server.")
                            sys.exit(0)
                    else:
                        print("Invalid option: ", data)
                else:
                    print("Invalid data format: ", data)

                print(to_client)
                if to_client is not None:
                    sms = {"content": to_client}
                    self.sendClient(sock, sms)
                    print("send to client: ", sms)

            except json.JSONDecodeError as json_err:
                print("JSON decoding error:", json_err)
            except Exception as e:
                pass
                # print("Error processing client data:", e)

    def auction_status_server(self):
        self.file_use.load_data()
        auction_data = self.file_use.auctions
        bid_data = self.file_use.bids
        user_data = self.file_use.users
        # print("auction status work: ", self.auctions)
        result = {"auction_data": auction_data, "bid_data": bid_data, 'user_data': user_data}
        return result

    def placing_bids_server(self, sock, data):
        global send_data
        print("placing_bids: ", data)
        bids_flag = False
        item_flag = False
        username_bids_client = data['data'][0]
        email_bid_client = data['data'][1]
        auction_name = data['data'][2]
        price_give = data['data'][3]

        for k, v in self.file_use.auctions.items():
            if auction_name == v['item_name'] or auction_name == v['item_id']:
                print("Found Item.-->", v)
                item_flag = True
                end_time = v['end_time']
                print("--->Item expired in: ", time_remaining(end_time), type(time_remaining(end_time)))
                if email_bid_client != v['email']:
                    # print("email bid client")
                    if str(time_remaining(end_time)) != "0:00:00":
                        # print("end time check")
                        if int(price_give) > int(v['highest_price_bid']):
                            # print("price check")
                            v['highest_price_bid'] = price_give

                            # print("work here...")
                            data_form_bid = {"auction_name": auction_name,
                                             # "auction_owner_email": v['email'],
                                             # "auction_owner_name": v['username'],
                                             "username_bid": username_bids_client,
                                             "email_bid": email_bid_client,
                                             "highest_price_bid": v['highest_price_bid']}

                            key_id = my_modules.key_id() + str(len(self.bids))
                            self.file_use.bids.update({key_id: data_form_bid})
                            self.file_use.save_files_bids(self.file_use.bids)
                            v.update(
                                {"username_bid": username_bids_client,
                                 "email_bid": email_bid_client,
                                 "highest_price_bid": v['highest_price_bid']})

                            self.file_use.save_files_auction(self.file_use.auctions)
                            print('======', v)
                            bids_flag = True
                            break
                        else:
                            info = "Given Price must be higher than the current price. current price is {}".format(
                                v['highest_price_bid'])
                            send_data = {"status": bids_flag, 'message': info}
                            print(info)
                    else:
                        info = "Event Expire."
                        send_data = {"status": bids_flag, 'message': info}
                        print(info)
                else:
                    info = "You cannot give price your own Item."
                    send_data = {"status": bids_flag, 'message': info}
                    print(info)

                break
            else:
                item_flag = False

        if not item_flag:
            info = "Item Not found"
            send_data = {"status": bids_flag, 'message': info}
            print(info)

        if bids_flag is True:
            self.file_use.load_data()
            auction_data = self.auctions
            bid_data = self.bids
            info = "Bid placed successfully."
            send_data = {"status": bids_flag, 'message': info, "auction_data": auction_data, "bid_data": bid_data}
            print(send_data)

        return send_data

    def auction_creation_server(self, sock, data):
        print("from auction server: ", data)
        try:
            item_name: str = data['data'][0]
            description: str = data['data'][1]
            end_time: str = data['data'][2]
            email: str = data['data'][3]
            uuid: str = str(random.randint(1111, 9999)) + str(my_modules.current_time_milliseconds())[-5:]  # for user

            data_form = {
                "item_id": uuid,
                "item_name": item_name,
                "description": description,
                "end_time": end_time,
                "email": email,  # owner of item
                "username_bid": "unknown user",  # current username who give highest price
                "email_bid": "unknown email",  # current email of its username
                "highest_price_bid": "0",  # current price
            }

            result2 = self.r2.auction_validation_check_in_db(data, self.auctions)
            print(result2)
            if result2['item_name_check'] == -1:
                key_id = my_modules.key_id() + str(len(self.auctions))
                self.file_use.auctions.update({key_id: data_form})
                self.file_use.save_files_auction(self.file_use.auctions)
                print('auction: ', self.file_use.auctions)
                self.file_use.load_data()
                print('update auction: ', self.file_use.auctions)
                send_data = {"status": True, "message": "auction creation success.", "data": self.auctions}
            else:
                send_data = {"status": False, "message": "Invalid auction creation."}

        except Exception as err:
            print("server auction error: ", err)
            send_data = {"status": False, "message": "something wrong in auction creation."}

        return send_data

    def register_server(self, sock, data):
        try:
            name = data['data'][0]
            email = data['data'][1]
            password = data['data'][2]
            address = data['data'][3]
            phone_number = str(data['data'][4])
            content = data['data'][5]
            uuid = data['data'][6]
            data_form = {"uuid": uuid,
                         "username": name,
                         "email": email,
                         "password": password,
                         "address": address,
                         "phone_number": phone_number,
                         "content": content}

            result1 = self.r2.validation_register(data)
            if result1 is False:
                send_data = "register validation fail."
            else:
                result2 = self.r2.validation_check_in_db(data, self.users)
                print(result2)
                if result2['email_check'] == -1 and result2['phone_check'] == -1:
                    key_id = my_modules.key_id() + str(len(self.users))
                    self.file_use.users.update({key_id: data_form})
                    self.file_use.save_files_users(self.file_use.users)
                    print('users: ', self.file_use.users)
                    send_data = "register successfully."
                else:
                    send_data = "already register."
        except Exception as err:
            print("server register error: ", err)
            send_data = "something wrong in registration."

        return send_data

    def login_server(self, sock, data):
        try:
            self.file_use.load_data()
            email = data['data'][0]
            password = data['data'][1]
            data_form = {"email": email, "password": password}

            result1 = self.r2.validation_login(data)
            if result1 is False:
                send_data = {"message": "login validation fail.", "status": False}
            else:
                result2 = self.r2.login_check(data, self.users)
                if result2:
                    # User successfully logged in
                    print('---->result2 from server: ', result2)
                    data = {'auth_info': result2,
                            "status": True,
                            "auction_data": self.file_use.auctions,
                            "bid_data": self.file_use.bids}
                    send_data = data
                else:
                    # Empty result2, indicating login failure
                    send_data = {"message": "login fail: invalid credentials.", "status": False}

        except Exception as err:
            print("server login error: ", err)
            send_data = {"message": "server: something wrong in login.", "status": False}

        print('result2 from server: ', send_data)
        return send_data

    def sendClient(self, sock, data):
        json_string = json.dumps(data)
        encrypted_data = self.a3E.start_encryption(json_string, self.getting_key())
        content = bytes(encrypted_data, "utf-8")
        sock.send(content)

    def recvClient(self, sock):
        from_client = sock.recv(1024)
        encrypted_data = from_client.decode("utf-8")
        decrypted_data = self.a3D.startDecryption(encrypted_data)
        result = json.loads(decrypted_data)
        return result

    def recvClient2(self, sock):
        try:
            # Initialize an empty string to store the received data
            received_data = ""
            while True:
                # Receive data in chunks
                chunk = sock.recv(4096)
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

    def auctions_delete_server(self, sock, data):
        print(data)
        auction_name = data['data'][0]
        email = data['data'][1]  # authenticated user email
        keys_to_remove_auction = []
        keys_to_remove_bid = []

        auction_found = False

        for k, v in self.file_use.auctions.items():
            print(f"Checking auction: {v['item_name']} owned by {v['email']}")
            if (v['item_name'] == auction_name or v['item_id'] == auction_name) and v['email'] == email:
                auction_found = True
                break

        if not auction_found:
            print("Item not found.")
            return {"status": False, "message": "Item not found for deletion"}

        for i, j in self.file_use.bids.items():
            if j['auction_name'] == auction_name:
                keys_to_remove_bid.append(i)

        for k, v in self.file_use.auctions.items():
            if (v['item_name'] == auction_name or v['item_id'] == auction_name) and v['email'] == email:
                keys_to_remove_auction.append(k)
                break

        for key in keys_to_remove_auction:
            self.file_use.auctions.pop(key)
            self.file_use.save_files_auction(self.file_use.auctions)
            self.file_use.load_data()

        for key in keys_to_remove_bid:
            self.file_use.bids.pop(key)
            self.file_use.save_files_bids(self.file_use.bids)
            self.file_use.load_data()

        data = {"status": True,
                "message": "Successfully deleted.",
                "auction_data": self.auctions,
                "bid_data": self.bids}
        print(data)
        return data

    def exit_program(self, sock, data):
        print(data)
        print("Exit ...")
        print("Client at {}:{} is exiting.".format(sock.getpeername()[0], sock.getpeername()[1]))
        # if data['auction_update'] and data['bids_update']:
        #     self.file_use.auctions.update(data['auction_update'])
        #     self.file_use.bids.update(data['bids_update'])
        # else:
        #     print("no need to update....")

        # new_data = "Bye Bye from server ...."
        # return new_data

    def user_delete_acc_server(self, sock, data):
        email = data['data'][0]
        # auction_name_ = ''
        item_name_to_remove_bid = []
        keys_to_remove_user = []
        keys_to_remove_auction = []
        keys_to_remove_bid = []

        user_found = False
        auction_found = False

        for k, v in self.file_use.users.items():
            print(f"Checking auction: {v['username']} owned by {v['email']}")
            if v['email'] == email:
                user_found = True
                break

        if not user_found:
            return {"status": False, "message": "User not found for deletion"}

        for a, b in self.file_use.users.items():
            if b['email'] == email:
                keys_to_remove_user.append(a)
                break

        for k, v in self.file_use.auctions.items():
            if v['email'] == email:
                item_name_to_remove_bid.append(v['item_name'])
                keys_to_remove_auction.append(k)

        for i, j in self.file_use.bids.items():
            if j['auction_name'] in item_name_to_remove_bid:
                keys_to_remove_bid.append(i)

        for key in keys_to_remove_user:
            self.file_use.users.pop(key)
            self.file_use.save_files_users(self.file_use.users)
            self.file_use.load_data()

        for key in keys_to_remove_auction:
            self.file_use.auctions.pop(key)
            self.file_use.save_files_auction(self.file_use.auctions)
            self.file_use.load_data()

        for key in keys_to_remove_bid:
            self.file_use.bids.pop(key)
            self.file_use.save_files_bids(self.file_use.bids)
            self.file_use.load_data()

        data = {"status": True,
                "message": "Successfully deleted."}

        return data

    def counter(self):
        self.index += 1
        return self.index


if __name__ == "__main__":
    auction: Server = Server()
    # auction.file_use.create_files()
    auction.main()
