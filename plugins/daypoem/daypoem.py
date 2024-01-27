from utils.api import send_txt, send_image
import requests
import time
import schedule
import threading
from plugins import register, Plugin, Event, logger, Reply, ReplyType
# BingImage
from bot.BingImageCreator import ImageGen
import os
import shutil
from config import conf

POEM_API = "https://v1.jinrishici.com/all"
DEFAULT_SENTENCE = "芝兰生于幽谷\r\n不以无人而不芳\r\n君子修道立德\r\n不以穷困而改节\r\n"
TEMP_OUTPUT_DIR = "temp_output"

def get_one_sentence():
        try:
            r = requests.get(POEM_API)
            if r.ok:
                concent = r.json().get("content")
                return concent
            return DEFAULT_SENTENCE
        except:
            print("get POEM_API wrong")
            return DEFAULT_SENTENCE

@register
class DayPoem(Plugin):
    name = "daypoem"

    def __init__(self, config: dict):
        super().__init__(config)
        scheduler_thread = threading.Thread(target=self.start_schedule)
        scheduler_thread.start()

    def did_receive_message(self, event: Event):
        pass

    def will_generate_reply(self, event: Event):
        query = event.context.query
        if query == self.config.get("command"):
            event.reply = self.command_poem_and_image()
            event.bypass()

    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "每日诗词和配图"

    def start_schedule(self):
        schedule_time_poem = self.config.get("schedule_time", "10:00")
        schedule.every().day.at(schedule_time_poem).do(self.poem_daily_push)
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    def command_poem_and_image(self):
        logger.info("Start command poem")
        content = self.get_poem()
        poem_reply = Reply(ReplyType.TEXT, content)
        prompt = self.get_prompt_of_poem(content)
        image_url = self.get_image_of_poem(prompt)
        image_reply = Reply(ReplyType.IMAGE, image_url)
        reply = [poem_reply, image_reply]
        return reply
    
    # def command_image(self, poem) -> Reply:
    #     logger.info("Start command poem image")
    #     prompt = self.get_prompt_of_poem(poem)
    #     image = self.get_image_of_poem(prompt)
    #     reply = Reply(ReplyType.IMAGE, image)
    #     return reply
    
    def get_poem(self) -> str:
        poem = get_one_sentence()
        return poem
    

    def poem_daily_push(self):
        logger.info("Start daily push")
        single_chat_list = self.config.get("single_chat_list", [])
        group_chat_list = self.config.get("group_chat_list", [])
        content = self.get_poem()
        prompt_of_poem = self.get_prompt_of_poem(content)
        self.get_image_of_poem(prompt_of_poem)
        for single_chat in single_chat_list:
            send_txt(content, single_chat)
            # send_txt(prompt_of_poem, single_chat)
            send_image("C:\\\\wechat-gptbot-gyb\\\\wechat-gptbot\\\\temp_output\\\\0.jpeg", single_chat)
        for group_chat in group_chat_list:
            send_txt("今日诗词：" + content, group_chat)
            # send_txt(prompt_of_poem, group_chat)
            send_image("C:\\\\wechat-gptbot-gyb\\\\wechat-gptbot\\\\temp_output\\\\0.jpeg", group_chat)
        if os.path.exists(TEMP_OUTPUT_DIR):
            shutil.rmtree(TEMP_OUTPUT_DIR)
    
    def get_poem(self) -> str:
        poem = get_one_sentence()
        return poem

    def get_prompt_of_poem(self, poem):
        prompt = f"revise `{poem}` to a DALL-E prompt"
        from bot.gemini import GenimiBot
        self.bot = GenimiBot()
        result = self.bot.reply_text(prompt)
        prompt_of_poem = result["content"]
        return prompt_of_poem
    
    def get_image_of_poem(self, prompt_of_poem):
        gen = ImageGen(auth_cookie=conf().get("dalle_cookie"))
        normal_image_links = gen.get_images(prompt_of_poem)
        image_url = normal_image_links[0]
        if not os.path.exists(TEMP_OUTPUT_DIR):
            os.mkdir(TEMP_OUTPUT_DIR)
        if not os.path.exists("./{TEMP_OUTPUT_DIR}/0.jpeg"):
            gen.save_images([image_url], TEMP_OUTPUT_DIR)
        return image_url
        # logger.info(f"[{self.name}] Image={image_url}")
        # return image_url
    