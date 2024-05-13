from telethon.sync import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsBots, ChannelParticipantsKicked, ChannelParticipantsBanned, ChannelParticipantsSearch, InputChannel, InputChannelEmpty
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import Chat
import asyncio
import time
import pytz
import speedtest
import datetime
import os
import requests
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
api_id = '21829390'
api_hash = 'e162ea1852049e2d22e18a854b74fe07'

client = TelegramClient('dysession', api_id, api_hash)

target_chat_id = None
fake_typing_task = None
owner_id = '6721761178'

unread_messages = {}



API_KEY = "xyydycoders"

@client.on(events.NewMessage(pattern='/quote'))
async def quote_to_sticker(event):
    # Mendapatkan teks kutipan dari pesan
    text = event.message.text.split(' ', 1)[1] if ' ' in event.message.text else None
    if not text:
        await event.respond("Please provide text to quote.")
        return

    # Mendapatkan informasi pengguna Telegram
    user = await client.get_entity(event.sender_id)
    username = user.username
    avatar = await client.download_profile_photo(user, file="profile_photo.jpg")
    
    # Membuat permintaan ke API untuk membuat kutipan
    url = f"https://skizo.tech/api/qc?apikey={API_KEY}&text={text}&username={username}&avatar={avatar}"
    response = requests.get(url)
    if response.status_code == 200:
        sticker_bytes = response.content
        
        # Mengirim sticker ke pengguna
        await client.send_file(event.chat_id, BytesIO(sticker_bytes))
    else:
        await event.respond("Failed to create quote sticker.")

    # Menghapus file foto profil yang diunduh
    os.remove("profile_photo.jpg")


@client.on(events.NewMessage(pattern=r'/groupinfo\s+(\S+)'))
async def group_info(event):
    if str(event.sender_id) != owner_id:
        return
    group_link = event.pattern_match.group(1)
    try:
        entity = await client.get_entity(group_link)
        if entity:
            info_text = f'Nama Grup: {entity.title}\n'
            info_text += f'Jumlah Member: {await get_total_members(entity)}\n'
            info_text += f'Jumlah member yang sedang online: {await get_online_members(entity)}\n'
            info_text += f'Jumlah admin grup: {await get_admin_count(entity)}\n'
            info_text += f'Jumlah pengguna telegram premium yang ada di grup: {await get_premium_users_count(entity)}\n'
            await event.respond(info_text)
        else:
            await event.respond('Grup tidak ditemukan.')
    except Exception as e:
        await event.respond(f'Error: {e}')

async def get_total_members(entity):
    try:
        participants = await client.get_participants(entity)
        return len(participants)
    except Exception as e:
        return "Error: " + str(e)

async def get_online_members(entity):
    try:
        participants = await client.get_participants(entity)
        online_count = sum(1 for user in participants if user.status == 'online')
        return online_count
    except Exception as e:
        return "Error: " + str(e)

async def get_admin_count(entity):
    try:
        admins = await client.get_participants(entity, filter=ChannelParticipantsAdmins)
        return len(admins)
    except Exception as e:
        return "Error: " + str(e)

async def get_premium_users_count(entity):
    try:
        participants = await client.get_participants(entity)
        premium_count = sum(1 for user in participants if user.premium)
        return premium_count
    except Exception as e:
        return "Error: " + str(e)

@client.on(events.NewMessage(pattern='/status'))
async def get_status(event):
    if str(event.sender_id) != owner_id:
        return
    global target_chat_id
    with open('zall.txt', 'r') as file:
        saved_chat_id = file.read()
    if saved_chat_id:
        response = f'ID Target: {saved_chat_id}\nRequest Date: {datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")}\nLast Chat Message: {await get_last_message(saved_chat_id)}'
    else:
        response = 'No target chat ID set.'
    await event.respond(response)

async def get_last_message(chat_id):
    try:
        async for message in client.iter_messages(int(chat_id), limit=1):
            return message.text if message.text else "Null"
    except Exception as e:
        return "Error: " + str(e)


@client.on(events.NewMessage(pattern='/restart'))
async def restart(event):
    if str(event.sender_id) != owner_id:
        return
    await event.respond('Restarting bot...')
    os.execv(__file__, [__file__])

