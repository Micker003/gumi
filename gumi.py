print("Starting imports")
#from _typeshed import NoneType
import sys

from discord.ui.item import Item
print(sys.version)
from datetime import datetime, timezone
import calendar
import math
import logging
import discord
import mysql.connector
import os
import emoji
import random
import asyncio
import traceback
from discord.ext import commands
from dotenv import load_dotenv
print("Imports done!")

load_dotenv() #Load authentication data
TOKEN = os.getenv('DISCORD_TOKEN')
MYSQLUNAME = os.getenv('MYSQLUNAME')
MYSQLPWD = os.getenv('MYSQLPWD')
ADMINID = os.getenv('ADMINID')
BRANCH = os.getenv('BRANCH')

DEVBRANCH = False
if(BRANCH == "DEV"):
  DEVBRANCH = True

#Emote initialisation
blankEmote = "<:Blank:864112967658373121>"
commonEmote = "C"
uncommonEmote = "U"
rareEmote = "R"
superEmote = "S"
supeREmote = "R"
ultraEmote = "U"
ultRaEmote = "R"
legendaryEmote = "L"

#Pity limits, in amount of pulls
Gacha1PityULim = 100
Gacha3PityRLim = 100
Gacha3PitySRLim = 600

#color pallette initialisation
MiharuBlue = 0xCDD3FE
AxlPink = 0xFF9599
GumiYellow = 0xFFD68A

#ReactionInitialisation
BotAdminOnlyCommand = discord.Embed(title="You don't have permission to use this command. This is an bot-admin only command.", color=discord.Colour.dark_grey())

def char_is_emoji(character):
  return character in emoji.UNICODE_EMOJI

def getTimestamp(): #Amount of seconds since Unix
  current_datetime = datetime.utcnow()
  current_timetuple = current_datetime.utctimetuple()
  current_timestamp = int(calendar.timegm(current_timetuple))
  return current_timestamp

def getRarityCoefeccient(rarity):
  '''
  Gets coeffeccient to combine with most operations to deal with rarity
  '''
  if (rarity == 0): return 1
  if (rarity == 1): return 1.1
  if (rarity == 2): return 1.25
  if (rarity == 3): return 1.5
  if (rarity == 4): return 1.75
  if (rarity == 5): return 2.1
  else: return 1

def getRarityName(rarity):
  '''
  Gets name of rarity rank
  '''
  if (rarity == 0): return "Common"
  if (rarity == 1): return "Uncommon"
  if (rarity == 2): return "Rare"
  if (rarity == 3): return "Super Rare"
  if (rarity == 4): return "Ultra Rare"
  if (rarity == 5): return "Legendary"
  else: return 1

def getRarityEmotes(rarity):
  '''
  Gets emote string of rarity rank
  '''
  if (rarity == 0): return (commonEmote)
  if (rarity == 1): return (uncommonEmote)
  if (rarity == 2): return (rareEmote)
  if (rarity == 3): return (superEmote + supeREmote)
  if (rarity == 4): return (ultraEmote + ultRaEmote)
  if (rarity == 5): return (legendaryEmote)
  else: return 1

