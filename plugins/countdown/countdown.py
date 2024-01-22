from datetime import datetime
from plugins import register, Plugin, Event, logger, Reply, ReplyType

@register
class Countdown(Plugin):
    name = "countdown"
    def did_receive_message(self, event: Event):
        pass

    def will_generate_reply(self, event: Event):
        query = event.context.query
        if query == self.config.get("command"):
            event.reply = self.reply()
            event.bypass()

    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "Record your important day count. 为你记录重要日期。"

    def reply(self) -> Reply:
        # get first day of next year
        next_new_year_day = datetime(datetime.now().year + 1, 1, 1).strftime("%Y-%m-%d")
        important_thing = self.config.get("important_thing", "元旦")
        important_day = self.config.get("important_day", next_new_year_day)
        important_daytime = datetime.strptime(important_day, "%Y-%m-%d")
        time_difference = important_daytime - datetime.now()
        reply_text = "今日是 " + datetime.now().strftime("%Y-%m-%d") + ", 距离 " + important_thing + " 还有 " + str(time_difference.days) + " 天！"
        reply = Reply(ReplyType.TEXT, reply_text)
        return reply