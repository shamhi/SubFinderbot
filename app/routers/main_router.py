from aiogram import Router, F, html, md
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from app.states import MainState, TempState, AcceptCommandState
from app.keyboards import inline_kbs as ikb
from app.routers import stickers
from random import choice
import asyncio

main_router = Router()


@main_router.message(Command('start', 'help'))
async def cmd_start(message: Message, state: FSMContext):
    file_id = choice(stickers.start_stickers)
    await message.answer_sticker(sticker=file_id)
    await message.reply(
        f'Начни поиск командой /search <span class="tg-spoiler">{html.quote("<full_command>(необязательно)")}</span>',
        parse_mode='html')

    await state.set_state(TempState.temp)


@main_router.message(Command('cancel'))
async def cmd_cancel(message: Message, state: FSMContext):
    await message.answer(text='Состояние поиска отменено')

    await message.reply(
        f'Начни поиск командой /search <span class="tg-spoiler">{html.quote("<full_command>(необязательно)")}</span>',
        parse_mode='html')

    await state.set_state(TempState.temp)



@main_router.callback_query(F.data == ikb.cancel_data)
async def cancel_search(call: CallbackQuery, state: FSMContext):
    await call.answer(text='Состояние поиска отменено')
    await call.message.delete()

    await call.message.answer(
        f'Начни поиск командой /search <span class="tg-spoiler">{html.quote("<full_command>(необязательно)")}</span>',
        parse_mode='html')

    await state.set_state(TempState.temp)



@main_router.message(Command('search'), StateFilter(TempState.temp))
async def cmd_search(message: Message, state: FSMContext, command: CommandObject):
    if command.args:
        # if command.args.split()[0].strip() not in ['subfinder', 'httpx'] or all(arg.split()[0].strip() not in ['subfinder', 'httpx'] for arg in command.args.split('|')) or all(arg.split()[0].strip() not in ['subfinder', 'httpx'] for arg in command.args.split('&')):
        #     file_id = choice(stickers.not_pass_domain_stickers)
        #     await message.answer_sticker(sticker=file_id)
        #     await message.reply(
        #         text=f'<span class="tg-spoiler"><a href="tg://user?id={message.from_user.id}">{html.quote(message.from_user.username)}</a></span>, хорошая попытка\n'
        #              f'Ваша команда должна начинаться с <code>subfinder</code> либо <code>httpx</code>',
        #         parse_mode='html')
        #     return
        await state.set_state(AcceptCommandState.wait_accept)

        await message.reply(text=f'Ваша команда:\n```bash\n{md.quote(command.args)}\n```\n\n'
                                 f'Вы точно хотите ее выполнить?', parse_mode='markdownv2', reply_markup=ikb.accept_command)

        await state.update_data(command_args=command.args)
        return
    file_id = stickers.start_job_sticker
    await message.answer_sticker(sticker=file_id)

    await message.reply('Отправь домен или список доменов (можно с новой строки либо через пробел)')

    await state.set_state(MainState.get_domain)


@main_router.callback_query(F.data.in_(ikb.accepted_data), StateFilter(AcceptCommandState.wait_accept))
async def search_cmd_args(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    if call.data == 'is_accepted':
        state_data = await state.get_data()
        command = state_data.get('command_args')

        process = await asyncio.create_subprocess_shell(
            cmd=command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        msg = await call.message.answer("Ваш запрос обрабатывается, ожидайте...")
        await call.message.answer_sticker(sticker=stickers.wait_process_sticker)
        await call.message.bot.send_chat_action(chat_id=call.message.chat.id, action='upload_document')

        await process.wait()

        if process.returncode == 0:
            await call.message.bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id, text="Команда завершена")

            if '-o' in command or '-output' in command:
                file = FSInputFile(path='result.txt', filename='result')
                await call.message.answer_document(document=file)
            else:
                stdout = await process.stdout.read()
                result = stdout.decode('windows-1251')

                with open('app/search_results/result.txt', 'w') as file:
                    file.write(result)

                file = FSInputFile(path='app/search_results/result.txt', filename='result')
                try: await call.message.answer_document(document=file)
                except: ...

            file_id = stickers.finish_job_stickers
            await call.message.answer_sticker(sticker=file_id)
        else:
            stderr = await process.stderr.read()
            error = stderr.decode('windows-1251')

            await call.message.bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id,
                                                     text=f'При выполнении команды произошла ошибка\n```bash\n{md.quote(error)}\n```',
                                                     parse_mode='markdownv2')
    else:
        file_id = stickers.not_accepted_command
        await call.message.answer_sticker(sticker=file_id)
        # await call.message.answer(
        #     f'Начни поиск командой /search <span class="tg-spoiler">{html.quote("<full_command>(необязательно)")}</span>',
        #     parse_mode='html')

    await call.message.answer(
        f'Начни поиск командой /search <span class="tg-spoiler">{html.quote("<full_command>(необязательно)")}</span>',
        parse_mode='html')
    await state.set_state(TempState.temp)


