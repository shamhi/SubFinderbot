from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


choosing_command = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='subdomains', callback_data='command1'),
        InlineKeyboardButton(text='webs', callback_data='command2')
    ]
])

choosing_command_data = ['command1', 'command2']

def get_search_commands(domain_name, command_data):
    search_commands = {
        'command1': f'subfinder -d {domain_name} -silent -nc -o result.txt',
        'command2': f'subfinder -d {domain_name} -silent  |httpx -silent -nc -sc -ip -cl -title -location -server'
    }

    return search_commands.get(command_data)
