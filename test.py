from twitch import TwitchClient
import pprint

client = TwitchClient('9nmje2zw0z52qn0g75wcrbsh1hxwny')

users = client.users.translate_usernames_to_ids('xqcow')
logo = users[0]['logo']

print(users)
