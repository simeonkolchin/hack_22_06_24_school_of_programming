import multiprocessing
from ui.layout import main as streamlit_main
from bot.telegram_bot import run_bot

if __name__ == "__main__":
    streamlit_process = multiprocessing.Process(target=streamlit_main)
    bot_process = multiprocessing.Process(target=run_bot)

    streamlit_process.start()
    bot_process.start()

    streamlit_process.join()
    bot_process.join()
