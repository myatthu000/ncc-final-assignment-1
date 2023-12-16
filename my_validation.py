import re


class Validation:
    def __init__(self):
        self.start = 1

    '''
    Register validation start
    '''

    def validation_register(self, new_data):
        flag = False
        name = new_data['data'][0]
        email = new_data['data'][1]
        password = new_data['data'][2]
        address = new_data['data'][3]
        phone_no = new_data['data'][4]
        content = new_data['data'][5]
        if (self.is_valid_email(email)
                and self.is_strong_password(password)
                and self.is_valid_name(name)
                and self.is_valid_address(address)
                and self.is_valid_content(content)
                and self.is_valid_phone_number(phone_no)):
            flag = True
            print("\n>>>>register validation pass: ", flag)
        else:
            print("\n>>>register validation fail: ", flag)

        return flag  # edit for testing purpose

    def validation_check_in_db(self, new_data, data):
        email_exit_flag = -1  # not exit
        phone_exit_flag = -1  # not exit
        email = new_data['data'][1]
        phone = str(new_data['data'][4])
        # print(email,phone)
        for key, value in data.items():
            if email == value['email']:
                print("email already exit: key:{} value:{}".format(key, value['email']))
                email_exit_flag = 1  # email exit
                break
            if phone == value['phone_number']:
                print("phone already exit: key:{} value:{}".format(key, value['phone_number']))
                phone_exit_flag = 1  # phone exit
                break
        # print("email exit check: ", email, email_exit_flag, "phone exit check: ", phone, phone_exit_flag)
        result = {"email_check": email_exit_flag, "phone_check": phone_exit_flag}
        return result

    '''
    Login validation start
    validation_login method: return True or False if its email is valid
        and password is strong
    login check method: return data_form if its email and password is correct
    '''

    def validation_login(self, new_data):
        flag = False
        email = new_data['data'][0]
        password = new_data['data'][1]

        if self.is_valid_email(email) and self.is_strong_password(password):
            flag = True
            print(">>>login validation pass: ", flag)
        else:
            print(">>>login validation fail: ", flag)

        return flag  # edit for testing purpose

    def login_check(self, login_data, data):
        email_exit_flag = -1  # not exit
        pass_exit_flag = -1  # not exit
        data_form = {}
        email = login_data['data'][0]
        password = login_data['data'][1]
        print("------> ",email, password)
        for key, value in data.items():
            if email == value['email']:
                # print("key:{} value:{} ".format(key, value))
                email_exit_flag = 1
                if password == value['password']:
                    pass_exit_flag = 1
                    data_form.update({key: value})
                    print("------> ", email, password)
                    break

        # print(data_form)
        print("email exit check: ", email, email_exit_flag, "phone exit check: ", password, pass_exit_flag)
        if (email_exit_flag == -1 and pass_exit_flag == -1) or (email_exit_flag == -1 or pass_exit_flag == -1):
            return {}
        else:
            print("validation ------> ", data_form)
            return data_form

    '''
    Auction validation method: check in db if item_name is already exit or not.
    if it exit return 1 and else -1
    '''

    def auction_validation_check_in_db(self, new_data, data):
        item_exit_flag = -1  # not exit
        time_end_flag = -1  # not exit

        item_name: str = new_data['data'][0]
        description: str = new_data['data'][1]
        end_time: str = new_data['data'][2]
        uuid: str = new_data['data'][3]

        # print(email,phone)
        for key, value in data.items():
            if item_name == value['item_name']:
                print("Item already exit: key:{} value:{}".format(key, value['email']))
                item_exit_flag = 1  # email exit
                break

        # print("item_name check": item_exit_flag, item_name)
        result = {"item_name_check": item_exit_flag}
        return result

    '''
    Here is small validation check methods of each columns
    '''

    def is_valid_email(self, email):
        # checking if it contains @gmail, @outlook ....
        result = bool(re.match(r'\b[A-Za-z0-9._%+-]+@(gmail|outlook)\.[A-Z|a-z]{2,}\b', email))
        if not result:
            print("----email : ", email, bool(result))
        return result

    def is_strong_password(self, password):
        result = len(password) >= 6 and any(char.islower() for char in password) and any(
            char.isupper() for char in password) and not any(char.isspace() for char in password)
        if not result:
            print("----password: ", password, bool(result))
        return result

    def is_valid_phone_number(self, phone_number):
        result = bool(re.match(r'^\d{7,13}$', phone_number))
        if not result:
            print("----phone number: ", phone_number, result)
        return result

    def is_valid_name(self, name):
        result = bool(
            re.match(r'^[A-Za-z0-9\s]+$', name)
            and len(name) >= 3)
        if not result:
            print("\ncan only accept with alphabet, numeric and white space"
                  "\n----name: ", name, result, "\n")
        return result

    def is_valid_content(self, content):
        result = bool(content.strip())
        if not result:
            print("----content: ", content, result)
        return result

    def is_valid_address(self, address):
        print("----address: ", address)
        return True  # edit for testing purpose

# r2 = Validation()