import multiprocessing
from ui.layout import main as streamlit_main
from bot.telegram_bot import run_bot
import uvicorn

def run_streamlit():
    streamlit_main()

def run_fastapi():
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    streamlit_process = multiprocessing.Process(target=run_streamlit)
    bot_process = multiprocessing.Process(target=run_bot)
    api_process = multiprocessing.Process(target=run_fastapi)

    streamlit_process.start()
    bot_process.start()
    api_process.start()

    streamlit_process.join()
    bot_process.join()
    api_process.join()
