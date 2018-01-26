import re

class Patterns():
    def __init__(self, bot_id):
        self.bot_id = bot_id
        self.celestia = "(princess )?((celes)?tia|sun ?(butt|horse|pon[ye])|cell?y|(the )princess of (the )suns?|<@!?{}>)".format(bot_id)
        self.hug = re.compile("[_\*](hug(gle)?s|glomps|snug(gle)?s( with)?|squeezes) ({}|every(one|pony))".format(self.celestia), re.IGNORECASE)
        self.greet = re.compile("(hi|hello|hey|(good )?afternoon) (every(one|pony)|(y'?)?all|friends|folks|guys|{})!*".format(self.celestia), re.IGNORECASE)
        self.morning = re.compile("(good |')?mornin(g|')? (every(one|pony)|(y'?)?all|friends|folks|guys|{})!*".format(self.celestia), re.IGNORECASE)
        self.bap = re.compile("(_(baps|smacks|hits|slaps)|bad) {}".format(self.celestia), re.IGNORECASE)
        self.konami = re.compile(r"((up|🔼|⬆|\^)\s?){2}((down|🔽|⬇|v)\s?){2}((left\s?right|⬅\s?➡|◀\s?▶|<\s?>)\s?){2}(B|🅱)\s?(A|🅰)", re.IGNORECASE)
        self.derpi = re.compile(r"derpicdn\.net/img/(view/)?\d+/\d+/\d+/\d+")
