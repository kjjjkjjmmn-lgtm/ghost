import requests, os, psutil, sys, jwt, pickle, json, binascii, time, urllib3, base64, datetime, re, socket, threading
import random
from protobuf_decoder.protobuf_decoder import Parser
from xP import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Lock, Event
from flask import Flask, request, jsonify
from Pb2 import MajoRLoGinrEq_pb2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

# ================== مفاتيح التشفير ==================
AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# ================== دوال التشفير ==================
def encAEs(hexStr):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(bytes.fromhex(hexStr), AES.block_size)).hex()

def decAEs(hexStr):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return unpad(cipher.decrypt(bytes.fromhex(hexStr)), AES.block_size).hex()

def encPacket(hexStr, k, iv):
    return AES.new(k, AES.MODE_CBC, iv).encrypt(pad(bytes.fromhex(hexStr), 16)).hex()

def decPacket(hexStr, k, iv):
    return unpad(AES.new(k, AES.MODE_CBC, iv).decrypt(bytes.fromhex(hexStr)), 16).hex()

# ================== بناء البايلود باستخدام Pb2 ==================
def build_major_login_payload(open_id, access_token, platform_id=2):
    """بناء بايلود MajorLogin باستخدام Protobuf من Pb2"""
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    
    # تعبئة الحقول
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = platform_id
    major_login.client_version = "1.126.1"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019116753"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    
    # Serialize إلى bytes
    protobuf_raw = major_login.SerializeToString()
    
    # طباعة Protobuf RAW (اختياري - للإيضاح)
    print(f"\n📦 Protobuf RAW (Hex):")
    print(protobuf_raw.hex())
    print("="*60)
    
    # تشفير باستخدام AES
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded = pad(protobuf_raw, AES.block_size)
    encrypted = cipher.encrypt(padded)
    
    # طباعة Encrypted Payload (اختياري - للإيضاح)
    print(f"\n🔐 Encrypted Payload (Hex):")
    print(encrypted.hex())
    print("="*60)
    
    return encrypted, protobuf_raw.hex()

socket_lock = Lock()
data_lock = Lock()
connected_clients = {}
connected_clients_lock = threading.Lock()

app = Flask(__name__)

def generate_random_color():
    color_list = [
        "[00FF00][b][c]", "[FFDD00][b][c]", "[3813F3][b][c]", "[FF0000][b][c]",
        "[0000FF][b][c]", "[FFA500][b][c]", "[DF07F8][b][c]", "[11EAFD][b][c]",
        "[DCE775][b][c]", "[A8E6CF][b][c]", "[7CB342][b][c]", "[FFB300][b][c]",
        "[90EE90][b][c]", "[FF4500][b][c]", "[FFD700][b][c]", "[32CD32][b][c]",
        "[87CEEB][b][c]", "[9370DB][b][c]", "[FF69B4][b][c]", "[8A2BE2][b][c]",
        "[00BFFF][b][c]", "[1E90FF][b][c]", "[20B2AA][b][c]", "[00FA9A][b][c]",
        "[008000][b][c]", "[FFFF00][b][c]", "[FF8C00][b][c]", "[DC143C][b][c]"
    ]
    return random.choice(color_list)

