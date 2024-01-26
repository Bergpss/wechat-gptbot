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
        schedule_time = self.config.get("schedule_time", "10:00")
        schedule.every().day.at(schedule_time).do(self.poem_daily_push)
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
        gen = ImageGen(auth_cookie="ipv6=hit=1706244823163&t=6; MUID=24E33E4F0BC46DE13AC52D3B0AAA6C0D; MUIDB=24E33E4F0BC46DE13AC52D3B0AAA6C0D; SRCHD=AF=B00032; SRCHUID=V=2&GUID=B2B4572BA1E048DAB12957B771F3FCAA&dmnchg=1; MicrosoftApplicationsTelemetryDeviceId=757f69e1-4a13-497d-99f4-4e883528a819; _UR=QS=0&TQS=0&cdxcls=0; USRLOC=HS=1&ELOC=LAT=34.03925704956055|LON=-118.26509857177734|N=Los%20Angeles%2C%20California|ELT=6|; _Rwho=u=d; ipv6=hit=1706239417644&t=6; _HPVN=CS=eyJQbiI6eyJDbiI6MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6MiwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyNC0wMS0yNlQwMDowMDowMFoiLCJJb3RkIjowLCJHd2IiOjAsIlRucyI6MCwiRGZ0IjpudWxsLCJNdnMiOjAsIkZsdCI6MCwiSW1wIjo4LCJUb2JuIjowfQ==; ABDEF=V=13&ABDV=13&MRNB=1706236186919&MRB=0; SRCHHPGUSR=SRCHLANG=en&IG=EABF0F16423F417596B00A45A8CC7F1E&PV=10.0.0&BRW=HTP&BRH=M&CW=933&CH=856&SCW=1164&SCH=2377&DPR=1.0&UTC=480&DM=0&WTS=63841832602&HV=1706236192&PRVCW=933&PRVCH=856&PR=1&SPLSCR=1&CIBV=1.1498.2&EXLTT=3; CSRFCookie=865783fa-e27b-4883-8c99-e2c0709e900c; _EDGE_S=SID=2127185966C56F9935870C4B673E6E5A; ANON=A=C106E689DFEF1E3385C811C7FFFFFFFF&E=1d56&W=1; NAP=V=1.9&E=1cfc&C=0lorBU5WrSYVnUDhb4T7DiZwROtRPbQZW9IVKO2aWrwF0XCfSPalmA&W=1; PPLState=1; KievRPSSecAuth=FAByBBRaTOJILtFsMkpLVWSG6AN6C/svRwNmAAAEgAAACDYQ1A86eoTGMAR1FEj9GeicLRIjsi0E+W154Cs+Rv/q94isBSyhND1SXdOck1DquN3vgoHXNzd35M1Pv+t1GlpLDgbZXlLDPGS4G3fxQLW2gKu82by+LKswv5gCfVDtGuSLWDUMW37lszDfK5/N88YEG88z9ldZcZyGpqyDF2jSLPFiGcveMJAKcjQK9XVhR96jRcjvxJhK/0xk7ySaUdzMMoKl0re2YuAC61PbiZnu+ZW7RoNP5/VmSNoOGfvkEYmPJIOP4oAJ6t4mVPExHuFCJ3fzcWuMP3KTGdh9AyNTEZCNghTm6sp2/9zrL8ZQeAoGI/Eb1iz8JARR3MLMtWXGIleJiz2VIW8DEtNUtShkda5WsFN4XFkbB4hgjkGFsrNxiTGCHRPi0agjpKECUNBdJ4wndSWBkPjprqPPC5kxt479lJk7dvtI9xrRRhVXkRS+7+LktoKbu245+hH/jC+AsHBMUjVsCaPQaShhe2Yr5BSSD8q2FhxEwdR1GEH8/U98lfjCPrENW1I8roUN79bSUKMm3OVYhYHNf7xhq6s4YhhCZXTk9+GMXC5yHlYzdcIiiOabVmK8UJvu9wSfCRBwQvanxXQxRhZ7st/igrZIdWRYxEoDo3LlEhHG05uHrlPepN+NlNoN+bebZb92kqJJe90KD9V2Obw4wOgrBByxkLyD4gRnI/MfrYFdADfyOr8BZ88xLXOk7MsLxgApkR2nwgnKeQH1gzFgNBi1HcZdUxBL9enVgZGDhqASdka4lUXsuSBhWm2SBa4idb8JOa9ioArGRyGdk6Uj1374avoFRE3jaNFH/8QdTeXN6CD/JjM8bmi5M8mwubVIczaEJFRrImzWkdbefgHKztSaS55zrjbSmvNEgIF1k4plaWTfYcY7veIq1f9CX2vtRpN31Q464k3nENipcad9zjhS+ZY196ivj6RZV8BGrA53+629svvxY+YPAO2O03GrrbBxh7raEOiCl7Tj6th0Ldht2i6w6NaQ0yaVC0CLKXKb1ezQlZfwdg2/hG++2YhKi7ITABdVt33oCWpaPJZMFYAsEFv90JOaoV2RBVFS7FcyRHfHOJ29L7nDSF7ZsRntQJmyUVRAKFE1qzugcGQFnDQTanpKJsNqqf6sKpsDQ+MOMKBJOnWdEaFIgXtbcw9Q9MPAE7qDFPVzHzfRKA0VSoC1evmHdEH6f5hmezs+tcNkEToPG41P8M90bRUJlUcd8SniJDJJHxPHtf/UHYKPDSJGy8M21PR7nbhxKVVFRLUbqMwjl+wAKMr1S0kNi/vIQYSJB8DoBz+bxKIK+MuGGD08Qzca6eHjofloz+nJ6Rx1lwhYOA0mvhBnIFUZ30mZG6Z9AF3FkdSGHYULQAdMyr5XHwq0jhYlObLB/1T85PV3DUhjwKg6NLL7KnLDS3k/m4GN3IXDjOVWDa/KqiZKFADo4laui2tZ4HjeDSpISOdodPR0uQ==; _U=1jtIDUqcXpo9Ia_6iNqR9U2iEX8ukUl98DL6mYeBmoEvbOHnn-GLKQrH56VKhP5smsYv6caAlMVaYNig3fOPP0AAzoD-yxYfJgZsAjqqUx-CLp8KX7jzmaU1BITjxgMJJF9m2XKQ9mi02zV6XfPP_63ertoGwhE8jBIj1yvqdC4wRD5Cs_C2rnvn0rcUyb0lQsJa46zTn2IXC-Ks-HFSfWg; WLS=C=77f12073534215a0&N=Berg; WLID=RAzuQRgQ32TEzPaXtVY+UE3uEsqzkh2eSxgBlbkt+ITZGTqLX6oqA66HmH2a1qkOb05fwnWvN26QyV9w03e5fkYMscv/FC8eiz8hxjrJo3Q=; SnrOvr=X=rebateson; GI_FRE_COOKIE=gi_prompt=4&gi_fre=2&gi_sc=1; SRCHUSR=DOB=20230821&T=1706241224000&POEX=W; _SS=SID=0A85CB32F19663673145DF20F01262E3&R=778&RB=778&GB=0&RG=0&RP=778; _RwBf=r=1&ilt=10&ihpd=1&ispd=4&rc=778&rb=778&gb=0&rg=0&pc=778&mtu=0&rbb=0.0&g=0&cid=&clo=0&v=7&l=2024-01-25T08:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&o=0&p=bingcopilotwaitlist&c=MY00IA&t=7823&s=2023-02-10T04:32:08.3991390+00:00&ts=2024-01-26T03:53:48.4244832+00:00&rwred=0&wls=2&wlb=0&lka=0&lkt=0&TH=&ard=0001-01-01T00:00:00.0000000&rwdbt=2023-03-02T19:08:27.0963659-08:00&wle=0&ccp=0&aad=0&mta=0&e=qAb_0heINQRzx5F8DRQGd6ZpbPUKBAL5-F0QCcuA516kvqUG2C9FkE6DjTbguDXXGY6yNvWOeEOlg1iqav2TZQ&A=C106E689DFEF1E3385C811C7FFFFFFFF; GC=IUnjWBnsrevDoSQkeGcmpCB-bSOjmAPG-NtC_IDuwe57ZbCI5cyXjW4XijSaEctumcmrAszL40pSenLjLDQDXA")
        normal_image_links = gen.get_images(prompt_of_poem)
        image_url = normal_image_links[0]
        if not os.path.exists(TEMP_OUTPUT_DIR):
            os.mkdir(TEMP_OUTPUT_DIR)
        if not os.path.exists("./{TEMP_OUTPUT_DIR}/0.jpeg"):
            gen.save_images([image_url], TEMP_OUTPUT_DIR)
        return image_url
        # logger.info(f"[{self.name}] Image={image_url}")
        # return image_url
    