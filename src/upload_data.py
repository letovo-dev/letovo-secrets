import pandas
import hashlib
import requests
import os

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DataUploader():
    _file_path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'example upload.xlsx'))
    _data = pandas.DataFrame()
    # TODO: спрятать
    _credentials = {
        "login": "scv-7",
        "password": "7"
    }
    _auth_url = "https://0.0.0.0:8080/auth/login/"
    _is_user_url = "https://0.0.0.0:8080/auth/isuser/"
    _create_user = "https://0.0.0.0:8080/auth/reg/"
    _add_role = "https://0.0.0.0:8080/auth/add_userrights/"
    _department = "https://0.0.0.0:8080/user/set_department/"
    _token = ""
    _uploaded_data = pandas.DataFrame({
        "ФИО": [],
        "login": [],
        "role": [],
        "department": [],
        "password": []
    })

    def __init__(self):
        self._authorize()
        self._add_role += self._token

    @property
    def file_path(self):
        return self._file_path
    
    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        self._data = value

    def _authorize(self):
        self._token = requests.post(self._auth_url, json=self._credentials, verify=False).json()["token"]

    def _user_to_server(self, login: str, password: str):
        responce = requests.post(self._create_user, json={"login": login, "password": password}, verify=False)
        if responce.status_code != 200:
            return responce.status_code
        return login

    def _add_rights_to_user(self, login: str, role: str):
        print("-------", f"'{login} : {role}'", "-------")
        responce = requests.put(self._add_role, json={"username": login, "rights": role}, verify=False)
        if responce.status_code != 200:
            return responce.status_code
        return login

    def _set_department(self, login: str, department: str):
        print("-------", f"'{department}'", "-------")
        response = requests.put(self._department, json={
            "username": login, 
            "department": department, 
            "token": self._token
        }, verify=False)
        if response.status_code != 200:
            return str(response.status_code) + " " + response.text
        return login

    def _read_data(self):
        self.data = pandas.read_excel(self.file_path).fillna("")

    def check_bad_words(self, text: str) -> bool:
        return False

    def check_login(self, login: str) -> bool:
        if login is None or login == "":
            return False
        response = requests.get(self._is_user_url + str(login), verify=False)
        if response.status_code == 200:
            return True
        if self.check_bad_words(login):
            return False
        return True

    def _parse_data(self):
        parsed_data = []
        for player in self.data.iterrows():
            player_data = {}
            for key, value in player[1].items():
                if not value:
                    value = ""
                player_data[key] = value
            parsed_data.append(player_data)
        self.data = parsed_data

    def _upload_player(self, player: dict):
        _temp_login = player["Логин"]
        _temp_password = ""
        _temp_department = ""
        _temp_role = ""
        if not self.check_login(player["Логин"]):
            _temp_login = hashlib.md5(player["ФИО"].encode()).hexdigest()[:8]
            _temp_password = hashlib.md5(player["ФИО"].encode()).hexdigest()[8:16]
            _temp_login = self._user_to_server(_temp_login, _temp_password)
        if "Роль" in player and player["Роль"] and player["Роль"] != "":
            _temp_role = self._add_rights_to_user(_temp_login, player["Роль"])
        if "Департамент" in player and player["Департамент"] and player["Департамент"] != "":
            _temp_department = self._set_department(_temp_login, player["Департамент"])

        self._uploaded_data.loc[len(self._uploaded_data)] = {
            "ФИО": player["ФИО"],
            "login": _temp_login,
            "role": _temp_role,
            "department": _temp_department,
            "password": _temp_password
        }
    def save_file(self):
        pandas.DataFrame.from_dict(self._uploaded_data).to_excel(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploaded.xlsx')))
        return os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploaded.xlsx'))

                

if __name__ == "__main__":
    print(os.path.dirname(os.path.abspath(__file__)))
    uploader = DataUploader()
    uploader._read_data()
    uploader._parse_data()
    print(uploader.data)
    for d in uploader.data:
        uploader._upload_player(d)
    file = uploader.save_file()
    print(pandas.read_excel(file).head())