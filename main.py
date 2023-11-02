from aiogram import Bot, Dispatcher
from app.middlewares import InfoLoggerMiddleware, ThrottlingMiddleware
from app.filters import ChatTypeFilter, IsAdmin
from app.routers import main_router
from app.config import config
from app import utils


def setup_logging(dp: Dispatcher):
    dp["aiogram_logger"] = utils.logging.setup_logger().bind(type="aiogram")
    dp["throttling_logger"] = utils.logging.setup_logger().bind(type="throttling")


async def setup_commands(bot: Bot):
    pass


async def setup_aiogram(dp: Dispatcher, bot: Bot):
    await setup_commands(bot)
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    setup_handlers(dp)
    setup_filters(dp)
    setup_middlewares(dp)
    logger.info("Configured aiogram")


async def aiogram_on_startup(dispatcher: Dispatcher, bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(dispatcher, bot)
    dispatcher["aiogram_logger"].info("Started polling")


async def aiogram_on_shutdown(dispatcher: Dispatcher, bot: Bot):
    dispatcher["aiogram_logger"].debug("Stopping polling")
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped polling")


def setup_handlers(dp: Dispatcher):
    dp.include_router(main_router)


def setup_filters(dp: Dispatcher):
    dp.message.filter(ChatTypeFilter('private'))
    dp.message.filter(IsAdmin())


def setup_middlewares(dp: Dispatcher):
    dp.update.outer_middleware(InfoLoggerMiddleware(logger=dp['aiogram_logger']))
    dp.message.middleware(ThrottlingMiddleware(logger=dp['throttling_logger'], throttling_time=10))



def main():
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher()

    dp.startup.register(aiogram_on_startup)
    dp.shutdown.register(aiogram_on_shutdown)
    dp.run_polling(bot)


if __name__ == '__main__':
    main()
