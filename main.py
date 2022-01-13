import discum
import os

if os.name == "posix":
    os.system('clear')
else:
    os.system('cls')

class MassMention(object):

    def __init__(self):
        self.user_token = input("Token: ")
        self.guild_id = input("Guild ID: ")
        self.channel_id = input("Channel ID: ")
    
    def scrape_member_ids(self):
        session = discum.Client(token=self.user_token, log=False)
        test = session.gateway.fetchMembers(
            self.guild_id, 
            self.channel_id, 
            reset=True, 
            keep="all"
        )
        session.gateway.finishedMemberFetching(self.guild_id)

        @session.gateway.command
        def start_getting_ids(resp):
            if session.gateway.finishedMemberFetching(self.guild_id):
                session.gateway.removeCommand(start_getting_ids)
                session.gateway.close()
            
        session.gateway.run()

        for id in session.gateway.session.guild(self.guild_id).members:
            with open("ids.txt", "w") as f:
                f.write("{}\n".format(id))
            print("<@{}>".format(id))

if __name__ == "__main__":
    client = MassMention()
    client.scrape_member_ids()