def makeLegibleTime(SecondsIn):
  '''
  Makes a legible (x)s/m/h/d out. 
  '''
  if(SecondsIn < 60):
    return (SecondsIn + 's')
  elif(SecondsIn < 3600):
    return ((SecondsIn // 60) + 'm')
  elif(SecondsIn < 86400):
    return((SecondsIn // 3600) + 'h')
  else:
    return((SecondsIn // 86400) + 'd')

def sqlstr(orgstr):
  '''
  Adds brackets around a string to allow it to be send as SQL-command string. Needed for strings and dates. Also whitelists characters that are allowed to be serched
  '''
  sqlstring = ""
  for x in range(0, len(str(orgstr))):
    char = orgstr[x]
    if(char.isalpha()): #Is a letter?
      sqlstring += char
    elif(char.isnumeric()): #Is a number?
      sqlstring += char
    elif(char == " "): #Is a space?
      sqlstring += char
    elif(char_is_emoji(char)): #Is emoji?
      sqlstring += char
    #Else, not character that has to be searched
    
  return ("'" + str(orgstr) + "'")

lmydb = mysql.connector.connect(#Needed for "closes if wasn't closed" scenarios in cases of errors
  host="localhost",
  user=MYSQLUNAME,
  password=MYSQLPWD,
  database="gumi"
)

'''
def mydbsecondary():
  mydb = mysql.connector.connect( #connect to database
    host="localhost",
    user=MYSQLUNAME,
    password=MYSQLPWD,
    database="gumi"
  )
  return mydb
'''

def mydbconnect():
  '''
  try: #Close connection if was not closed previously
    lmydb.close #ignore warn
  except:
    temp = True
  '''
  mydb = mysql.connector.connect( #connect to database
    host="localhost",
    user=MYSQLUNAME,
    password=MYSQLPWD,
    database="gumi"
  )
  lmydb = mydb
  return mydb

#cursor = mydb.cursor()

def hasUserProfile(UID):
  UIDstr = str(UID)
  #mydb = mydbsecondary()
  with mysql.connector.connect(
    host="localhost",
    user=MYSQLUNAME,
    password=MYSQLPWD,
    database="gumi"
  ) as mydb:
    with mydb.cursor() as cursor:
      cursor.execute(
      "SELECT UID, COUNT(*) FROM Users WHERE UID = %s GROUP BY UID",
      (UIDstr,)
      )
      results = cursor.fetchall()
      rowct = cursor.rowcount #Seems to be necessary to be sure to fetch everything
  """
  cursor = mydb.cursor
  mydb.cursor.execute(
    "SELECT UID, COUNT(*) FROM Users WHERE UID = %s GROUP BY UID",
    (UIDstr,)
  )
  results = cursor.fetchall() #Seems to be necessary to be sure to fetch everything
  """
  if (rowct == 0):
    mydb.close
    return(False)
  else:
    mydb.close
    return(True)

def changeBalance(UID, CarrotsDelta, CheeseDelta, cursor): 
  '''
  Before using, check whether user has user account. Commit after usage
  '''
  query1 = '''SELECT Carrots, Cheese
  FROM Users
  WHERE UID = ''' + str(UID)
  cursor.execute(query1)
  cursorout = cursor.fetchall()
  Carrots = (cursorout[0])[0] + int(CarrotsDelta)
  Cheese = (cursorout[0])[1] + int(CheeseDelta)
  query2 = '''UPDATE Users
  SET
    Carrots = ''' + str(Carrots) + ''',
    Cheese = ''' + str(Cheese) + '''
  WHERE
    UID = ''' + str(UID)
  cursor.execute(query2)

def getBalance(UID): 
  '''
  Before using, check whether user has user account. Out: Carrot, Cheese
  '''
  query = '''SELECT Carrots, Cheese
  FROM Users
  WHERE UID = ''' + str(UID)
  with mysql.connector.connect(
    host="localhost",
    user=MYSQLUNAME,
    password=MYSQLPWD,
    database="gumi"
  ) as mydb:
    with mydb.cursor() as cursor:
      cursor.execute(query)
      cursorout = cursor.fetchall()

  Carrots = (cursorout[0])[0] 
  Cheese = (cursorout[0])[1]
  return(Carrots, Cheese)

def getSelectedCharID(UID): 
  '''
  Before using, check whether user has user account. Commit after usage
  '''
  query = '''SELECT CurrentSelectedCharacter
  FROM Users
  WHERE UID = ''' + str(UID)
  with mysql.connector.connect(
    host="localhost",
    user=MYSQLUNAME,
    password=MYSQLPWD,
    database="gumi"
  ) as mydb:
    with mydb.cursor() as cursor:
      cursor.execute(query)
      cursorout = cursor.fetchall()
  CharID = (cursorout[0])[0]
  return(CharID)

def getAmountItemOwned(UID, ItemID):
  query = '''SELECT Amount
  FROM ItemOwnership
  WHERE
    ItemID = ''' + sqlstr(ItemID) + ''' AND UID = ''' + str(UID)
  with mysql.connector.connect(
    host="localhost",
    user=MYSQLUNAME,
    password=MYSQLPWD,
    database="gumi"
  ) as mydb:
    with mydb.cursor() as cursor:
      cursor.execute(query)
      cursorout = cursor.fetchall()
  if(len(cursorout) == 0):
    return 0
  else:
    return (cursorout[0])[0]

def getItemEmoteFromID(ItemID):
  query = '''SELECT Emote
  FROM Items
  WHERE
    ItemID =''' + sqlstr(ItemID)
  with mysql.connector.connect(
    host="localhost",
    user=MYSQLUNAME,
    password=MYSQLPWD,
    database="gumi"
  ) as mydb:
    with mydb.cursor() as cursor:
      cursor.execute(query)
      cursorout = cursor.fetchall()
  if(len(cursorout) == 0):
    return "NOEMOTE"
  else:
    return (cursorout[0])[0]

def getItemNameFromID(ItemID):
  query = '''SELECT ItemName
  FROM Items
  WHERE
    ItemID =''' + sqlstr(ItemID)
  with mysql.connector.connect(
    host="localhost",
    user=MYSQLUNAME,
    password=MYSQLPWD,
    database="gumi"
  ) as mydb:
    with mydb.cursor() as cursor:
      cursor.execute(query)
      cursorout = cursor.fetchall()
  if(len(cursorout) == 0):
    return "NONAME"
  else:
    return (cursorout[0])[0]

def getCharacterNameFromID(CharID):
  query = '''SELECT Name
  FROM Characters
  WHERE
    CharID =''' + str(CharID)
  with mysql.connector.connect(
    host="localhost",
    user=MYSQLUNAME,
    password=MYSQLPWD,
    database="gumi"
  ) as mydb:
    with mydb.cursor() as cursor:
      cursor.execute(query)
      cursorout = cursor.fetchall()
  if(len(cursorout) == 0):
    return "NONAME"
  else:
    return (cursorout[0])[0]

def addCharacterToHarem(UID, CharID, Amount, cursor): 
  '''
  Commit after usage
  '''
  query1 = '''SELECT Amount
  FROM CharacterOwnership
  WHERE
    CharID = ''' + str(CharID) + ''' AND UID = ''' + str(UID)
  cursor.execute(query1) #Fetch user data from database
  cursorout = cursor.fetchall()
  if(len(cursorout) == 0): #If nothing found
    query2 = '''INSERT INTO CharacterOwnership(UID, CharID, Amount)
    VALUES ( ''' + str(UID) + ' , ' + str(CharID) + ' , ' + str(Amount) + ''')
    '''
    cursor.execute(query2)
    #mydb.commit()
  else: #Else, update the amount of seeds owned
    newAmount = (cursorout[0])[0]
    newAmount += Amount
    query3 = """UPDATE CharacterOwnership
    SET
      Amount = """ + str(newAmount) + """
    WHERE
      CharID = """ + str(CharID) + """ AND UID = """ + str(UID) +"""
    """
    cursor.execute(query3)

def addItemToInventory(UID, ItemID, Amount, cursor): 
  '''
  Commit after usage
  '''
  query1 = '''SELECT Amount
  FROM ItemOwnership
  WHERE
    ItemID = ''' + sqlstr(ItemID) + ''' AND UID = ''' + str(UID)
  cursor.execute(query1) #Fetch user data from database
  cursorout = cursor.fetchall()
  if(len(cursorout) == 0): #If nothing found
    query2 = '''INSERT INTO ItemOwnership(UID, ItemID, Amount)
    VALUES ( ''' + str(UID) + ' , ' + sqlstr(ItemID) + ' , ' + str(Amount) + ''')
    '''
    cursor.execute(query2)
    #mydb.commit()
  else: #Else, update the amount of seeds owned
    newAmount = (cursorout[0])[0]
    newAmount += Amount
    query3 = """UPDATE ItemOwnership
    SET
      Amount = """ + str(newAmount) + """
    WHERE
      ItemID = """ + sqlstr(ItemID) + """ AND UID = """ + str(UID) +"""
    """
    cursor.execute(query3)
    print(query3)

bot = commands.Bot(command_prefix=['gumi ', 'Gumi '], help_command=None) #Bot prefix!

'''
class FarmPlantButton(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.value = None
        self.ctx = ctx
        self.UID = ctx.message.author.id

    @discord.ui.button(label='Plant my seeds', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        while True: #
          await interaction.response.send_message('Confirming', ephemeral=True)#not needed
          print("Awaited")
          self.value = interaction.user.id
          nUID = interaction.user.id
          print(self.UID)
          print(nUID)
          if(nUID == self.UID): #Edit is done back there
            self.stop()
            print("Stopped")
          else:
            print("Passed through")
            user = bot.get_user(nUID)
            seedsLeft = getAmountItemOwned(nUID, "CSD")
            print(seedsLeft)
            querycheck = """SELECT AmountPlanted, CarrotFieldSize
            FROM Users
            WHERE UID = """ + str(nUID)
            cursor.execute(querycheck) #Fetch user data from database
            cursorout = cursor.fetchall()
            AmountPlanted = (cursorout[0])[0]
            CarrotFieldSize = (cursorout[0])[1]
            if(AmountPlanted > 0):
              title = "You already have carrots planted. If you wanna try to harvest them, type _gumi farm_"
            elif(seedsLeft == 0):
              title = "You don't have any seeds to plant!"
            else:
              if (seedsLeft > 20): #Should not be hard coded, but...
                seedsLeft = 20
              stopTimestamp = (getTimestamp() + random.randint(10800, 21600)) #Farming takes between 3 and 6 hours
              queryplant = """UPDATE Users
              SET
                FarmStartTimestamp = """ + str(getTimestamp()) + """,
                FarmStopTimestamp = """ + str(stopTimestamp) + """,
                AmountPlanted = """ + str(seedsLeft) + """
              WHERE
                UID = """ + str(nUID)
              print(queryplant)
              addItemToInventory(nUID, "CSD", (seedsLeft * (-1)), cursor)
              cursor.execute(queryplant)
              mydb.commit
              title = "You planted " + str(seedsLeft) + " seeds"
            embedVar = discord.Embed(title=title, color=discord.Colour(GumiYellow))
            await self.ctx.send(embed = embedVar)
'''        

class MakeProfileButton(discord.ui.Button['MakeProfile']):
    def __init__(self):
      super().__init__(style=discord.ButtonStyle.success, label='I accept!')
    async def callback(self, interaction:discord.Interaction):
      UID = interaction.user.id
      date = datetime.utcnow().strftime("%Y%m%d")
      makeProfileQuery = '''INSERT INTO Users(UID, ProfileCreated)
      VALUES ( ''' + str(UID) + ' , ' + str(date) + ''')
      '''
      makeMainCharacterQuery = '''INSERT INTO CharacterOwnership(UID, CharID, Amount)
      VALUES ( ''' + str(UID) + ''' , 1 , 1 )
      '''
      mydb = mydbconnect()
      cursor = mydb.cursor()
      cursor.execute(makeProfileQuery)
      cursor.execute(makeMainCharacterQuery)
      #query for giving MC to user
      mydb.commit() #Saves edit to database
      mydb.close() #Closes connection
      view: MakeProfile = self.view
      self.disabled = True
      embedVar = discord.Embed(title='''You made your profile!''', description='''_Gumi will explain what you can do by telling her "gumi gather"!_
      
      First of all, there are a few rules I gotta tell you.
      > You are not allowed to use alts to gain any advantage over other users
      > You are not allowed to use bots or scripts for this bot (this breaks the Discord TOS as well, by the way)
      > You are not allowed to (overly) abuse exploits if they give you an advantage over other users

      If you break any of these rules, you may get your account blocked or wiped.
      ''',  color=discord.Colour.green())
      embedVar.add_field(name="Privacy Policy", value="The only personally identifyable information I collect is your Discord ID. For more information, [go here to read the full privacy policy](https://sites.google.com/view/gumibot/privacy-policy).", inline=False)
      embedVar.add_field(name="Questions?", value="If you have any questions, ask them in the [support server](https://discord.gg/DHD3S2B8DQ).", inline=False)
      embedVar.set_footer(text='You accepted the rules and the Privacy Policy!')
      await interaction.response.edit_message(embed = embedVar, view = view)
        
class MakeProfile(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MakeProfileButton())

@bot.command(aliases=["Gacha", "Banner", "banner", "banners", "Banners"] , description = "Shows the gacha list/banners, gotten from the sql")
async def gacha(ctx):
  query = """SELECT Text, ImgLink, Footer
  FROM GachaView
  ORDER BY ViewID DESC""" #Get latest.
  mydb = mydbconnect()
  cursor = mydb.cursor()
  cursor.execute(query) #Fetch user data from database
  cursorout = cursor.fetchall()
  mydb.close()
  Text = (cursorout[0])[0]
  ImgLink = (cursorout[0])[1]
  Footer = (cursorout[0])[2]
  if(Text == ""):
    Text = "No banner information given."
  embedVar = discord.Embed(title="Welcome to the gacha zone", description= Text, color=discord.Colour(GumiYellow))
  if(ImgLink != ""):
    embedVar.set_image(url=ImgLink)
  if(Footer != ""):
    embedVar.set_footer(text=Footer)
  await ctx.send(embed = embedVar) #Add buttons later

@bot.command(aliases=['setchar', "Setchar", "SetChar", "setcharacter", "Setcharacter"] , description = "Set your current character")
async def setCharacter(ctx, CharID=0):
  UID = ctx.message.author.id
  if(hasUserProfile(UID) == False):
    embedVar = discord.Embed(title="You don't have an profile yet!", color=discord.Colour.red())
    embedVar.set_footer(text="You can make a profile using gumi start")
  elif(CharID == 0):
    embedVar = discord.Embed(title="You have to enter a character ID of the character you want to set", color=discord.Colour.red())
  else:
    q2 = 'SELECT * FROM `CharacterOwnership` WHERE `UID` = ' + str(UID) + ' AND `CharID` = ' + str(CharID)
    mydb = mydbconnect()
    cursor = mydb.cursor()
    cursor.execute(q2) #Fetch user data from database
    cursorout = cursor.fetchall()
    if(len(cursorout) == 0): #User doesn't have the wished character
      embedVar = discord.Embed(title="You don't have a character with this ID", color=discord.Colour.red())
    else:
      querysaveselectchar = '''UPDATE Users
      SET
        CurrentSelectedCharacter = ''' + str(CharID) + '''
      WHERE
        UID = ''' + str(UID)
      cursor.execute(querysaveselectchar)
      mydb.commit()
      embedVar = discord.Embed(title=(getCharacterNameFromID(CharID) + " is now selected"), color=discord.Colour.red())
    mydb.close
  await ctx.send(embed = embedVar)

@bot.command(aliases=["Pull"] , description = "Pull new characters from a banner")
async def pull(ctx, bannerID=0):
  embedawait = discord.Embed(title="Pulling...", color=discord.Colour.dark_grey())
  message = await ctx.send(embed = embedawait)
  UID = ctx.message.author.id
  UNAME = ctx.message.author.name
  title = UNAME + " pulled"
  priceMultiplier = 1 
  pullCount = 1
  if((bannerID % 2) == 0): #If number even, is a 10pull
    if(bannerID != 0):
      priceMultiplier = 9 
      pullCount = 10
      bannerID += -1 #Get gacha to be pulled itself
  if(hasUserProfile(UID) == False):
    embedVar = discord.Embed(title="You don't have an profile yet. No waifus for you... well, until you make a profile and can afford to pull", color=discord.Colour.red())
    embedVar.set_footer(text="You can make a profile using gumi start")
  elif(bannerID == 0):
    embedVar = discord.Embed(title="Specify the banner ID of the banner you want to pull", color=discord.Colour(AxlPink))
  else:
    query = '''SELECT CarrotPrice, CheesePrice, ItemID, ItemAmount, CRewardLim, URewardLim, UCharLim, RRewardLim, RCharLim, SRCharLim, URCharLim, LCharLim, FeaturedCharID
    FROM Gachas
    WHERE BannerID = ''' + str(bannerID)
    mydb = mydbconnect()
    cursor = mydb.cursor()
    cursor.execute(query) #Fetch user data from database
    cursorout = cursor.fetchall()
    queryprofile = '''SELECT Carrots, Cheese, Gacha1PityU, Gacha3PityR, Gacha3PitySR
    FROM Users
    WHERE UID = ''' + str(UID)
    cursor.execute(queryprofile)
    profilecursorout = cursor.fetchall()
    Carrots = (profilecursorout[0])[0]
    Cheese = (profilecursorout[0])[1]
    Gacha1PityU = (profilecursorout[0])[2]
    Gacha3PityR = (profilecursorout[0])[3]
    Gacha3PitySR = (profilecursorout[0])[4]

    CarrotPrice = (cursorout[0])[0]
    CheesePrice = (cursorout[0])[1]
    ItemID = (cursorout[0])[2]
    ItemAmount = (cursorout[0])[3]
    CRewardLim = (cursorout[0])[4]
    URewardLim = (cursorout[0])[5]
    UCharLim = (cursorout[0])[6]
    RRewardLim = (cursorout[0])[7]
    RCharLim = (cursorout[0])[8]
    SRCharLim = (cursorout[0])[9]
    URCharLim = (cursorout[0])[10]
    LCharLim = (cursorout[0])[11]
    FeaturedCharID = (cursorout[0])[12] #Featured higher chance something something not yet implemented
    CanAfford = True
    if(ItemAmount != 0):
      ownedAmount = getAmountItemOwned(UID, ItemID)
      ItemAmount = ItemAmount * priceMultiplier
      if(ownedAmount < ItemAmount):
        CanAfford = False
    CheesePrice = CheesePrice * priceMultiplier
    CarrotPrice = CarrotPrice * priceMultiplier
    bal = getBalance(UID)
    CarrotsOwned = bal[0]
    CheeseOwned = bal[1]
    if(CarrotPrice > CarrotsOwned):
      CanAfford = False
    if(CheesePrice > CheeseOwned):
      CanAfford = False
    if(CanAfford == False):
      embedVar = discord.Embed(title="You can't afford this pull", color=discord.Colour.red())
    else:
      if(ItemAmount != 0): #Pay for the pulls
        addItemToInventory(UID, ItemID, ItemAmount, cursor)
      Carrots += (CarrotPrice * -1)
      Cheese += (CheesePrice * -1)

      query = '''SELECT RewardID, ItemID, Carrots, Cheese, ItemCount
      FROM CommonReward'''
      cursor.execute(query) #Fetch user data from database
      CommonRewards = cursor.fetchall()
      CommonRewardsCount = len(CommonRewards)
      query = '''SELECT RewardID, ItemID, Carrots, Cheese, ItemCount
      FROM UncommonReward'''
      cursor.execute(query) #Fetch user data from database
      UncommonRewards = cursor.fetchall()
      UncommonRewardsCount = len(UncommonRewards)

      query = '''SELECT CharID, Rarity
      FROM Characters
      WHERE ObtainableFromGacha = 1'''
      cursor.execute(query) #Fetch user data from database
      AllCharacters = cursor.fetchall()
      CCharacters = []
      UCharacters = []
      RCharacters = []
      SRCharacters = []
      URCharacters = []
      LCharacters = []
      for x in range(0, len(AllCharacters)): #Make lists of characters to pick from
        CurrCharRarity = (AllCharacters[x])[1]
        if(CurrCharRarity == 0):
          CCharacters.append(AllCharacters[x][0])
        elif(CurrCharRarity == 1):
          UCharacters.append(AllCharacters[x][0])
        elif(CurrCharRarity == 2):
          RCharacters.append(AllCharacters[x][0])
        elif(CurrCharRarity == 3):
          SRCharacters.append(AllCharacters[x][0])
        elif(CurrCharRarity == 4):
          URCharacters.append(AllCharacters[x][0])
        elif(CurrCharRarity == 5):
          LCharacters.append(AllCharacters[x][0])
        
      rewardShorts = []
      rewardLongs = []
      rewardPics = []
      for pullnum in range(0, pullCount):
        rewardPic = ""
        #Add pity to counter
        if(bannerID == 1):
          Gacha1PityU += 1
        if(bannerID == 3):
          Gacha3PityR += 1
          Gacha3PitySR +=1
        #Check pity rewards
        if(bannerID == 1 and Gacha1PityU > Gacha1PityULim): #Banner type 1, U pity
          CharID = random.choice(UCharacters)
          addCharacterToHarem(UID, CharID, 1, cursor)
          rarityID = 1
          Gacha1PityU = 0
        elif(bannerID == 3 and Gacha3PityR > Gacha3PityRLim): #Banner type 3, R pity
          CharID = random.choice(RCharacters)
          addCharacterToHarem(UID, CharID, 1, cursor)
          rarityID = 2
          Gacha3PityR = 0
        elif(bannerID == 3 and Gacha3PitySR > Gacha3PitySRLim): #Banner type 3, SR pity
          CharID = random.choice(SRCharacters)
          addCharacterToHarem(UID, CharID, 1, cursor)
          rarityID = 3
          Gacha3PitySR = 0
        else: #No pity for you
          seed = random.uniform(0, 100)
          CharID = 0
          rewardShort = "NOSHORT" #Single emote/letter for the "progress bar" or whatever it is called
          rewardLong = "NOFULL" #String, without item slot before it, shown in rewards gotten
          if(seed > CRewardLim):
            reward = random.choice(CommonRewards)
            ItemCount = reward[4]
            if(ItemCount != 0):
              addItemToInventory(UID, reward[1], reward[4], cursor)
            Carrots += reward[2]
            Cheese += reward[3]
          elif(seed > URewardLim):
            reward = random.choice(UncommonRewards)
            ItemCount = reward[4]
            if(ItemCount != 0):
              addItemToInventory(UID, reward[1], reward[4], cursor)
            Carrots += reward[2]
            Cheese += reward[3]
          elif(seed > UCharLim):
            CharID = random.choice(UCharacters)
            addCharacterToHarem(UID, CharID, 1, cursor)
            rarityID = 1
            if(bannerID == 1): #Reset pity counter
              Gacha1PityU = 0
          elif(seed > RRewardLim):
            temp = True #RRewards don't exist... yet
          elif(seed > RCharLim):
            CharID = random.choice(RCharacters)
            addCharacterToHarem(UID, CharID, 1, cursor)
            rarityID = 2
            if(bannerID == 3): #Reset pity counter
              Gacha3PityR = 0
          elif(seed > SRCharLim):
            CharID = random.choice(SRCharacters)
            addCharacterToHarem(UID, CharID, 1, cursor)
            rarityID = 3
            if(bannerID == 3): #Reset pity counter
              Gacha3PitySR = 0
          elif(seed > URCharLim):
            CharID = random.choice(URCharacters)
            addCharacterToHarem(UID, CharID, 1, cursor)
            rarityID = 4
          elif(seed > LCharLim):
            CharID = random.choice(LCharacters)
            addCharacterToHarem(UID, CharID, 1, cursor)
            rarityID = 5
          else:
            raise Exception("Hit undefined reward")

        if(CharID == 0): #You got a reward (not character), build reward sentences
          if(ItemCount != 0):
            rewardShort = getItemEmoteFromID(reward[1]) #Reward[1] is the ItemID
            rewardLong = "You got " + str(reward[4]) + " " + rewardShort
            if(reward[2] != 0 and reward[3] != 0):
              rewardLong += ", " + str(reward[2]) + " 🥕 and " + str(reward[3]) + " 🧀"
            elif(reward[2] != 0):
              rewardLong += " and " + str(reward[2]) + " 🥕"
            elif(reward[3] != 0):
              rewardLong += " and " + str(reward[3]) + " 🧀"
          elif(reward[2] != 0 or reward[3] != 0): #Only cheese and/or carrots
            if(reward[3] != 0):
              rewardShort = " 🧀"
              rewardLong = "You got " + str(reward[3]) + " 🧀"
              if(reward[2] != 0):
                rewardLong += " and " + str(reward[2]) + " 🥕"
            else:
              rewardShort = " 🥕"
              rewardLong == "You got " + str(reward[2]) + " 🥕"
          
        else:  
          rewardShort = getRarityEmotes(rarityID)
          querycharmetadata = '''SELECT Name, PictureLink
          FROM Characters
          WHERE
            CharID =''' + str(CharID)
          cursor.execute(querycharmetadata)
          cursorout = cursor.fetchall()
          
          rewardLong = (cursorout[0])[0] + " joined your harem"
          rewardPic = (cursorout[0])[1]
        rewardShorts.append(str(rewardShort)) #Add generated rewards to array
        rewardLongs.append(rewardLong) 
        rewardPics.append(rewardPic)
      
      querysavebal = '''UPDATE Users
      SET
        Carrots = ''' + str(Carrots) + ''',
        Cheese = ''' + str(Cheese) + ''',
        Gacha1PityU = ''' + str(Gacha1PityU) + ''', 
        Gacha3PityR = ''' + str(Gacha3PityR) + ''', 
        Gacha3PitySR = ''' + str(Gacha3PitySR) + '''
      WHERE
        UID = ''' + str(UID)
      cursor.execute(querysavebal)
      mydb.commit()
      mydb.close
      pic = ""
      for pullnum in range(1, (pullCount + 1)): #Need to always show something.
        progbar = ""
        for x in range(0, pullnum): #Fill full slots
          progbar += "["
          progbar += rewardShorts[x]
          progbar += "]"
        for y in range(pullnum, pullCount): #Fill slots with emptyness
          progbar += "["
          progbar += blankEmote
          progbar += "]"
        description = progbar
        for x in range(0, pullnum): #Add the longer parts
          description += """
          ["""
          description += rewardShorts[x]
          description += "] "
          description += rewardLongs[x]
        if(rewardPics[pullnum] != 0):
          pic = rewardPics[pullnum]
        embedVar = discord.Embed(title=title, description=description, color=discord.Colour.red())
        if(pic != ""):
          embedVar.set_image(url=pic)
        await message.edit(embed = embedVar)
        await asyncio.sleep(2)
  await message.edit(embed = embedVar)
      

@bot.command(aliases=['start', "Start", "MakeProfile", "Makeprofile", "makeprofile" ])
async def makeProfile(ctx: commands.Context):
  #First, get whether the user already has a profile
  UIDstr = str(ctx.message.author.id) #Get UID
  mydb = mydbconnect()
  cursor = mydb.cursor()
  cursor.execute(
    "SELECT UID, COUNT(*) FROM Users WHERE UID = %s GROUP BY UID",
     (UIDstr,)
  )
  results = cursor.fetchall() #Seems to be necessary to be sure to fetch everything
  if (cursor.rowcount != 0):
    mydb.close
    embedVar = discord.Embed(title="You already have a profile!", color=discord.Colour.dark_grey())
    embedVar.set_footer(text="use gumi profile to view your profile")
    await ctx.channel.send(embed=embedVar)
  
  else: #If user doesn't have a profile yet
    mydb.close
    embedVarOrgChan = discord.Embed(title='''Check your DM's to start''', description='''If you haven't received a DM, you have to allow users from this server to send you DM's. Click on this server with the right mouse button, go to Privacy Settings and allow DM's from server members. If you are on mobile, long press the server, select More Options, and toggle to allow DM's from server members.''',  color=discord.Colour(GumiYellow))
    embedVar = discord.Embed(title='''Hey hey! You wanna make a profile?''', description='''First of all, there are a few rules I gotta tell you.
    > You are not allowed to use alts to gain any advantage over other users
    > You are not allowed to use bots or scripts for this bot (this breaks the Discord TOS as well, by the way)
    > You are not allowed to (overly) abuse exploits if they give you an advantage over other users
    
    If you break any of these rules, you may get your account blocked or wiped.
    ''',  color=discord.Colour(GumiYellow))
    embedVar.add_field(name="Privacy Policy", value="The only personally identifyable information I collect is your Discord ID. For more information, [go here to read the full privacy policy](https://sites.google.com/view/gumibot/privacy-policy).", inline=False)
    embedVar.add_field(name="Questions?", value="If you have any questions, ask them in the [support server](https://discord.gg/DHD3S2B8DQ).", inline=False)
    embedVar.set_footer(text='Press "I accept" under here if you accept the rules and the Privacy Policy to create your profile')
    global CTXglobal
    CTXglobal = ctx
    await ctx.author.send(embed = embedVar, view = MakeProfile())
    await ctx.send(embed = embedVarOrgChan)

@bot.command(aliases=["Restart", "reboot"]) #Restart bot, admin only
async def restart(ctx):
  UID = ctx.message.author.id
  if (str(UID) == str(ADMINID)):
    embedVar = discord.Embed(title='Restarting...', color=discord.Colour(GumiYellow))
    await ctx.send(embed = embedVar)
    os.system("python3.8 gumi.py")
    print("Restart initiated")
    exit()
  else:
    await ctx.send(embed = BotAdminOnlyCommand)
    
@bot.command(aliases=["Exit"]) #Exit bot, admin only
async def exit(ctx):
  UID = ctx.message.author.id
  if (str(UID) == str(ADMINID)):
    embedVar = discord.Embed(title='Exiting...', color=discord.Colour(GumiYellow))
    await ctx.send(embed = embedVar)
    print("Exited due to command")
    exit()
  else:
    await ctx.send(embed = BotAdminOnlyCommand)

@bot.command(aliases=['ping', "Ping"])
async def pong(ctx):
  embedVar = discord.Embed(title='You really expect me to say "Pong!" back? Ugh, fine. Pong!', color=ctx.author.color)
  await ctx.send(embed = embedVar)

@bot.command
async def shop(ctx):
  embedVar = discord.Embed(title='A shop?', description = "Well, there isn't a shop as of now. You could get _gumi_ to show you the _banners_, and then pull instead. Maybe I'll open a shop later on, ara ara~~" ,  color=discord.Colour(MiharuBlue))
  await ctx.send(embed = embedVar)


@bot.command(aliases=['Profile', 'p'], brief = "Shows profile" ,description='''Shows the profile of the user you mentioned, or if you didn't mention anyone, your own profile''') 
async def profile(ctx, member: discord.Member=None):
    self = False #Get user pinged
    if member is None:
      member = ctx.message.author
      self = True
    UID = member.id
    UNAME = member.name

    title = UNAME + "'s profile"
    UIDstr = str(UID) #Get string form of UserID to append it
    query = '''SELECT Carrots, Cheese, ProfileCreated, CurrentSelectedCharacter
    FROM Users
    WHERE UID = ''' + UIDstr
    mydb = mydbconnect()
    cursor = mydb.cursor()
    cursor.execute(query) #Fetch user data from database
    cursorout = cursor.fetchall()

    try:
      Carrots = (cursorout[0])[0]
      Cheese = (cursorout[0])[1]
      ProfileCreated = str((cursorout[0])[2])
      CurrentCharID = (cursorout[0])[3]
      CurrentCharName = getCharacterNameFromID(CurrentCharID)
      descr = "Character: "  + CurrentCharName
      embedVar = discord.Embed(title=title, description = descr, color=ctx.author.color)
      embedVar.add_field(name="Carrots", value=Carrots, inline=True)
      embedVar.add_field(name="Cheese", value=Cheese, inline=True)
      embedVar.set_footer(text=("Account created on "+ ProfileCreated))
    except: #If nothing found
      if(self == True):
        embedVar = discord.Embed(title="You don't have an profile yet!", color=discord.Colour.red())
        embedVar.set_footer(text="You can make a profile using gumi start")
      else:
        embedVar = discord.Embed(title="This user doesn't have a profile yet", color=discord.Colour.dark_grey())
        embedVar.set_footer(text="They can make a profile using gumi start")     
    mydb.close 
    await ctx.channel.send(embed=embedVar) #Send message

@bot.command(aliases=['charlist', 'Charlist', 'chl', 'haram', 'Harem', 'Haram'], brief = "Shows list of owned characters" ,description='''Shows list of owned characters of the user you mentioned, or if you didn't mention anyone, your own''') 
async def harem(ctx, member: discord.Member=None):
    self = False #Get user pinged
    if member is None:
      member = ctx.message.author
      self = True
    UID = member.id
    UNAME = member.name

    if(hasUserProfile == False and self == True): #User himself has no profile?
      embedVar = discord.Embed(title="You don't have an profile yet!", color=discord.Colour.red())
      embedVar.set_footer(text="You can make a profile using gumi start")
    elif(hasUserProfile == False): #Other user pinged, has no profile
      embedVar = discord.Embed(title="This user doesn't have a profile yet", color=discord.Colour.dark_grey())
      embedVar.set_footer(text="They can make a profile using gumi start")
    else:
      mydb = mydbconnect()
      cursor = mydb.cursor()
      title = UNAME + "'s characters"
      UIDstr = str(UID) #Get string form of UserID to append it
      query = '''SELECT CharID, Amount
      FROM CharacterOwnership
      WHERE UID = ''' + UIDstr
      cursor.execute(query) #Fetch user data from database
      cursorout = cursor.fetchall()
      charcount = len(cursorout)
      selectedChar = getSelectedCharID(UID)
      if(charcount == 0):
        embedVar = discord.Embed(title="No characters? O-O", color=ctx.author.color)
      
      else:
        description = "" #Has all displayed characters
        for x in range (0, charcount):
          CurrentCharID = (cursorout[x])[0]
          CurrentCharName = getCharacterNameFromID(CurrentCharID)
          if((cursorout[x])[1] != 0):
            if(selectedChar == CurrentCharID):
              selectedCharSelector = "**"
            else:
              selectedCharSelector = ""
            description += selectedCharSelector + str(CurrentCharID) + " | " + str((cursorout[x])[1]) +  "x | " + CurrentCharName + selectedCharSelector +"""
            """ #Build a line of description
        if (description == ""):
          description = "No characters? O-O"
        embedVar = discord.Embed(title=title, description = description, color=ctx.author.color)
        mydb.close()
    await ctx.channel.send(embed=embedVar) #Send message

@bot.command(aliases=['lookup', 'Lookup', 'find', 'Find', 'lookupCharacter', "lookupcharacter", "Lookupcharacter"], brief = "Find character by name or ID") 
async def LookupCharacter(ctx, toBeSearched=None):
    if (toBeSearched==None):
      embedVar = discord.Embed(title="Enter a name or a character ID to look them up", color=discord.Colour.dark_grey())
    else:

      try:
        int(toBeSearched)
        query = '''SELECT CharID, Name, Description, PictureLink, Rarity, STR, WIS, AGL, CHR, CON, LCK, AuthorFootnote
        FROM Characters
        WHERE CharID =''' + str(toBeSearched) + ' AND LookUppable = True'
        
      except:
        query = '''SELECT CharID, Name, Description, PictureLink, Rarity, STR, WIS, AGL, CHR, CON, LCK, AuthorFootnote
        FROM Characters
        WHERE Name LIKE ''' + sqlstr( "%" + str(toBeSearched) + "%") + ' AND LookUppable = True'
        
      mydb = mydbconnect()
      cursor = mydb.cursor()
      cursor.execute(query) #Fetch user data from database
      cursorout = cursor.fetchall()
      mydb.close()
      if(len(cursorout) == 0):
        embedVar = discord.Embed(title="No one found with that name or ID", color=discord.Colour.light_gray())
      else:
        CharID = (cursorout[0])[0]
        Name = (cursorout[0])[1]
        Description = (cursorout[0])[2]
        PictureLink = (cursorout[0])[3]
        Rarity = (cursorout[0])[4]
        STR = (cursorout[0])[5]
        WIS = (cursorout[0])[6]
        AGL = (cursorout[0])[7]
        CHR = (cursorout[0])[8]
        CON = (cursorout[0])[9]
        LCK = (cursorout[0])[10]
        AuthorFootnote = (cursorout[0])[11]
        rarityName = getRarityName(Rarity)
        rarityEmoteString = getRarityEmotes(Rarity)
        title = Name
        descEmbed = str(CharID) + " | " + rarityEmoteString + " " + rarityName + """
        """
        descEmbed += Description 
        embedVar = discord.Embed(title=title, description = descEmbed, color=ctx.author.color)
        embedVar.add_field(name="STR", value=str(STR), inline=True)
        embedVar.add_field(name="INT", value=str(WIS), inline=True) #Wis == Int
        embedVar.add_field(name="AGL", value=str(AGL), inline=True)
        embedVar.add_field(name="CHR", value=str(CHR), inline=True)
        embedVar.add_field(name="CON", value=str(CON), inline=True)
        embedVar.add_field(name="LCK", value=str(LCK), inline=True)
        
        if(PictureLink != ""): #If there is a picture link, embed it
          embedVar.set_image(url=PictureLink)
        if(AuthorFootnote != ""): #If there is a footer, embed it
          embedVar.set_footer(text=AuthorFootnote)
    await ctx.channel.send(embed=embedVar)

@bot.command(brief = "Get help" , aliases=['Help']) 
async def help(ctx, toBeSearched=None):
    mydb = mydbconnect()
    cursor = mydb.cursor()
    if (toBeSearched==None): #Regular help command, multiple embeds
      embedVar = discord.Embed(title="You received a DM with help for you!", description="Didn't receive a DM? You have to allow users from this server to send you DM's. Click on this server with the right mouse button, go to Privacy Settings and allow DM's from server members. If you are on mobile, long press the server, select More Options, and toggle to allow DM's from server members. ", color=discord.Colour.dark_grey())
      query = '''SELECT Name, Category, ShortDescription
      FROM CommandList'''
      cursor.execute(query) #Fetch user data from database
      cursorout = cursor.fetchall()
      dmbedvar1 = discord.Embed(title="HELP", description="To get more info on a certain command, type _gumi help command_. You can also DM me these commands~~", color=ctx.author.color)
      AdminCommands = ""
      ProfileCommands = ""
      GachaCommands = ""
      GatheringCommands = ""
      MetaCommands = ""
      for x in range(0, len(cursorout)): #Put commands and short descriptions in right category
        Name = (cursorout[x])[0]
        ShortDescription = (cursorout[x])[2]
        Category = (cursorout[x])[1]
        if(Category == "Admin"): 
          AdminCommands += "**" + Name + ":** " + ShortDescription + """
          """
        if(Category == "Profile"):
          ProfileCommands += "**" + Name + ":** " + ShortDescription + """
          """
        if(Category == "Gacha"):
          GachaCommands += "**" + Name + ":** " + ShortDescription + """
          """
        if(Category == "Gathering"):
          GatheringCommands += "**" + Name + ":** " + ShortDescription + """
          """
        if(Category == "Meta"):
          MetaCommands += "**" + Name + ":** " + ShortDescription + """
          """
      mydb.close()
      dmbedvar2 = discord.Embed(title="Profile", description=ProfileCommands, color=ctx.author.color)
      dmbedvar3 = discord.Embed(title="Gacha", description=GachaCommands, color=ctx.author.color)
      dmbedvar4 = discord.Embed(title="Gathering", description=GatheringCommands, color=ctx.author.color)
      dmbedvar5 = discord.Embed(title="Meta", description=MetaCommands, color=ctx.author.color)
      await ctx.author.send(embed = dmbedvar1)
      await ctx.author.send(embed = dmbedvar2)
      await ctx.author.send(embed = dmbedvar3)
      await ctx.author.send(embed = dmbedvar4)
      await ctx.author.send(embed = dmbedvar5)
      await ctx.channel.send(embed=embedVar) #Note that command list in DMs

    else:                    #Search something in the help command
      query = '''SELECT Name, Category, ShortDescription, LongDescription, Alias1, Alias2, Alias3, Alias4
      FROM CommandList
      WHERE Name LIKE ''' + sqlstr( "%" + str(toBeSearched) + "%")   #Implement: search on aliases, perhaps
      cursor.execute(query) #Fetch user data from database
      cursorout = cursor.fetchall()
      mydb.close()
      if(len(cursorout) == 0):
        embedVar = discord.Embed(title="No command or category found with that name", color=discord.Colour.light_gray())
      else:
        aliases = ""
        Name = (cursorout[0])[0]
        Category = (cursorout[0])[1]
        ShortDescription = (cursorout[0])[2]
        LongDescription = (cursorout[0])[3]
        Alias1 = (cursorout[0])[4]
        Alias2 = (cursorout[0])[5]
        Alias3 = (cursorout[0])[6]
        Alias4 = (cursorout[0])[7]
        title = Name
        if(Alias1 != None): #Add part showing all aliases
          aliases = "**Aliases:** " + Alias1
          if(Alias2 != None):
            aliases += ", " + Alias2
          if(Alias3 != None):
            aliases += ", " + Alias3
          if(Alias4 != None):
            aliases += ", " + Alias4
          aliases += '''
          ''' #Add next line
        descEmbed = "**Category:** " + str(Category) + '''
        ''' + aliases + LongDescription
        embedVar = discord.Embed(title=title, description = descEmbed, color=ctx.author.color)
        #embedVar.add_field(name="STR", value=str(STR), inline=True)
        await ctx.channel.send(embed=embedVar) #For now, specific help in chat where called
    


@bot.command(aliases=['Inventory', 'inv', 'INV'], brief = "Shows inventory" ,description='''Shows the inventory of the user you mentioned, or if you didn't mention anyone, your own''') 
async def inventory(ctx, member: discord.Member=None, pagenumber=1):
    self = False #Get user pinged
    if member is None:
      member = ctx.message.author
      self = True
    UID = member.id
    UNAME = member.name
    PAGELEN = 15 #Amount of items per page

    if(hasUserProfile == False and self == True): #User himself has no profile?
      embedVar = discord.Embed(title="You don't have an profile yet!", color=discord.Colour.red())
      embedVar.set_footer(text="You can make a profile using gumi start")
    elif(hasUserProfile == False): #Other user pinged, has no profile
      embedVar = discord.Embed(title="This user doesn't have a profile yet", color=discord.Colour.dark_grey())
      embedVar.set_footer(text="They can make a profile using gumi start")
    else:
      mydb = mydbconnect()
      cursor = mydb.cursor()
      title = UNAME + "'s inventory"
      UIDstr = str(UID) #Get string form of UserID to append it
      query = '''SELECT ItemID, Amount
      FROM ItemOwnership
      WHERE UID = ''' + UIDstr
      cursor.execute(query) #Fetch user data from database
      cursorout = cursor.fetchall()
      itemcount = len(cursorout)
      if(itemcount == 0):
        embedVar = discord.Embed(title="Seems this inventory is empty... as of now", color=ctx.author.color)
      
      #elif(itemcount <= PAGELEN): #Everything fits on a single page. It always does. Just remove empty inventory slots.
      else:
        description = "" #Has all displayed items
        for x in range (0, itemcount):
          CurrentItemID = (cursorout[x])[0]
          CurrentItemName = getItemNameFromID(CurrentItemID)
          if((cursorout[x])[1] != 0):
            description += CurrentItemID + " | " + str((cursorout[x])[1]) + "x | " + CurrentItemName + """
            """ #Build a line of description
        if (description == ""):
          description = "Seems this inventory is empty... as of now"
        embedVar = discord.Embed(title=title, description = description, color=ctx.author.color)

      mydb.close()
      #Make arrow keys. Or not
      '''
      else: #Not everything fits on a single page.
        if(isinstance(pagenumber, int)):
          startitemnum = (pagenumber - 1) * 15 
        else:
          startitemnum = 0
        if(startitemnum > itemcount):
          startitemnum = 0
        enditemnum = startitemnum + 14 #or 15? hmm
        if(enditemnum > itemcount):
          enditemnum = itemcount
        for x in range (startitemnum, enditemnum):
          CurrentItemID = (cursorout[x])[0]
          CurrentItemName = getItemNameFromID(CurrentItemID)
          description += CurrentItemID + " | " + str((cursorout[x])[1]) + "x | " + CurrentItemName + """
          """ #Build a line of description
        
        embedVar = discord.Embed(title=title, description = description, color=ctx.author.color)
        '''
    await ctx.channel.send(embed=embedVar) #Send message


    '''
    try:
      Carrots = (cursorout[0])[0]
      Cheese = (cursorout[0])[1]
      ProfileCreated = str((cursorout[0])[2])
      embedVar = discord.Embed(title=title, color=ctx.author.color)
      embedVar.add_field(name="Carrots", value=Carrots, inline=True)
      embedVar.add_field(name="Cheese", value=Cheese, inline=True)
      embedVar.set_footer(text=("Account created on "+ ProfileCreated))
    except: #If nothing found
      if(self == True):
        embedVar = discord.Embed(title="You don't have an profile yet!", color=discord.Colour.red())
        embedVar.set_footer(text="You can make a profile using gumi start")
      else:
        embedVar = discord.Embed(title="This user doesn't have a profile yet", color=discord.Colour.dark_grey())
        embedVar.set_footer(text="They can make a profile using gumi start")
    await ctx.channel.send(embed=embedVar) #Send message
    '''

@bot.command(aliases=["Gather"] , description = "Gather carrots... Or at least, that is the plan")
async def gather(ctx):
  UID = ctx.message.author.id
  if(hasUserProfile(UID) == False):
    embedVar = discord.Embed(title="You don't have an profile yet!", color=discord.Colour.red())
    embedVar.set_footer(text="You can make a profile using gumi start")
  else:
    query = '''SELECT LastDayGathered, GatheredToday, CurrentSelectedCharacter, GatheredTotal, LastTimeGathered, Carrots , Cheese, TimesBeenInJail
    FROM Users
    WHERE UID = ''' + str(UID)
    mydb = mydbconnect()
    cursor = mydb.cursor()
    cursor.execute(query) #Fetch user data from database
    cursorout = cursor.fetchall()
    LastDayGathered = (cursorout[0])[0]
    GatheredToday = (cursorout[0])[1]
    CurrentSelectedCharacter = (cursorout[0])[2]
    GatheredTotal = (cursorout[0])[3]
    LastTimeGathered = (cursorout[0])[4]
    AmountCarrots = (cursorout[0])[5]
    AmountCheese = (cursorout[0])[6]
    TimesBeenInJail = (cursorout[0])[7]
    datetoday = datetime.date(datetime.utcnow())
    datetodayforsql = datetime.utcnow().strftime("%Y%m%d") #This one is needed if date needs to be saved in SQL 
    GatherRandomReturnCoef = random.uniform(0.5, 1.6)

    if(GatheredTotal == 0): #First time gathering
      embedVar = discord.Embed(title='Welcome to the carrot fields, humu humu', description = '''Here, we collect carrots. Okay, sometimes also a bit of cheese and carrot seeds. Every 10 minutes you can come to collect a few.
      You asking me what you do with carrots? Well, as a rabbit I would recommend you to eat them. But you could look at the _gumi banner_ to have a look what pulls you can do to collect items and maybe even characters!
      Sometimes you stumble upon some carrot seeds. You can plant them in the _gumi farm_ 
      Good luck comrade, and you know what? I'll give you a sackfull of carrots and two pieces of cheese as a starter gift!
      ''' , color=discord.Colour(GumiYellow))
      embedVar.set_footer(text="You got 42 🥕 and 2 🧀")
      queryFirstGather = '''
      UPDATE Users
      SET
        Carrots = ''' + str(AmountCarrots + 42) + ''',
        Cheese = ''' + str(AmountCheese + 2) + ''',
        LastTimeGathered = ''' + str(getTimestamp()) + ''',
        GatheredToday = 1,
        GatheredTotal = 1,
        LastDayGathered = ''' + str(datetodayforsql)+ '''
      WHERE
        UID = ''' + str(UID)
      cursor.execute(queryFirstGather)
      mydb.commit()
    elif(LastTimeGathered > getTimestamp()): #Jail
      jailtimeleft = (LastTimeGathered - getTimestamp())
      jaildescription = "You shall be let free after " + makeLegibleTime(jailtimeleft)
      embedVar = discord.Embed(title='You are currently in jail', description = jaildescription ,  color=discord.Colour.light_gray())
    elif(LastTimeGathered > (getTimestamp() - 600)): #Gather timeout
      embedVar = discord.Embed(title='Hang on, comrade', description = "You may only gather once every 10 minutes", color=discord.Colour.light_grey())
    else: #Else, first get selected character data
      query2 = '''SELECT Rarity, STR, WIS, AGL, CHR, CON, LCK
      FROM Characters
      WHERE CharID = ''' + str(CurrentSelectedCharacter)
      cursor.execute(query2) #Fetch user data from database
      cursorout = cursor.fetchall()
      Rarity = (cursorout[0])[0]
      STR = (cursorout[0])[1]
      WIS = (cursorout[0])[2]
      AGL = (cursorout[0])[3]
      CHR = (cursorout[0])[4]
      CON = (cursorout[0])[5]
      LCK = (cursorout[0])[6]
      AmountSeedsDelta = 0
      AmountCheeseDelta = 0
      AmountCarrotsDelta = 0

      if(LastDayGathered < datetoday): #First time gatehring today
        event = random.randint(1, 100)
        if(event>95): #Miharu selected for welcome
          if(event == 99): #Regular loot
            description = "Gumi? She is... stuck in my basement for now. Do you also want to be in my basement? Just kidding~~ Oh yeah, you earned a salary from gathering carrots, Gumi told me. Here, take it!"
          else: #Regular loot
            description = "Seems like Gumi isn't here for now. The rabbit she is, I don't look at her for a second and she has already hopped away. Anyway, you helped her collect carrots? Here, take this as a reward for helping our cute Gumi-chan!"
          AmountCarrotsDelta = int(GatheredToday * GatherRandomReturnCoef) + 1
          embedVar = discord.Embed(title='Ara ara~~', description = description ,  color=discord.Colour(MiharuBlue))
        elif(event>88):#Axl selected for welcome
          if(event == 90): #Nothing
            description = "Yes, I nuked all of Gumi's carrots, so what? Does that matter or anything? Nukes are fun, aren't they? What, you were expecting some carrots? Get lost, mate."
          elif(event == 91): #Cheese
            description = "Yes, I nuked all of Gumi's carrots, so what? Does that matter or anything? Nukes are fun, aren't they? What, you were expecting some carrots? Ah well, if you really want something, I could give you some cheese from my place..."
            AmountCheeseDelta = (random.randint(1,2))
          else: #Regular
            description = "Why you want carrots, cheese is way better mate. Why do you even want those orange hard sticks? But if you insist, I could give you these here..."
            AmountCarrotsDelta = int(GatheredToday * GatherRandomReturnCoef) + 1
          embedVar = discord.Embed(title='Carrots?',description = description,  color=discord.Colour(AxlPink))
        else:
          if(event > 76): # Cheese
            descriptions = ("Axl brought me some cheese today. You want some as well?", "Axl tested the nukes on my carrot shed. I told him never to try that again, but he wouldn't listen. The dummy! At least I hopped into his storage shed and stole some of the cheese he had. Here, take some!")
            description = random.choice(descriptions)
            AmountCheeseDelta = (random.randint(1,3))
          elif(event > 74): #Carrot jackpot
            description = "Yesterday while searching the ideal carrot pulling place, I found a giant field... And it was full of carrots. Here, take this, enjoy and eat up!"
            AmountCarrotsDelta = 69
          elif(event > 72): #Nothing
            description = "My shed... It's empty again! Did that catboy Axl take all the carrots away? Time to catch him, and pull him by his tail. Also, sorry for today, can't really give you anything. Tomorrow you should get your carrots once again, so don't worry~~"
          else:
            descriptions = ("Hey there comrade! Good timing, I got your bonus o'carrots right here!",
            "You collected a lot of carrots yesterday, so take some of these for yourself!",
            "I saw Axl looking at my shed. I really hope it won't become one of his nuke testing locations.",
            "I still don't understand why we haven't been able to decide whether cheese or carrots are more tasty. But... I like them both! Maybe I don't have to choose at all?" ,
            "_Gumi hops toward you, with a big carrot in her mouth. She brought some carrots, and gave you your part. And after that, Gumi pushed a carrot into your mouth as well_",
            "Take these carrots, and after that hurry up. We have to collect even more!",
            "Did Miharu try to explain to you why foxgirls are the best type of girls? Sure, I can't deny they are cute. But you are a rabbit girl enjoyer, right? Prefect cute and smol tails, and the best ears on the planet!",
            "Remember the carrot seeds you find when you go out gathering? Don't forget to plant them somewhere, they will grow into tasty, juicy, orange carrots!")
            description = random.choice(descriptions)
            AmountCarrotsDelta = int(GatheredToday * GatherRandomReturnCoef) + 1
            if(AmountCarrotsDelta > 50): #Limit carrots at 50
              AmountCarrotsDelta = 50
            
          embedVar = discord.Embed(title='Hop, hop, hop',description = description,  color=discord.Colour(GumiYellow))
        if(AmountCarrotsDelta > 0): #Create footer
          footertext = "You got " + str(AmountCarrotsDelta) + "🥕"
        elif(AmountCheeseDelta > 0):
          footertext = "You got " + str(AmountCheeseDelta) + "🧀"
        AmountCarrots += AmountCarrotsDelta
        AmountCheese += AmountCheeseDelta
        embedVar.set_footer(text=footertext)

        QueryBack = """UPDATE Users
        SET
          Carrots = """ + str(AmountCarrots) + """,
          Cheese = """ + str(AmountCheese) + """,
          LastDayGathered = """ + sqlstr(datetodayforsql)+ """,
          GatheredToday = 1,
          GatheredTotal = """ + str(GatheredTotal + 1) + """,
          LastTimeGathered = """ + str(getTimestamp())+"""
        WHERE
          UID = """ + str(UID) +"""
        """
        cursor.execute(QueryBack)
        mydb.commit()
      
      elif(LastDayGathered == datetoday): #Already gathered today
        LastTimeGathered = getTimestamp()
        event = random.randint(1, 100)
        if(event > 95): #Jail, AGL
          Chance = ((GatherRandomReturnCoef * AGL * getRarityCoefeccient(Rarity) )/ 80)
          if(Chance < 1): #Put in jail
            LastTimeGathered += 1200 #20 mins
            TimesBeenInJail += 1
            description = "You tried to steal some carrots from the carrot fields of your neighbours. But your thievery has been seen, and you have been sent to jail for 20 minutes."
          else:
            AmountCarrotsDelta = int((Chance-1) * 20)
            description = "You couldn't find anymore carrots near your place, but you saw some at your neighbour. You were able to sneak inside and quickly steal a few carrots before getting seen."
        elif(event > 90): #Jail, Intellegence
          Chance = ((GatherRandomReturnCoef * WIS * getRarityCoefeccient(Rarity) )/ 80)
          if(Chance < 1): #Put in jail
            LastTimeGathered += 900 #15 mins 
            TimesBeenInJail += 1
            AmountCarrotsDelta = int(Chance * 20)
            description = "You saw a few carrots laying on a sus pile on an open place. Without thinking, your eyes started to glow and you ran to take the carrots. A net caught you though, but at least you have a generous pile of carrots now."
          else:
            description = "You saw a few carrots laying on a sus pile on an open place. Too suspicious, to be exact. Who would have left them over here? Is it a trap? Are it poisoned carrots? You walked away to find some less... risky carrots."

        elif(event > 75): #STR
          description = "Carrots. Brute force carrot pulling. Don't think, just pull. Pull as much as you can carry!"
          AmountCarrotsDelta = ((GatherRandomReturnCoef * STR * getRarityCoefeccient(Rarity) )/ 10)
        elif(event > 60): #WIS
          description = "Be smart and think. You don't have to get the carrots right now. You could also get the seeds to plant them, and get more carrots later then you can find now."
          AmountSeedsDelta = ((GatherRandomReturnCoef * WIS * getRarityCoefeccient(Rarity) )/ 8)
        elif(event > 45): #AGL
          description = "Carrot gathering is a sport. You need strength to pull the carrots out, you need a good eyesight to find the carrots. But you almost forgot the need for agility. The ability to take the carrots faster than the rabbits that hunt carrots even more competitevly than you."
          AmountCarrotsDelta = ((GatherRandomReturnCoef * AGL * getRarityCoefeccient(Rarity) )/ 10)
        elif(event > 30): #CHR
          description = "One doesn't gather alone all the time. Having good friends to gather together is good, gathering the food from your friends hands could even be better"
          Chance = ((GatherRandomReturnCoef * CHR * getRarityCoefeccient(Rarity) )/ 80)
          if(Chance > 1):
            AmountCheeseDelta = (int((Chance-1) * 4) + 1)
          else:
            AmountCarrotsDelta = (int(Chance * 11) + 1)
        elif(event > 15): #CON
          description = "A good constitution is also somehow important for gathering. Okay, I say somehow, but you won't find a lot if you get tired after pulling a single carrot. You can at least find some more, right?"
          AmountCarrotsDelta = ((GatherRandomReturnCoef * CON * getRarityCoefeccient(Rarity) )/ 10)
        else:             #LCK
          Chance = ((GatherRandomReturnCoef * LCK * getRarityCoefeccient(Rarity) )/ 80)
          if(Chance > 1):
            description = "Lucky you found cheese in the fields! Although...  Why was there cheese in the fields at all?"
            AmountCheeseDelta = (int((Chance-1) * 3) + 1)
          else:
            description = "The luck wasn't with you. You found nothing but a single carrot."
            AmountCarrotsDelta = 1

        AmountCarrotsDelta = int(AmountCarrotsDelta)
        AmountCheeseDelta = int(AmountCheeseDelta)
        AmountSeedsDelta = int(AmountSeedsDelta)
        AmountCarrots += AmountCarrotsDelta
        AmountCheese += AmountCheeseDelta

        if(AmountCarrotsDelta > 0): #Create footer
          footertext = "You got " + str(AmountCarrotsDelta) + "🥕"
        elif(AmountCheeseDelta > 0):
          footertext = "You got " + str(AmountCheeseDelta) + "🧀"
        elif(AmountSeedsDelta > 0):
          footertext = "You got " + str(AmountSeedsDelta) + "🌱"
          addItemToInventory(UID, "CSD" , AmountSeedsDelta, cursor) #Only needed for these types of seeds.
        else:
          footertext = "You did not receive anything"
        
        queryUsers = '''
        UPDATE Users
        SET
          Carrots = ''' + str(AmountCarrots) + ''',
          Cheese = ''' + str(AmountCheese) + ''',
          LastTimeGathered = ''' + str(LastTimeGathered) + ''',
          TimesBeenInJail = ''' + str(TimesBeenInJail) + ''',
          GatheredToday = ''' + str(GatheredToday + 1) + ''',
          GatheredTotal = ''' + str(GatheredTotal + 1) + '''
        WHERE
          UID = ''' + str(UID)
        cursor.execute(queryUsers)
        mydb.commit()
        embedVar = discord.Embed(title="You went out to gather~~", description = description, color=ctx.author.color)
        embedVar.set_footer(text=footertext)
    mydb.close()
  await ctx.send(embed = embedVar)

@bot.command(aliases=['Farm'] , description = "Grow carrots from your carrot seeds")
async def farm(ctx):
  UID = ctx.message.author.id
  ViewSet = False
  #view = FarmPlantButton(ctx)
  if(hasUserProfile(UID) == False):
    embedVar = discord.Embed(title="You don't have an profile yet!", color=discord.Colour.red())
    embedVar.set_footer(text="You can make a profile using gumi start")
  else:
    mydb = mydbconnect()
    cursor = mydb.cursor()
    query = '''SELECT FarmStartTimestamp, FarmStopTimestamp, AmountPlanted, CarrotFieldSize
    FROM Users
    WHERE UID = ''' + str(UID)
    cursor.execute(query) #Fetch user data from database
    cursorout = cursor.fetchall()
    FarmStartTimestamp = (cursorout[0])[0]
    FarmStopTimestamp = (cursorout[0])[1]
    AmountPlanted = (cursorout[0])[2]
    CarrotFieldSize = (cursorout[0])[3]
    if(FarmStartTimestamp == 0): #First time
      embedVar = discord.Embed(title="Welcome to the farm!", description = """The carrot seeds you find while gathering can be planted here. You wait a few hours, and you can harvest some juicy fresh carrots. How long exactly, you ask? _You never know._
      Allow me to give you a starter gift. Take this~~""", color=discord.Colour(GumiYellow))
      embedVar.set_footer(text="You got 5 🌱")
      queryFirstTime = """UPDATE Users
      SET
        FarmStartTimestamp = 1
      WHERE
        UID = """ + str(UID)
      cursor.execute(queryFirstTime)
      addItemToInventory(UID, "CSD", 5, cursor)
      mydb.commit()
    elif(getTimestamp() < FarmStopTimestamp): #Show loading bar
      barString = "["
      lengthLeftSeconds = (FarmStopTimestamp - getTimestamp()) #Amount of seconds still to wait
      lengthTotalSeconds = (FarmStopTimestamp - FarmStartTimestamp)
      lengthPassedSeconds = (lengthTotalSeconds - lengthLeftSeconds)
      if (lengthLeftSeconds < 0):
        raise Exception("Carrots already ready to harvest")
      carrotEmoteCount = int(((lengthPassedSeconds * 9) / lengthTotalSeconds)+ 1 )
      emptyEmoteCount = (10 - carrotEmoteCount)
      for x in range(carrotEmoteCount):
        barString += "🥕"
      for y in range(emptyEmoteCount):
        barString += blankEmote
      barString += "]"
      embedVar = discord.Embed(title="Your carrots are still growing", description = barString, color=ctx.author.color)
    elif(AmountPlanted > 0): #Collect grown carrots
      AmountCarrotsHarvested = int(AmountPlanted * random.uniform(0.8, 1.2))
      title = "You harvested " + str(AmountCarrotsHarvested) + "🥕"
      seedsLeft = getAmountItemOwned(UID, "CSD")
      if(seedsLeft == 0):
        description = "You don't have anymore seeds"
      else:
        description = "You still have " + str(seedsLeft) + "🌱"
        ViewSet = True
      queryBack = """UPDATE Users
      SET
        AmountPlanted = 0
      WHERE
        UID = """ + str(UID)
      cursor.execute(queryBack) # "Empty the fields"
      changeBalance(UID, AmountCarrotsHarvested, 0, cursor) #Add new carrots to balance
      mydb.commit
      embedVar = discord.Embed(title=title, description = description, color=ctx.author.color)
      embedVar.set_footer(text = ("In your field fit " + str(CarrotFieldSize) + "🌱. Use gumi farm again to plant them"))
    else: #No seeds planted at the given time
      seedsLeft = getAmountItemOwned(UID, "CSD")
      if(seedsLeft == 0):
        title = "You don't have any seeds to plant"
      else:
        
        stopTimestamp = (getTimestamp() + random.randint(10800, 21600)) #Farming takes between 3 and 6 hours
        
        seedsToPlant = seedsLeft
        if (seedsLeft > CarrotFieldSize):
          seedsToPlant = CarrotFieldSize
        queryplant = """UPDATE Users SET FarmStartTimestamp = """ + str(getTimestamp()) + """, FarmStopTimestamp = """ + str(stopTimestamp) + """, AmountPlanted = """ + str(seedsToPlant) + """ WHERE UID = """ + str(UID)
        seedsInvDelta = seedsToPlant * -1
        addItemToInventory(UID, "CSD", seedsInvDelta, cursor)
        cursor.execute(queryplant)
        mydb.commit()
        title = "You have " + str(seedsLeft) + " 🌱 ready to plant. You planted " + str(seedsToPlant) + " of them"
        #ViewSet = True
        
      embedVar = discord.Embed(title=title, color=ctx.author.color)
      embedVar.set_footer(text = ("In your field fit " + str(CarrotFieldSize) + " 🌱"))
    mydb.close
    await ctx.send(embed = embedVar)

    #Buttons: disabled for now.
  
''' #Put in the farm command
@bot.command(aliases=["Plant"] , description = "Plant carrots into the farm")
async def plant(ctx):
  UID = ctx.message.author.id
  if(hasUserProfile(UID) == False):
    embedVar = discord.Embed(title="You don't have an profile yet!", color=discord.Colour.red())
    embedVar.set_footer(text="You can make a profile using gumi start")
  else:
    seedsLeft = getAmountItemOwned(UID, "CSD")
    mydb = mydbconnect()
    cursor = mydb.cursor()
    querycheck = """SELECT AmountPlanted, CarrotFieldSize
    FROM Users
    WHERE UID = """ + str(UID)
    cursor.execute(querycheck) #Fetch user data from database
    cursorout = cursor.fetchall()
    
    AmountPlanted = (cursorout[0])[0]
    CarrotFieldSize = (cursorout[0])[1]
    if(AmountPlanted > 0):
      title = "You already have carrots planted. If you wanna try to harvest them, type _gumi farm_"
    elif(seedsLeft == 0):
      title = "You don't have any seeds to plant!"
    else:
      if (seedsLeft > 20): #Should not be hard coded, but...
        seedsLeft = 20
      stopTimestamp = (getTimestamp() + random.randint(10800, 21600)) #Farming takes between 3 and 6 hours
      queryplant = """UPDATE Users SET FarmStartTimestamp = """ + str(getTimestamp()) + """, FarmStopTimestamp = """ + str(stopTimestamp) + """, AmountPlanted = """ + str(seedsLeft) + """ WHERE UID = """ + str(UID)
      mydb2 = mydbconnect()
      cursor2 = mydb2.cursor()
      addItemToInventory(UID, "CSD", (seedsLeft * (-1)), cursor)
      mydb.commit
      print(queryplant)
      cursor2.execute(queryplant)
      mydb2.commit
      mydb2.close
      title = "You planted " + str(seedsLeft) + " seeds"
    mydb.close()
    embedVar = discord.Embed(title=title, color=ctx.author.color)
  await ctx.send(embed = embedVar)
'''

'''
  if(ViewSet): #If a button has to appear. ViewSet is a bool, no comparison needed.
    message = await ctx.send(embed = embedVar, view = view)
    print("GotHere.3")
    await view.wait()
    print("GotHere.4")
    nUID = view.value
    if (nUID == UID): #Edit message and plant carrots. No check whether user has profile needed
      seedsLeft = getAmountItemOwned(nUID, "CSD")
      querycheck = """SELECT AmountPlanted, CarrotFieldSize
      FROM Users
      WHERE UID = """ + str(nUID)
      cursor.execute(querycheck) #Fetch user data from database
      cursorout = cursor.fetchall()
      AmountPlanted = (cursorout[0])[0]
      CarrotFieldSize = (cursorout[0])[1]
      if(AmountPlanted > 0):
        title = "You already have carrots planted. If you wanna try to harvest them, type _gumi farm_"
      elif(seedsLeft == 0):
        title = "You don't have any seeds to plant!"
      else:
        if (seedsLeft > 20): #Should not be hard coded, but...
          seedsLeft = 20
        stopTimestamp = (getTimestamp() + random.randint(10800, 21600)) #Farming takes between 3 and 6 hours
        queryplant = """UPDATE Users
        SET
          FarmStartTimestamp = """ + str(getTimestamp()) + """,
          FarmStopTimestamp = """ + str(stopTimestamp) + """,
          AmountPlanted = """ + str(seedsLeft) + """
        WHERE
          UID = """ + str(nUID)
        print(queryplant)
        addItemToInventory(nUID, "CSD", (seedsLeft * (-1)), cursor)
        cursor.execute(queryplant)
        mydb.commit
        title = "You planted " + str(seedsLeft) + " seeds"
      embedVar = discord.Embed(title=title, color=ctx.author.color)
      await message.edit(embed = embedVar, view=None) #Removes button


  else: #Else, no button shall appear
    await ctx.send(embed = embedVar)
'''

'''
@bot.command(aliases=['gather', "Gather"] , description = "Base profile-required command")
async def base(ctx):
  UID = ctx.message.author.id
  if(hasUserProfile(UID) == False):
    embedVar = discord.Embed(title="You don't have an profile yet!", color=discord.Colour.red())
    embedVar.set_footer(text="You can make a profile using gumi start")
  else:
    embedVar = discord.Embed(title="Some test", color=discord.Colour.red())
  await ctx.send(embed = embedVar)
'''

#ErrorHandler, to be implemented later
'''
class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        Parameters
        ------------
        ctx: commands.Context
            The context used for command invocation.
        error: commands.CommandError
            The Exception raised.
        """

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
                await ctx.send('I could not find that member. Please try again.')

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignyaring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
'''

print("Bot online!")
bot.run(TOKEN)