@client.on(events.NewMessage(pattern='/readall'))
async def read_all_messages(event):
    if str(event.sender_id) != owner_id:
        return
    await event.respond('Reading all messages...')
    async for message in client.iter_messages(target_chat_id):
        if message.text:
            with open('msg.txt', 'a') as file:
                file.write(message.text + '\n')

@client.on(events.NewMessage(pattern='/menu'))
async def show_menu(event):
    
    menu_text = "Daftar Menu:\n"
    menu_text += "/fake_typing - Memulai fake typing\n"
    menu_text += "/setid [ID] - Set target chat ID\n"
    menu_text += "/status - Menampilkan status bot\n"
    menu_text += "/stop - Menghentikan fake typing\n"
    menu_text += "/restart - Me-restart bot\n"
    menu_text += "/readall - Membaca semua pesan\n"
    menu_text += "/top - Menampilkan grup dengan pesan terbanyak\n"
    menu_text += "/Ping - Untuk Mengecek Kecepatan Respon\n"
    menu_text += "/speedtest - Untuk mengecek kecepatan internet\n"
    await event.respond(menu_text)

@client.on(events.NewMessage(pattern='/top'))
async def top_groups(event):
    if str(event.sender_id) != owner_id:
        return
    await event.respond('Fetching top 20 groups...')
    global unread_messages
    unread_messages = {}
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            unread_count = dialog.unread_count
            if unread_count > 0:
                unread_messages[dialog.id] = unread_count
    sorted_groups = sorted(unread_messages.items(), key=lambda x: x[1], reverse=True)[:20]
    top_groups_text = 'Top 20 groups with most unread messages:\n'
    for group_id, count in sorted_groups:
        chat = await client.get_entity(group_id)
        top_groups_text += f'{chat.title}: {count} unread messages\n'
    await event.respond(top_groups_text)

with open('owner.txt', 'w') as file:
    file.write(owner_id)
    
@client.on(events.NewMessage(pattern='/ping'))
async def ping(event):
    if str(event.sender_id) != owner_id:
        return
    start_time = time.time()
    await event.respond('Wait!')
    end_time = time.time()
    response_time = end_time - start_time
    await event.respond(f'Bot response time: {response_time:.2f} seconds')
    
# DOWNLOADER MENU
    

@client.on(events.NewMessage(pattern='/download_tiktok'))
async def download_tiktok(event):
   
    try:
        api_key = "xyydycoders"  # Ganti dengan API key yang Anda miliki
        url = "https://skizo.tech/api/tiktok"
        params = {"apikey": api_key, "url": event.message.text.split(' ')[1]}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()["data"]
            video_url = data["play"]
            video_file = requests.get(video_url)
            if video_file.status_code == 200:
                with open("video.mp4", "wb") as f:
                    f.write(video_file.content)
                await event.respond(file="video.mp4")
            else:
                await event.respond("Gagal mengunduh video TikTok.")
        else:
            await event.respond("Gagal mengunduh video TikTok.")
    except Exception as e:
        await event.respond(f"Terjadi kesalahan: {str(e)}")


# Fungsi untuk mencari dan mendownload lagu dari SoundCloud
async def search_and_download_soundcloud(query):
    url = f"https://api.maher-zubair.tech/search/soundcloud?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()["result"]["result"]
        if result:
            song = result[0]  # Ambil lagu pertama dari hasil pencarian
            download_url = f"https://api.maher-zubair.tech/download/soundcloud?url={song['url']}"
            download_response = requests.get(download_url)
            if download_response.status_code == 200:
                download_data = download_response.json()["result"]
                title = download_data["title"]
                mp3_link = download_data["link"]
                mp3_file = requests.get(mp3_link)
                if mp3_file.status_code == 200:
                    return title, mp3_file.content
    return None, None

# Command /play untuk mencari dan memainkan lagu dari SoundCloud
@client.on(events.NewMessage(pattern='/play'))
async def play_soundcloud(event):
    
    try:
        query = event.message.text.split(' ', 1)[1]
        title, mp3_content = await search_and_download_soundcloud(query)
        if title and mp3_content:
            file_name = f"{title}.mp3"
            with open(file_name, "wb") as f:
                f.write(mp3_content)
            await event.respond(f"Sedang memainkan: {title}")
            await event.respond(file=file_name)  # Kirim file MP3 ke pengguna
            os.remove(file_name)  # Hapus file setelah dikirim
        else:
            await event.respond("Tidak ada hasil lagu yang ditemukan.")
    except Exception as e:
        await event.respond(f"Terjadi kesalahan: {str(e)}")







