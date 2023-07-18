from io import BytesIO
import threading
import dearpygui.dearpygui as dpg
import urllib.request
import os, json, codecs, requests, time

DISCORD_TOKEN = ""
SESSION = ""
COOKIES = ""
USER_INFO = {}
STATUS = ""
PATH = "?"
RELATIONSHIPS = []
SETTINGS = ""
LOGGER = []

def getProfile(user_id):
    url = f"https://discord.com/api/v9/users/{user_id}/profile"
    
    headers = {
        'Authorization': DISCORD_TOKEN,
    }

    response = requests.request("GET", url, headers=headers, cookies=COOKIES)

    return json.loads(response.text)

def getRelationships():
    url = "https://discord.com/api/v9/users/@me/relationships"
    
    headers = {
        'Authorization': DISCORD_TOKEN,
    }

    response = requests.request("GET", url, headers=headers, cookies=COOKIES)

    return json.loads(response.text)

def getNotes(user_id):
    url = f"https://discord.com/api/v9/users/@me/notes/{user_id}"
    
    headers = {
        'Authorization': DISCORD_TOKEN,
    }

    response = requests.request("GET", url, headers=headers, cookies=COOKIES)

    return json.loads(response.text)

def serchDM(user_id):
    url = "https://discord.com/api/v9/users/@me/channels"

    payload = json.dumps({
        "recipients": [
            str(user_id)
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': DISCORD_TOKEN,
    }
    response = requests.request("POST", url, headers=headers, data=payload, cookies=COOKIES)

    return json.loads(response.text)

def getMessages(channel_id, before_id = None):



    if before_id != None:
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages?before={before_id}&limit=50"
    else:
        url = f"https://discord.com/api/v6/channels/{channel_id}/messages?limit=50"

    headers = {
        'Authorization': DISCORD_TOKEN,
    }

    response = requests.request("GET", url, headers=headers, cookies=COOKIES)

    return json.loads(response.text)

def getAllMessage(channel_id):
    HEAP_MESSAGES = []
    LAST_MESSAGE_ID, MSGS_PACK = 0, 0

    # print('start getting message')
    dpg.add_text('start getting message', parent="console")
    try:
        if len(HEAP_MESSAGES) == 0:
            MSGS_PACK = getMessages(channel_id)
            LAST_MESSAGE_ID = MSGS_PACK[::-1][0]['id']
            HEAP_MESSAGES = HEAP_MESSAGES + MSGS_PACK
    except:
        return

    while True:
        # print(f'getted {len(HEAP_MESSAGES)} message')
        dpg.add_text(f'getted {len(HEAP_MESSAGES)} message', parent="console")

        MSGS_PACK = getMessages(channel_id, before_id=LAST_MESSAGE_ID)

        if len(MSGS_PACK) == 0:
            break

        LAST_MESSAGE_ID = MSGS_PACK[::-1][0]['id']
        HEAP_MESSAGES = HEAP_MESSAGES + MSGS_PACK

        time.sleep(1)

    # print('stop getting message')
    dpg.add_text('stop getting message', parent="console")

    return HEAP_MESSAGES

def getContent(msg, format='md'):

    def getTime(date_time_discord):
        return ' '.join(date_time_discord.split('T')).split('.')[0]

    content = msg['content']
    attachments = msg['attachments']

    if len(attachments) != 0:
        for attachment in attachments:
            if len(content) != 0:
                content += f"\n{attachment['url']}"
            else:
                content += f"{attachment['url']}"


    if(msg['author']['global_name'] == None):
        author = f"{ msg['author']['username'] }#{ msg['author']['discriminator'] }"
    else:
        author = f"{msg['author']['global_name']}"

    if format == 'md':
        return f'''{author} #{getTime(msg['timestamp'])}  \n{content}\n\n'''
    if format == 'json':
        return { 
            "author": author, 
            'time': getTime(msg['timestamp']), 
            "content": content, 
            # "attachments": attachments
        }

def writeInFile(PATH, FILE_NAME, DATA):

    if not os.path.exists(PATH):
        os.mkdir(PATH)
        dpg.add_text(f" Directory {PATH} Created ", parent="console")
        # print(f" Directory {PATH} Created ")

    with open(f'{PATH}/{FILE_NAME}', 'w', encoding='utf-8') as file:
        json.dump(DATA, file, ensure_ascii=False, indent=4)
    
def writeInfo(fileName, user_id):

    try:
        id_cannal = serchDM(user_id)['id']
    except:
        return
    

    USER = {}

    try:
        info = getProfile(user_id)['user']
        try:
            info["note"] = getNotes(user_id)['note']
        except:
            pass
    except:
        info = {"id": user_id}

    USER['info'] = info

    try:
        messages = getAllMessage(id_cannal)
        formated_messages = []
        for msg in messages:
            formated_messages.append(getContent(msg, 'json'))
        
        USER['messages'] = formated_messages
    except:
        pass
        

    writeInFile(PATH, f'{fileName}.json', USER)

def getDataInput(sender, app_data):
    global DISCORD_TOKEN
    DISCORD_TOKEN = app_data
    # print(DISCORD_TOKEN)



def login_fn():
    global SESSION
    global COOKIES
    global USER_INFO
    global STATUS

    

    SESSION = requests.get(
        "https://discord.com/api/v9/users/@me", 
        headers={
            'Content-Type': 'application/json',
            'Authorization': DISCORD_TOKEN,
        }
    )

    COOKIES = requests.utils.dict_from_cookiejar(SESSION.cookies)

    USER_INFO = json.loads(SESSION.text)

    if "message" in USER_INFO :
        STATUS = {USER_INFO["message"]}
        dpg.set_value("status", f"{STATUS}")
        
    else:
        STATUS = {'message': 'authorized'}
        user_nickname = USER_INFO["username"]
        dpg.set_value("status", f"is login")
        dpg.set_value("user_nickname", f"{user_nickname}")
        
        dpg.show_item("myInfo")

        dpg.hide_item("login")
        dpg.hide_item("token_input")

        add_flendList()

        for i in ["select_1", "select_2", "select_directory", "path", "text_msg_1", "exit"]:
            dpg.show_item(i)

        # print(getRelationships())

def exit_fn():
    for i in ["select_1", "select_2", "select_directory", "path", "text_msg_1", "myInfo", "exit"]:
        dpg.hide_item(i)
    for i in ["login", "token_input"]:
        dpg.show_item(i)
    
    dpg.set_value("status", "status: no authorization")
    dpg.set_value("user_nickname", "your nickname")
    dpg.delete_item("friends")
    
def get_senderLB(sender):
    value = f"{dpg.get_value(sender)}"
    value = value.split("'id': ")[1].split("'")[1]

    infoAboutAny(getProfile(value))
    # print(getProfile(f"{value}"))

def add_flendList():
    global RELATIONSHIPS

    RELATIONSHIPS = getRelationships()

    freandList = []

    for item in RELATIONSHIPS:
        
        freandList.append({"username": item["user"]["username"], "type": item["type"], "id": item["id"]})

    # print(RELATIONSHIPS)

    dpg.show_item("nothing0")
    # dpg.add_text("", tag="Freands_text", parent="window_login", before="nothing")
    dpg.add_listbox(freandList, width=600, tag="friends", parent="window_login", num_items=10, callback=get_senderLB, before="nothing")

def main_fn():
    global PATH

    dpg.show_item("window_loading")
    dpg.show_item("console")
    dpg.set_primary_window("window_login", False)

    dpg.hide_item("window_login")
    dpg.set_primary_window("window_loading", True)

    fromAll = dpg.get_value("select_1")
    fromFiends = dpg.get_value("select_2")

    if fromAll != fromFiends and len(RELATIONSHIPS) != 0:
        # print("good", RELATIONSHIPS, "\n", PATH)

        for user in RELATIONSHIPS:

            if (user['type'] == 2 and fromFiends):
                continue
            
            dpg.add_text(f"{user['user']['username']} {user['user']['global_name']}", parent="console")

            # print(f"{user['user']['username']} {user['user']['global_name']}")

            time.sleep(2)

            try:
                USERNAME = user['user']['global_name']
                if  USERNAME == None:
                    USERNAME = user['user']['username']

                writeInfo(USERNAME, user['id'])
            except:
                writeInfo(user['id'], user['id'])

    dpg.show_item("window_login")
    dpg.set_primary_window("window_login", False)

    dpg.delete_item("save_btn")
    dpg.set_value("path", 'path: ?')
    PATH = "?"
    dpg.hide_item("console")
    dpg.hide_item("window_loading")
    dpg.set_primary_window("window_login", True)

def infoAboutAny(data):
    user = data["user"]

    note = getNotes(user["id"])

    with dpg.window(
        label="window", 
        no_move=False, no_close=False, no_title_bar=False
    ):
        with dpg.group(horizontal=True):
            dpg.add_text("id: ")
            dpg.add_text(f'{user["id"]}')

        with dpg.group(horizontal=True):
            dpg.add_text("username: ")
            dpg.add_text(f'{user["username"]}')

        with dpg.group(horizontal=True):
            dpg.add_text("global_name: ")
            dpg.add_text(f'{user["global_name"]}')

        with dpg.group(horizontal=True):
            dpg.add_text("bio: ")
            dpg.add_text(f'{user["bio"]}')
            
        dpg.add_text(note)

def infoAboutMe():
    with dpg.window(
        label="window", 
        no_move=False, no_close=False, no_title_bar=False
    ):
        with dpg.group(horizontal=True):
            dpg.add_text("id")
            dpg.add_text(USER_INFO["id"])
        with dpg.group(horizontal=True):
            dpg.add_text("username")
            dpg.add_text(USER_INFO["username"])
        with dpg.group(horizontal=True):
            dpg.add_text("global_name")
            dpg.add_text(USER_INFO["global_name"])
        with dpg.group(horizontal=True):
            dpg.add_text("email")
            dpg.add_text(USER_INFO["email"])
        with dpg.group(horizontal=True):
            dpg.add_text("phone")
            dpg.add_text(USER_INFO["phone"])

def get_chuse(sendler):
    if sendler == "select_1":
        dpg.set_value("select_2", False)

    if sendler == "select_2":
        dpg.set_value("select_1", False)

def path_callback(sender, app_data):
    global PATH

    PATH = app_data["current_path"] + f'/{USER_INFO["username"]}'
    dpg.set_value('path', PATH)

    xthreadingFn = threading.Thread(target=main_fn)

    dpg.add_button(label="start", tag="save_btn", parent="window_login", callback=lambda: xthreadingFn.start())

    # print('OK was clicked.')
    # print("Sender: ", sender)
    # print("App Data: ", app_data)

def path_cancel_callback(sender, app_data):
    pass
    # print('Cancel was clicked.')
    # print("Sender: ", sender)
    # print("App Data: ", app_data)

def fn_chuse():
    print("select_1", dpg.get_value("select_1"), "select_2", dpg.get_value("select_2"), type(dpg.get_value("select_1")))

dpg.create_context()

with dpg.window(
        label="window_login", 
        tag="window_login", pos=(0,0), width=700, height=150, 
        no_move=True, no_close=True, no_title_bar=True
    ):

    dpg.add_text("your nickname", tag="user_nickname")
    dpg.add_text("status: no authorization", tag="status")
    dpg.add_button(label="show info", tag="myInfo", show=False, callback=infoAboutMe)
    dpg.add_input_text(tag="token_input", callback=getDataInput)
    dpg.add_button(label="login", tag="login", callback=login_fn)
    dpg.add_button(label="exit", tag='exit', show=False, callback=exit_fn)
    dpg.add_text("", tag="nothing0", show=False)

    dpg.add_text("", tag="nothing")

    dpg.add_text("Get messages from:", show=False, tag="text_msg_1")

    with dpg.group(horizontal=True):
        dpg.add_checkbox(label="All", tag='select_1', show=False, callback=get_chuse)
        dpg.add_checkbox(label="Friends", tag='select_2', show=False, callback=get_chuse)

    dpg.add_file_dialog(directory_selector=True, show=False, tag="file_directory_id", width=500 ,height=400, callback=path_callback, cancel_callback=path_cancel_callback)

    with dpg.group(horizontal=True):
        dpg.add_button(label="Select directory",tag="select_directory" , show=False, callback=lambda: dpg.show_item("file_directory_id"))
        dpg.add_text("path: ?", show=False, tag="path")



with dpg.window(
        label="window_loading", 
        tag="window_loading", pos=(0,0), width=700, height=150, 
        show=False,
        no_move=True, no_close=True, no_title_bar=True
    ):

    with dpg.group(horizontal=True):
        dpg.add_loading_indicator()
        dpg.add_text("Loading")

    
with dpg.window(label="console", tag="console", pos=(0,50), width=800, height=500, no_resize=True, show=False, no_close=True, no_move=True, no_title_bar=True):
    pass


dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("window_login", True)
dpg.start_dearpygui()
dpg.destroy_context()