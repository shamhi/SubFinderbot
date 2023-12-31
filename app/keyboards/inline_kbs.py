from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


choosing_command = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='subdomains', callback_data='command1'),
        InlineKeyboardButton(text='webs', callback_data='command2')
    ],
    [
        InlineKeyboardButton(text='Отмена поиска', callback_data='cancel')
    ]
])

accept_command = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Да', callback_data='is_accepted'),
        InlineKeyboardButton(text='Нет', callback_data='is_not_accepted')
    ]
])


choosing_command_data = ['command1', 'command2']
cancel_data = 'cancel'

accepted_data = ['is_accepted', 'is_not_accepted']


def get_search_commands(domain_name, command_data):
    search_commands = {
        'command1': f'subfinder -d {domain_name} -silent -nc -o app/search_results/result.txt',
        'command2': f'subfinder -d {domain_name} -silent  |httpx -silent -nc -sc -ip -cl -title -location -server'
    }

    return search_commands.get(command_data)

def get_search_commands_by_file(command_data):
    target_file = 'app/search_results/current_targets.txt'
    search_commands = {
        'command1': f'subfinder -dL {target_file} -silent -nc -o app/search_results/result.txt',
        'command2': f'subfinder -dL {target_file} -silent  |httpx -silent -nc -sc -ip -cl -title -location -server'
    }

    return search_commands.get(command_data)
