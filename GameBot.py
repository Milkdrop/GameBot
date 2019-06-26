#coding=utf-8
import os
import discord, platform, asyncio
import random, time
import subprocess
import pyscreenshot as ImageGrab
import io
from pynput.keyboard import Key, Controller

client = discord.Client()
token = "[ADD YOUR TOKEN HERE]"

loadedrom = "PokemonRed.gb"
pathtorom = os.getcwd() + "/" + loadedrom
msg = None
ch = None
UpdateLimit = 3
CurrentUpdate = 0
keyboard = Controller()

movtime = 0.25
# Emotes
emotes = {"LeftArrow": "\u2B05", "DownArrow": "\u2B07", "UpArrow": "\u2B06", "RightArrow": "\u27A1", "AButton": "\U0001F170", "BButton": "\U0001F171", "Start": "\u25B6", "Select": "\U0001F502"}

def IsValidReaction(react):
	global emotes
	for emote in emotes:
		if (react == emotes[emote]):
			return True
	return False
	
def GetWindowCoords():
	outs = str(subprocess.check_output(["wmctrl", "-lG"]))[2:-1].split("\\n")
	for f in outs:
		if (f.find("Gambatte SDL") != -1): #Found Window
			f2 = f.split(" ")
			f = []
			for elem in f2:
				if (elem != ""):
					f.append(elem)

			# Brut
			X1 = int(f[2])
			Y1 = int(f[3]) - 26
			X2 = X1 + int(f[4]) - 1
			Y2 = Y1 + int(f[5])
			return (X1, Y1, X2, Y2)
	return None
	
async def UpdateFrame():
	global msg
	global CurrentUpdate
	global UpdateLimit
	while True:
		if (ch != None):
			CurrentUpdate += 1
			if (CurrentUpdate < UpdateLimit):
				print ("Updating Frame...")
				await SendImage()
			elif (CurrentUpdate == UpdateLimit):
				print ("Updating Frame+Emojis...")
				await SendImage(True) # React
				print ("All good.")
			else:
				await asyncio.sleep(0.5)
		else:
			await asyncio.sleep(0.5)

async def SendImage(react=False):
	global msg
	global ch
	global emotes
	coords = GetWindowCoords()
	os.system("wmctrl -a 'Gambatte SDL'") # Focus Window
	im = ImageGrab.grab(bbox=(coords[0], coords[1], coords[2], coords[3])) # X1,Y1,X2,Y2
	im.save("frame.jpg")
	msgold = msg
	msg = await ch.send(file=discord.File("frame.jpg"))
	if (msgold != None):
		await msgold.delete()
	if (react):
		await msg.add_reaction(emotes["AButton"])
		await msg.add_reaction(emotes["BButton"])
		await msg.add_reaction(emotes["LeftArrow"])
		await msg.add_reaction(emotes["DownArrow"])
		await msg.add_reaction(emotes["UpArrow"])
		await msg.add_reaction(emotes["RightArrow"])
		await msg.add_reaction(emotes["Start"])
		await msg.add_reaction(emotes["Select"])

@client.event
async def on_ready():
	print('All good! Name: ' + client.user.name)
	asyncio.ensure_future(UpdateFrame()) # Fire and Forget
	
	await client.change_presence(activity=discord.Game(name='%activate'))

async def SendKey(k, movkey=False):
	global keyboard
	global movtime
	keyboard.press(k)
	if (movkey == False):
		await asyncio.sleep(0.25)
	else:
		await asyncio.sleep(movtime)
		
	keyboard.release(k)
	
@client.event
async def on_reaction_add(reaction, user):
	global msg
	global emotes
	global CurrentUpdate
	if (reaction.message.author == client.user and reaction.count != 1): # We got a react
		reaction = str(reaction) # Simplify
		if (IsValidReaction(reaction)):
			print ("Input Received: " + reaction)
			os.system("wmctrl -a 'Gambatte SDL'") # Focus Window
			
			if (reaction == emotes["LeftArrow"]):
				await SendKey(Key.left, True)
			elif (reaction == emotes["DownArrow"]):
				await SendKey(Key.down, True)
			elif (reaction == emotes["UpArrow"]):
				await SendKey(Key.up, True)
			elif (reaction == emotes["RightArrow"]):
				await SendKey(Key.right, True)
			elif (reaction == emotes["AButton"]):
				await SendKey("d")
			elif (reaction == emotes["BButton"]):
				await SendKey("c")
			elif (reaction == emotes["Start"]):
				await SendKey(Key.enter)
			elif (reaction == emotes["Select"]):
				await SendKey(Key.shift_r)
			
			CurrentUpdate = 0
			
@client.event
async def on_message(message):
	global msg
	global ch
	global CurrentUpdate
	global movtime
	
	if message.author == client.user:
		return
	
	if (message.content == "%activate"):
		if (GetWindowCoords() == None): # No emulator running
			os.system("gambatte_sdl " + pathtorom + " --scale 2 &")
			
		while (GetWindowCoords() == None): # Avoid any issues
			time.sleep(0.1)
		
		ch = message.channel
		msg = None
		CurrentUpdate = 0
	elif (message.content == "%stop"):
		await msg.delete()
		ch = None
	elif (message.content == "%loadrom"):
		pass
	elif (message.content[:8] == "%movtime"):
		inp = message.content[9:]
		movtime = float(inp)
		if (ch != None and message.channel == ch):
			await ch.send("Setting movement speed as: **" + str(inp) + "** (Default: 0.25)")
while True:
	try:
		client.run(token)
		client.close()
	except Exception as e:
		print (e)