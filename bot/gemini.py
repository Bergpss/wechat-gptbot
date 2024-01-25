import os
import pathlib
import textwrap
from config import conf
import google.generativeai as genai
# Used to securely store your API key
# from google.colab import userdata
from IPython.display import display
from IPython.display import Markdown
from common.reply import Reply, ReplyType
from common.context import ContextType, Context
from common.session import Session
from utils.log import logger

class GenimiBot:
    def __init__(self):
        gemini_api_key = conf().get("gemini_api_key")
        genai.configure(api_key=gemini_api_key)
        # os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
        self.name = self.__class__.__name__

    def reply(self, context: Context) -> Reply:
        query = context.query
        logger.info(f"[{self.name}] Query={query}")
        if context.type == ContextType.CREATE_IMAGE:
            return self.reply_img(query)
        else:
            # session_id = context.session_id
            # session = Session.build_session_query(context)
            response = self.reply_text(query)
            logger.info(f"[{self.name}] Response={response['content']}")
            # if response["completion_tokens"] > 0:
            # Session.save_session(
            #     response["content"], session_id, response["total_tokens"]
            # )
            return Reply(ReplyType.TEXT, response['content'])
    
    def reply_text(self, query):
        # for m in genai.list_models():
        #   if 'generateContent' in m.supported_generation_methods:
        #     print(m.name)
        # For text-only prompts, use the gemini-pro model:
        try:
            model = genai.GenerativeModel('gemini-pro')
            os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
            response = model.generate_content(query)
            os.environ['HTTP_PROXY'] = ''
            return {
                "content": response.text,
            }
        except Exception as e:
            logger.warn(f"[{self.name}] GeminiError: {e}")
            result = {"content": "Please ask me again"}
        return result