@main_router.message(F.text.regexp(r"^(https?:\/\/)?[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*$"), StateFilter(MainState.get_domain))
async def get_domain(message: Message, state: FSMContext):
    domain = message.text

    if '\n' in message.text or ' ' in message.text:
        await message.reply(text=f'Цель: `{md.quote("target.txt")} (Файл с доменами)`\n\n'
                                 f'Команда `subdomains`:\n```bash\n{md.quote("subfinder -dL target.txt -silent -nc -o <filename>")}\n```\n\n'
                                 f'Команда `webs`:\n```bash\n{md.quote("subfinder -dL target.txt -silent  |httpx -silent -nc -sc -ip -cl -title -location -server")}\n```\n\n'
                                 f'Выберите одну из них', parse_mode='markdownv2', reply_markup=ikb.choosing_command)
        domains = message.text.split('\n')

        with open('app/search_results/current_targets.txt', 'w') as file:
            for domain in domains:
                domain = '\n'.join(domain.split()) if ' ' in domain else domain
                file.write(f'{domain}\n')

        with open('app/search_results/history_domains.txt', 'a') as file:
            file.write(f'{domain}\n')

        await state.update_data(domain_name='dL')
        await state.set_state(MainState.get_command)
        return

    with open('app/search_results/history_domains.txt', 'a') as file:
        file.write(f'{domain}\n')

    file_id = choice(stickers.pass_domain_stickers)
    await message.answer_sticker(sticker=file_id)

    await message.reply(text=f'Цель: `{md.quote(domain)}`\n\n'
                             f'Команда `subdomains`:\n```bash\n{md.quote("subfinder -d <domain.com> -silent -nc -o <filename>")}\n```\n\n'
                             f'Команда `webs`:\n```bash\n{md.quote("subfinder -d <domain.com> -silent  |httpx -silent -nc -sc -ip -cl -title -location -server")}\n```\n\n'
                             f'Выберите одну из них', parse_mode='markdownv2', reply_markup=ikb.choosing_command)

    await state.update_data(domain_name=domain)
    await state.set_state(MainState.get_command)


@main_router.message(StateFilter(MainState.get_domain))
async def wrong_domain(message: Message):
    file_id = choice(stickers.not_pass_domain_stickers)
    await message.answer_sticker(sticker=file_id)
    await message.reply(
        text=f'<span class="tg-spoiler"><a href="tg://user?id={message.from_user.id}">{html.quote(message.from_user.username)}</a></span>, хорошая попытка\n'
             f'Отправь домен по типу <i>`http<span class="tg-spoiler">s</span>://example.com`</i> или <i>`<a href="http://www.example.com/">example.com</a>`</i>',
        parse_mode='html')


@main_router.callback_query(F.data.in_(ikb.choosing_command_data), StateFilter(MainState.get_command))
async def get_command(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    state_data = await state.get_data()

    domain = state_data.get('domain_name')
    command_data = call.data

    if domain == 'dL':
        command = ikb.get_search_commands_by_file(command_data=command_data)
    else:
        command = ikb.get_search_commands(domain_name=domain, command_data=command_data)

    if command is None:
        await call.answer(text='Команда не найдена')

        await state.set_state(TempState.temp)
        return

    process = await asyncio.create_subprocess_shell(
        cmd=command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    msg = await call.message.answer("Ваш запрос обрабатывается, ожидайте...")
    await call.message.answer_sticker(sticker=stickers.wait_process_sticker)
    await call.message.bot.send_chat_action(chat_id=call.message.chat.id, action='upload_document')

    await process.wait()

    if process.returncode == 0:
        await call.message.bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id, text="Команда завершена")

        if '-o' in command or '-output' in command:
            file = FSInputFile(path='app/search_results/result.txt', filename='result')

            await call.message.answer_document(document=file)

            with open('app/search_results/result.txt', 'w') as file:
                file.write('')
        else:
            stdout = await process.stdout.read()
            result = stdout.decode('windows-1251')

            with open('app/search_results/result.txt', 'w') as file:
                file.write(result)

            file = FSInputFile(path='app/search_results/result.txt', filename='result')
            await call.message.answer_document(document=file)

        file_id = stickers.finish_job_stickers
        await call.message.answer_sticker(sticker=file_id)
    else:
        stderr = await process.stderr.read()
        error = stderr.decode('windows-1251')

        await call.message.bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id,
                                                 text=f'При выполнении команды произошла ошибка\n```bash\n{md.quote(error)}\n```',
                                                 parse_mode='markdownv2')

    await call.message.answer(
        f'Начни поиск командой /search <span class="tg-spoiler">{html.quote("<full_command>(необязательно)")}</span>',
        parse_mode='html')
    await state.set_state(TempState.temp)


@main_router.message(F.sticker)
async def get_sticker(message: Message):
    await message.answer(str(message.sticker.file_id))


@main_router.message()
async def end(message: Message):
    await message.reply('Введите /start чтобы войти в состояние поиска')
