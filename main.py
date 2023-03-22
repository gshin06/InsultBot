import discord
import os
import json
import requests
import random
from discord.ext import commands
from replit import db
from webserver import keep_alive

client = commands.Bot(command_prefix="$$", intents=discord.Intents.all())

# API's Used
# nekos.life
# evilinsult.com


#Helper Functions
#------------------------------------------------------------------
#Pulls an insult from the API
def get_insult():
  response = requests.get(
    "https://evilinsult.com/generate_insult.php?lang=en&type=json")
  json_data = json.loads(response.text)
  insult = json_data['insult']
  return insult


#Adds a new insult to the db
def add_insult(new_insult):
  if "insults" in db.keys():
    if new_insult in db["insults"]:
      return False
    insults = db["insults"]
    insults.append(new_insult)
    db["insults"] = insults
  else:
    db["insults"] = [new_insult]
  return True


#Deletes an insult from the db
def delete_insult(index):
  insults = db["insults"]
  if len(insults) > index:
    del insults[index]
  db["insults"] = insults


#Commands
#------------------------------------------
#Ready notification
@client.event
async def on_ready():
  print(f'Logged on as {client.user.name}')


#Send a random insult from the API
@client.command(aliases=['insult'])
async def inspire(ctx, user: discord.User):
  insult = get_insult()
  await ctx.send(insult + " " + user.mention)


#If the user doesn't input a member to insult
@inspire.error
async def inspire_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send('You need to ping someone.')


#Private message an insult to a user
@client.command()
async def directInsult(ctx, user: discord.User):
  try:
    await user.send(get_insult())
    await ctx.send('Your insult has been sent.')
  except:
    await ctx.send(':x: Member had their dm close, insult not sent.')


#If the user forgets to put someone to dm.
@directInsult.error
async def directInsult(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send('You must input who you want to insult.')


#Add an insult to the database
@client.command()
async def add(ctx, *, message):
  if add_insult(message) == True:
    await ctx.send("New insult added.")
  else:
    await ctx.send("Insult already in database.")


#Delete an insult from the database using a provided index
@client.command()
async def delete(ctx, message):
  insults = []
  if "insults" in db.keys():
    index = int(message)
    delete_insult(index)
    insults = db["insults"]
  await ctx.send(insults)


#Send a random insult
@client.command()
async def test(ctx):
  await ctx.send(random.choice(db["insults"]))


#Display all insults in the database
@client.command()
async def list(ctx):
  embed = discord.Embed(title="List of Insults")
  counter = 0
  for x in db["insults"]:
    embed.add_field(name=counter, value=x)
    counter = counter + 1
  await ctx.send(embed=embed)


#Clear all insults in the databse
@client.command()
async def clearall(ctx):
  db["insults"].clear()
  await ctx.send("Insults all cleared.")


#Random anime image test
@client.command()
async def neko(ctx):
  cat = requests.get('http://api.nekos.fun:8080/api/laugh')
  res = cat.json()
  embed = discord.Embed()
  embed.title = get_insult()
  embed.set_image(url=res['image'])
  await ctx.send(embed=embed)


#Poll Bot Command
@client.command()
async def poll(ctx, question, *options: str):
  if (len(options) == 2 and options[0] == "Yes" and options[1] == "No"):
    reactions = ['✅', '❌']
  else:
    reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

  description = []
  for x, option in enumerate(options):
    description += "\n {} {}".format(reactions[x], option)

  embed = discord.Embed(title=question, description=''.join(description))
  react_msg = await ctx.send(embed=embed)
  for reaction in reactions[:len(options)]:
    await react_msg.add_reaction(reaction)


#Run the bot
keep_alive()
client.run(os.environ['TOKEN'])
