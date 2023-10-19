import discord
from discord.ext import commands
from rasa.core.agent import Agent
import requests
import json

# URL do servidor de ação personalizada do Rasa
rasa_action_endpoint = 'http://localhost:5055/webhook'

base_prompt =  (
    "You're a tour guide responsible for giving "
    "recommendations of places to visit, restaurants, "
    "historical facts, curiosities and much more."
    "I am your guest. I may ask you questions about anything "
    "related to travelling. Before I ask anything about a place, "
    "you must know where I am (if I haven't already told you)."
    "Here's my question:"
)

class MyClient(discord.Client):
    def create_agent(self):
        self.agent = Agent.load("rasa_3x/models/20231019-195318-auburn-genre.tar.gz")

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        
        output = await self.agent.handle_text(message.content)

        
        try:
            await message.channel.send(output[0]['text'])
        except:
            data = {
                    "next_action": "gepeto",  # Nome da ação personalizada
                    "tracker": {
                        "latest_message": {
                            "text": base_prompt+message.content  # Sua mensagem de entrada
                        },
                        "sender_id": str(self.user)  # ID único do remetente
                    }
                }
            
            response = requests.post(rasa_action_endpoint, json=data)

            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data["response"]
                # A resposta da ação personalizada está em response_data
                await message.channel.send(response_text)
            else:
                await message.channel.send(response.status_code)



def create_bot() -> discord.Client:
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)

    client.create_agent()

    return client
    

    # bot = commands.Bot(command_prefix="!", intents=intents)

    # @bot.event
    # async def on_ready():
    #     print(f"{bot.user.name} has connected to Discord!")

    # @bot.command(name="history", help="Return a list of historical facts about a city")
    # async def get_history(ctx: commands.Context, *city_name):
    #     city = " ".join(city_name)
    #     await ctx.send(f"It's history time about {city}")

    # @bot.command(
    #     name="restaurants", help="Returns a list of interesting restaurants in a city"
    # )
    # async def get_restaurants(ctx: commands.Context, *city_name):
    #     city = " ".join(city_name)
    #     await ctx.send(f"Here are some restaurants in {city}")

    # return bot
