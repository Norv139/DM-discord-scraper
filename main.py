import os, json, requests, time

# import http.client # requests -> http.client

DISCORD_TOKEN = str(input('discord token -> '))

SESSION = requests.get(
    "https://discord.com/api/v9/users/@me", 
    headers={
        'Content-Type': 'application/json',
        'Authorization': DISCORD_TOKEN,
    }
)
COOKIES = requests.utils.dict_from_cookiejar(SESSION.cookies)

WHO_IAM = json.loads(SESSION.text)

# getting functions 

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

def getProfile(user_id):
    url = f"https://discord.com/api/v9/users/{user_id}/profile"
    
    headers = {
        'Authorization': DISCORD_TOKEN,
    }

    response = requests.request("GET", url, headers=headers, cookies=COOKIES)

    return json.loads(response.text)

# improved funcrions

def getAllMessage(channel_id):
    HEAP_MESSAGES = []
    LAST_MESSAGE_ID, MSGS_PACK = 0, 0

    print('start getting message')

    try:
        if len(HEAP_MESSAGES) == 0:
            MSGS_PACK = getMessages(channel_id)
            LAST_MESSAGE_ID = MSGS_PACK[::-1][0]['id']
            HEAP_MESSAGES = HEAP_MESSAGES + MSGS_PACK
    except:
        return

    while True:
        print(f'getted {len(HEAP_MESSAGES)} message')

        MSGS_PACK = getMessages(channel_id, before_id=LAST_MESSAGE_ID)

        if len(MSGS_PACK) == 0:
            break

        LAST_MESSAGE_ID = MSGS_PACK[::-1][0]['id']
        HEAP_MESSAGES = HEAP_MESSAGES + MSGS_PACK

        time.sleep(1)

    print('stop getting message')

    return HEAP_MESSAGES

# work with data

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

# function 

def writeInFile(PATH, FILE_NAME, DATA):

    if not os.path.exists(PATH):
        os.mkdir(PATH)
        print("Directory " , PATH ,  " Created ")

    with open(f'{PATH}/{FILE_NAME}', 'w', encoding='utf-8') as file:
        json.dump(DATA, file, ensure_ascii=False, indent=4)
    

if __name__ == "__main__":

    WHO_IAM_username = WHO_IAM['username']

    PATH = f'./{WHO_IAM_username}'
    print(WHO_IAM_username)

    writeInFile(PATH, f'me.json', WHO_IAM)
        
    ALL_USERS = getRelationships()

    for user in ALL_USERS:
        if user['type'] == 2:
            continue

        print(f"{user['user']['username']} {user['user']['global_name']}")

        time.sleep(2)

        try:
            USERNAME = user['user']['global_name']
            if  USERNAME == None:
                USERNAME = user['user']['username']

            writeInfo(USERNAME, user['id'])
        except:
            writeInfo(user['id'], user['id'])