from .common import *

class Talker:
    # ------------------
    # SAYING STUFF
    # ------------------

    def humansay(self, content):
        self.M.append({"role": "user", "content": content})
        self.add_txt("dialogue", f"Player:\n{content}")

    def computersay(self, content):
        self.M.append({"role": "assistant", "content": content})
        self.add_txt("dialogue", f"DM:\n{content}")
        print("DM:", content)

    def computersay_self(self, content):
        self.M.append({"role": "system", "content": content})
        self.add_txt("dialogue", f"DM (to themselves):\n{content}")

    # ------------------
    # Running the Conversation
    # ------------------

    def run(self):
        
        # human does its thing
        query = input(">> ")
        self.humansay(query)

        # computer does its thing
        self.act()
        self.think()
        self.respond()
        self.act()

    def loop(self):
        while True:
            self.run()