class FF_CLient():
    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.thread_pool = ThreadPoolExecutor(max_workers=20)
        self.active_threads = []
        self.thread_timeout = 30
        self.InPuTMsG = ""
        self.DeCode_CliEnt_Uid = ""
        self.CliEnts = None
        self.CliEnts2 = None
        
        with connected_clients_lock:
            connected_clients[self.id] = self
        
        self.Get_FiNal_ToKen_0115()
        
    def GeTinFoSqMsG(self, teamcode):
        try:
            if hasattr(self, 'CliEnts2') and self.CliEnts2:
                self.CliEnts2.send(JoinSq(teamcode, self.key, self.iv))
                time.sleep(1)
                
                if hasattr(self, 'DaTa2') and len(self.DaTa2.hex()) > 4 and '0500' in self.DaTa2.hex()[0:4]:
                    dT = json.loads(DeCode_PackEt(self.DaTa2.hex()[10:]))
                    if '5' in dT and 'data' in dT["5"]:
                        idT = dT["5"]["data"]["1"]["data"]
                        if '14' in dT["5"]["data"] and 'data' in dT["5"]["data"]["14"]:
                            sq = dT["5"]["data"]["14"]["data"]
                        else:
                            sq = "1"
                        
                        self.CliEnts2.send(ExitSq('000000', self.key, self.iv))
                        time.sleep(0.2)
                        
                        return {"success": True, "team_id": idT, "sq": sq}
            
            return {"success": False}
            
        except Exception as e:
            return {"success": False}

    def SeNd_SpaM_MsG(self, team_id, sq, message):
        try:
            threads = []
            message_clients = list(connected_clients.values())[:3]
                
            for client in message_clients:
                thread = threading.Thread(target=self.SeNd_MsG, args=(client, team_id, sq, message))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join(timeout=30)
                
        except Exception as e:
            pass

    def SeNd_MsG(self, client, team_id, sq, message):
        try:
            if hasattr(client, 'CliEnts') and client.CliEnts:
                client.CliEnts.send(OpenCh(team_id, sq, client.key, client.iv))
                time.sleep(0.5)

                for i in range(100):
                    client.CliEnts.send(MsqSq(f'[b][c]{generate_random_color()}{message}', team_id, client.key, client.iv))
                    time.sleep(0.5)
                    
        except Exception as e:
            pass

    def Connect_SerVer_OnLine(self, Token, tok, host, port, key, iv, host2, port2):
        self.key = key
        self.iv = iv
        while True:
            try:
                self.CliEnts2 = socket.create_connection((host2, int(port2)))
                self.CliEnts2.send(bytes.fromhex(tok))                  
                
                while True:
                    try:
                        self.DaTa2 = self.CliEnts2.recv(99999)
                        if not self.DaTa2:
                            break
                        if len(self.DaTa2.hex()) > 4 and '0500' in self.DaTa2.hex()[0:4] and len(self.DaTa2.hex()) > 30:	         	    	    
                            self.packet = json.loads(DeCode_PackEt(f'08{self.DaTa2.hex().split("08", 1)[1]}'))
                            if '5' in self.packet and 'data' in self.packet['5'] and '7' in self.packet['5']['data'] and 'data' in self.packet['5']['data']['7']:
                                self.AutH = self.packet['5']['data']['7']['data']
                    except Exception as e:
                        break
                    
            except Exception as e:
                time.sleep(2)
                continue
                
    def cleanup_threads(self):
        current_time = time.time()
        self.active_threads = [t for t in self.active_threads 
                              if t['thread'].is_alive() and 
                              current_time - t['start_time'] < self.thread_timeout]
                                                              
    def Connect_SerVer(self, Token, tok, host, port, key, iv, host2, port2):
        self.key = key
        self.iv = iv
        try:
            self.CliEnts = socket.create_connection((host, int(port)))
            self.CliEnts.send(bytes.fromhex(tok))  
            self.DaTa = self.CliEnts.recv(1024)          
        except Exception as e:
            time.sleep(2)
            self.Connect_SerVer(Token, tok, host, port, key, iv, host2, port2)
            return
        
        secondary_thread = threading.Thread(target=self.Connect_SerVer_OnLine, args=(Token, tok, host, port, key, iv, host2, port2), daemon=True)
        secondary_thread.start()
               			      	

    def GeT_Key_Iv(self, serialized_data):
        try:
            import xK
            my_message = xK.MyMessage()
            my_message.ParseFromString(serialized_data)
            timestamp, key, iv = my_message.field21, my_message.field22, my_message.field23
            timestamp_obj = Timestamp()
            timestamp_obj.FromNanoseconds(timestamp)
            timestamp_seconds = timestamp_obj.seconds
            timestamp_nanos = timestamp_obj.nanos
            combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
            return combined_timestamp, key, iv            
        except Exception as e:
            return None, None, None

    def GuestLogin(self , uid , password):
        self.url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        self.headers = {"Host": "100067.connect.garena.com","User-Agent": "{Device}","Content-Type": "application/x-www-form-urlencoded","Accept-Encoding": "gzip, deflate","Connection": "close",}
        self.dataa = {"uid": f"{uid}","password": f"{password}","response_type": "token","client_type": "2","client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3","client_id": "100067",}
        try:
            self.response = requests.post(self.url, headers=self.headers, data=self.dataa).json()
            self.Access_ToKen , self.Access_Uid = self.response['access_token'] , self.response['open_id']
            
            # ✅ طباعة Open ID و Access Token
            print(f"\n✅ Open ID: {self.Access_Uid}")
            print(f"✅ Access Token: {self.Access_ToKen[:30]}...")
            
            time.sleep(0.2)
            return self.MajorLogin(self.Access_ToKen , self.Access_Uid)
        except Exception: 
            sys.exit()
                                        
    def DataLogin(self , JwT_ToKen , PayLoad):
        self.UrL = 'https://clientbp.ggpolarbear.com/GetLoginData'
        self.HeadErs = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JwT_ToKen}',
            'X-Unity-Version': '2022.3.47f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'clientbp.ggpolarbear.com',
            'Connection': 'close',
            'Accept-Encoding':  'gzip'}     
        try:
                self.Res = requests.post(self.UrL , headers=self.HeadErs , data=PayLoad , verify=False)
                self.DaTa_Pb2 = json.loads(DeCode_PackEt(self.Res.content.hex()))  
                address , address2 = self.DaTa_Pb2['32']['data'] , self.DaTa_Pb2['17']['data'] 
                ip , ip2 = address[:len(address) - 6] , address2[:len(address) - 6]
                port , port2 = address[len(address) - 5:] , address2[len(address2) - 5:]             
                return ip , port , ip2 , port2          
        except requests.RequestException as e:
                pass
        return None, None   

    def MajorLogin(self , Access_ToKen , Access_Uid):
        self.UrL = "https://loginbp.ggpolarbear.com/MajorLogin"
        self.HeadErs = {
            'X-Unity-Version': '2022.3.47f1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',    
            'X-GA': 'v1 1',
            'Content-Length': '928',
            'Host': 'loginbp.ggpolarbear.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'}   

        # ✅ بناء البايلود باستخدام Pb2 بدلاً من البايتس الثابتة
        encrypted_payload, protobuf_raw = build_major_login_payload(Access_Uid, Access_ToKen)
        self.PaYload = encrypted_payload
        
        self.ResPonse = requests.post(self.UrL, headers = self.HeadErs ,  data = self.PaYload , verify=False)        
        if self.ResPonse.status_code == 200 and len(self.ResPonse.text) > 10:
            self.DaTa_Pb2 = json.loads(DeCode_PackEt(self.ResPonse.content.hex()))
            self.JwT_ToKen = self.DaTa_Pb2['8']['data']           
            self.combined_timestamp , self.key , self.iv = self.GeT_Key_Iv(self.ResPonse.content)
            ip , port , ip2 , port2 = self.DataLogin(self.JwT_ToKen , self.PaYload)            
            return self.JwT_ToKen , self.key , self.iv, self.combined_timestamp , ip , port , ip2 , port2
        else:
            sys.exit()

    def Get_FiNal_ToKen_0115(self):
        token , key , iv , Timestamp , ip , port , ip2 , port2 = self.GuestLogin(self.id , self.password)
        self.JwT_ToKen = token        
        try:
            self.AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
            self.AccounT_Uid = self.AfTer_DeC_JwT.get('account_id')
            self.EncoDed_AccounT = hex(self.AccounT_Uid)[2:]
            self.HeX_VaLue = DecodE_HeX(Timestamp)
            self.TimE_HEx = self.HeX_VaLue
            self.JwT_ToKen_ = token.encode().hex()
        except Exception as e:
            return
        try:
            self.Header = hex(len(EnC_PacKeT(self.JwT_ToKen_, key, iv)) // 2)[2:]
            length = len(self.EncoDed_AccounT)
            self.__ = '00000000'
            if length == 9: self.__ = '0000000'
            elif length == 8: self.__ = '00000000  '
            elif length == 10: self.__ = '000000'
            elif length == 7: self.__ = '000000000'
            else:
                pass                
            self.Header = f'0115{self.__}{self.EncoDed_AccounT}{self.TimE_HEx}00000{self.Header}'
            self.FiNal_ToKen_0115 = self.Header + EnC_PacKeT(self.JwT_ToKen_ , key , iv)
        except Exception as e:
            pass
        self.AutH_ToKen = self.FiNal_ToKen_0115
        self.Connect_SerVer(self.JwT_ToKen , self.AutH_ToKen , ip , port , key , iv , ip2 , port2)        
        return self.AutH_ToKen , key , iv

def ChEck_Commande(team_code):
    return bool(team_code and len(team_code) >= 6)

ACCOUNTS = [
    {"id":"5536557807","password":"sdfghjk_BY_JAGWAR_8DhKeP5s"},
    {"id":"5536557878","password":"sdfghjk_BY_JAGWAR_riaXnNWY"},
    {"id":"5536557941","password":"sdfghjk_BY_JAGWAR_XvRVrjwR"},
    {"id":"5536557842","password":"sdfghjk_BY_JAGWAR_Bi5jivkF"},
    {"id":"5536557828","password":"sdfghjk_BY_JAGWAR_I1WLla0H"},
    {"id":"5536557860","password":"sdfghjk_BY_JAGWAR_v8QuyRHF"}
]

def start_account(account):
    try:
        FF_CLient(account['id'], account['password'])
    except Exception as e:
        start_account(account)

@app.route('/msg', methods=['GET', 'POST'])
def send_message():
    try:
        if request.method == 'GET':
            teamcode = request.args.get('teamcode')
            message = request.args.get('message')
        else:
            data = request.get_json()
            teamcode = data.get('teamcode')
            message = data.get('message')

        if not teamcode or not message:
            return jsonify({'status': 'error', 'message': 'Teamcode and message are required'}), 400

        if not ChEck_Commande(teamcode):
            return jsonify({'status': 'error', 'message': 'Invalid teamcode'}), 400

        response = jsonify({'status': 'success', 'message': 'Processing started...'})
        
        def background_job(teamcode, message):
            try:
                with connected_clients_lock:
                    if len(connected_clients) == 0:
                        return
                
                    first_client = list(connected_clients.values())[0]
                    team_data = first_client.GeTinFoSqMsG(teamcode)

                    if not team_data["success"]:
                        return

                    team_id = team_data["team_id"]
                    sq = team_data["sq"]
                    first_client.SeNd_SpaM_MsG(team_id, sq, message)
            except Exception as e:
                print("Background error:", str(e))

        threading.Thread(target=background_job, args=(teamcode, message)).start()
        return response, 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def start_bot():
    time.sleep(10)         
    print(f"\n - Bot is Online")
    print(f" - Connected Successfully!\n")    
    
    threads = []
    
    for account in ACCOUNTS:
        thread = threading.Thread(target=start_account, args=(account,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(5)
    
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)