@client.on(events.NewMessage(pattern='/speedtest'))
async def speed_test(event):
    if str(event.sender_id) != owner_id:
        return
    await event.respond('Running speed test...')
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    upload_speed = st.upload() / 1_000_000  # Convert to Mbps
    ping = st.results.ping
    server_info = st.results.server
    client_info = st.results.client
    await event.respond(f'Download speed: {download_speed:.2f} Mbps\nUpload speed: {upload_speed:.2f} Mbps\nPing: {ping} ms')
    await event.respond(f'Server Info:\n{server_info}')
    await event.respond(f'Client Info:\n{client_info}')

async def get_id(event):
    user_id = event.sender_id
    await event.respond(f"Your ID is: {user_id}")

@client.on(events.NewMessage(pattern='/getid'))
async def get_id_wrapper(event):
    await get_id(event)



# Fungsi untuk mendapatkan respons dari API simi
async def get_simi_response(text):
    api_key = "xyydycoders"
    level = 10
    url = f"https://skizo.tech/api/simi?apikey={api_key}&text={text}&level={level}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()["result"]
        return result
    return None

# Perintah untuk memulai fungsionalitas simi
@client.on(events.NewMessage(pattern='/startsimi'))
async def startsimi(event):
    global target_chat_ids
    if target_chat_ids:
        await event.respond('Simi already started.')
    else:
        await event.respond('Please set target chat IDs using /setid command.')

# Perintah untuk menghentikan fungsionalitas simi
@client.on(events.NewMessage(pattern='/stopsimi'))
async def stopsimi(event):
    global target_chat_ids
    sender_chat_id = event.chat_id
    for label, chat_ids in target_chat_ids.items():
        if sender_chat_id in chat_ids:
            target_chat_ids[label] = []
            await event.respond(f'Simi for label {label} stopped.')
            break
    else:
        await event.respond('You are not authorized to stop simi.')

# Fungsi untuk merespons pesan yang masuk ke simi
@client.on(events.NewMessage())
async def simi_chat(event):
    global target_chat_ids
    for label, chat_ids in target_chat_ids.items():
        if event.chat_id in chat_ids:
            text = event.message.text
            response = await get_simi_response(text)
            if response:
                # Merespon sambil merespon pengguna
                await event.reply(response)
            else:
                await event.respond("Failed to get response from simi API.")

# Perintah untuk mengatur ID target chat
@client.on(events.NewMessage(pattern=r'/setid\s+(\d+)\s+(\w+)'))
async def set_id(event):
    global target_chat_ids
    chat_id = int(event.pattern_match.group(1))
    label = event.pattern_match.group(2)
    if chat_id:
        if label in target_chat_ids:
            target_chat_ids[label].append(chat_id)
        else:
            target_chat_ids[label] = [chat_id]
        with open('simi.json', 'w') as file:
            json.dump(target_chat_ids, file)
        await event.respond(f'Target chat ID {chat_id} with label {label} set successfully.')
    else:
        await event.respond('Please provide a valid chat ID.')

# Membaca target chat IDs dari file JSON saat bot dimulai
target_chat_ids = {}
try:
    with open('simi.json', 'r') as file:
        target_chat_ids = json.load(file)
except FileNotFoundError:
    pass


    
@client.on(events.NewMessage(pattern='/kick'))
async def kick_user(event):
    # Periksa apakah pengirim pesan adalah pemilik bot
    if str(event.sender_id) != owner_id:
        await event.respond('You are not authorized to use this command.')
        return

    # Periksa apakah perintah diberikan di grup
    if event.is_group:
        # Periksa apakah pesan memiliki balasan yang di-tag
        if event.reply_to_msg_id is not None:
            # Dapatkan pesan balasan
            reply_message = await event.get_reply_message()
            # Dapatkan ID pengguna yang di-tag
            user_id = reply_message.sender_id
            # Kick pengguna dari grup
            await event.client.kick_participant(event.chat_id, user_id)
            await event.respond('User kicked successfully.')
        else:
            await event.respond('Reply to a message to tag a user to kick.')
    else:
        await event.respond('This command can only be used in groups.')




client.start()
client.run_until_disconnected()