from flask import Flask, request, jsonify
import json
import os
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import time
from threading import Thread
import threading

app = Flask(__name__)
ACCOUNTS_FILE = 'a.json'
TOKENS_FILE = 'tokens.json'  # ملف لتخزين التوكنات المخزنة مع وقتها
TOKENS_CACHE_TIME = 3600  # تخزين التوكنات لمدة ساعة (يمكن تغييرها حسب صلاحية الـ JWT)

# مفاتيح التشفير (نفس اللي عندك)
KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# قاموس لتتبع حالة السبام لكل uid (True = يعمل, False = متوقف)
active_spam = {}
spam_lock = threading.Lock()

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tokens(tokens):
    data = {
        "tokens": tokens,
        "timestamp": time.time()
    }
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_cached_tokens():
    if not os.path.exists(TOKENS_FILE):
        return None
    with open(TOKENS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if time.time() - data.get("timestamp", 0) > TOKENS_CACHE_TIME:
        return None  # منتهية الصلاحية
    return data.get("tokens")


def get_tokens():
    # محاولة تحميل التوكنات من الكاش
    tokens = load_cached_tokens()
    if tokens:
        return tokens

    accounts = load_accounts()
    tokens = []

    for uid, pwd in accounts.items():
        try:
            response = requests.get(
                f"https://damar-free-jwt.spcfy.eu/guest?uid={uid}&pw={pwd}",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("status") == "success" and data.get("token"):
                    token = data["token"]
                    tokens.append(token)

                    # رسالة عند نجاح تسجيل الدخول
                    print(f"تم تسجيل الدخول. UID: {uid}")

                else:
                    print(f"فشل تسجيل الدخول. UID: {uid}")

            else:
                print(f"خطأ HTTP {response.status_code}. UID: {uid}")

        except Exception as e:
            print(f"خطأ مع UID {uid}: {e}")

    if tokens:
        save_tokens(tokens)

    return tokens

def encrypt_data(plain_text):
    if isinstance(plain_text, str):
        plain_text = bytes.fromhex(plain_text)
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def encode_id(number):
    number = int(number)
    encoded_bytes = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not number:
            break
    return bytes(encoded_bytes).hex()

def spam_worker(uid):
    """دالة السبام اللي بتشتغل في خلفية لكل uid"""
    tokens = get_tokens()
    if not tokens:
        print(f"[UID {uid}] لا توجد توكنات صالحة")
        return

    enc_id = encode_id(uid)
    payload = f"08a7c4839f1e10{enc_id}1801"
    enc_data = encrypt_data(payload)

    while True:
        with spam_lock:
            if not active_spam.get(uid, False):
                break  # توقف إذا تم إيقاف السبام

        for token in tokens:
            try:
                requests.post(
                    "https://clientbp.ggpolarbear.com/RequestAddingFriend",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Unity-Version": "2018.4.11f1",
                        "X-GA": "v1 1",
                        "ReleaseVersion": "OB54",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
                        "Connection": "Keep-Alive",
                        "Accept-Encoding": "gzip"
                    },
                    data=bytes.fromhex(enc_data),
                    timeout=10
                )
            except Exception:
                pass

        time.sleep(1)  # تأخير بسيط بين الدورات عشان ما يثقل السيرفر (يمكن تعديله)

    print(f"[UID {uid}] تم إيقاف السبام")

# API لتشغيل السبام (مثل spam_vip)
@app.route('/spam_vip')
def start_spam():
    uid = request.args.get("id")
    if not uid:
        return jsonify({"status": "error", "message": "يجب تقديم id"}), 400

    try:
        uid = int(uid)
    except ValueError:
        return jsonify({"status": "error", "message": "id غير صالح"}), 400

    with spam_lock:
        if active_spam.get(uid, False):
            return jsonify({"status": "already_running", "message": f"السبام شغال بالفعل على {uid}"})

        active_spam[uid] = True

    # شغل السبام في thread منفصل
    thread = Thread(target=spam_worker, args=(uid,))
    thread.daemon = True
    thread.start()

    return jsonify({"status": "started", "message": f"تم تشغيل السبام على {uid} بنجاح"})

# API لإيقاف السبام (مثل stop)
@app.route('/stop')
def stop_spam():
    uid = request.args.get("id")
    if not uid:
        return jsonify({"status": "error", "message": "يجب تقديم id"}), 400

    try:
        uid = int(uid)
    except ValueError:
        return jsonify({"status": "error", "message": "id غير صالح"}), 400

    with spam_lock:
        if not active_spam.get(uid, False):
            return jsonify({"status": "not_running", "message": f"السبام مش شغال على {uid} أصلاً"})

        active_spam[uid] = False

    return jsonify({"status": "stopped", "message": f"تم إيقاف السبام على {uid} بنجاح"})

# صفحة رئيسية سريعة
@app.route('/')
def home():
    return jsonify({
        "status": "نشط",
        "endpoints": {
            "/spam_vip?id={uid}": "تشغيل السبام VIP (إرسال طلبات صداقة مستمرة)",
            "/stop?id={uid}": "إيقاف السبام لـ uid معين"
        },
        "note": "التوكنات تُخزن مؤقتاً لمدة ساعة عشان ما يعاد توليدها كل مرة"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6709, debug=False)  # غيرت البورت للي طلبت (6709)