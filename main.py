import discord
import asyncio
import sys, os, re, datetime, pytz, difflib, random, json
from math import floor
import koduck, yadon
import settings
from collections import OrderedDict

emojis = None
types = None
numberemojis = ["❌", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣"]
typecolor = {"Normal":0xa8a878, "Fire":0xf08030, "Water":0x6890f0, "Grass":0x78c850, "Electric":0xf8d030, "Ice":0x98d8d8, "Fighting":0xc03028, "Poison":0xa040a0, "Ground":0xe0c068, "Flying":0xa890f0, "Psychic":0xf85888, "Bug":0xa8b820, "Rock":0xb8a038, "Ghost":0x705898, "Dragon":0x7038f8, "Dark":0x705848, "Steel":0xb8b8d0, "Fairy":0xee99ac}

#Background task is run every set interval while bot is running (by default every 10 seconds)
async def backgroundtask():
    #can't put this in setup() because it runs before discord client is set up
    global emojis
    if emojis is None:
        emojis = {}
        for server in koduck.client.guilds:
            if server.name.startswith("Pokemon Shuffle Icons") or server.id == settings.mainserverid:
                for emoji in server.emojis:
                    emojis[emoji.name.lower()] = "<:{}:{}>".format(emoji.name, emoji.id)
settings.backgroundtask = backgroundtask

##################
# BASIC COMMANDS #
##################
#Be careful not to leave out this command or else a restart might be needed for any updates to commands
async def updatecommands(context, *args, **kwargs):
    tableitems = yadon.ReadTable(settings.commandstablename).items()
    if tableitems is not None:
        koduck.clearcommands()
        for name, details in tableitems:
            try:
                koduck.addcommand(name, globals()[details[0]], details[1], int(details[2]))
            except (KeyError, IndexError, ValueError):
                pass

async def shutdown(context, *args, **kwargs):
    return await koduck.client.logout()

async def sendmessage(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_sendmessage_noparam)
    try:
        channelid = int(args[0])
    except ValueError:
        channelid = -1
    THEchannel = koduck.client.get_channel(channelid)
    THEmessagecontent = context["paramline"][context["paramline"].index(settings.paramdelim)+1:].strip()
    return await koduck.sendmessage(context["message"], sendchannel=THEchannel, sendcontent=THEmessagecontent, ignorecd=True)

async def changestatus(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.client.change_presence(activity=discord.Game(name=""))
    else:
        return await koduck.client.change_presence(activity=discord.Game(name=context["paramline"]))

async def updatesettings(context, *args, **kwargs):
    koduck.updatesettings()
    return

#note: discord server prevents any user, including bots, from changing usernames more than twice per hour
#bot name is updated in the background task, so it won't update immediately
async def updatesetting(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_noparam)
    variable = args[0]
    value = context["paramline"][context["paramline"].index(settings.paramdelim)+1:].strip()
    result = koduck.updatesetting(variable, value, koduck.getuserlevel(context["message"].author.id))
    if result is not None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_success.format(variable, result, value))
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_failed)

async def addsetting(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_updatesetting_noparam)
    variable = args[0]
    value = context["paramline"][context["paramline"].index(settings.paramdelim)+1:].strip()
    result = koduck.addsetting(variable, value, koduck.getuserlevel(context["message"].author.id))
    if result is not None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addsetting_success)
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addsetting_failed)

async def removesetting(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removesetting_noparam)
    result = koduck.removesetting(args[0], koduck.getuserlevel(context["message"].author.id))
    if result is not None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removesetting_success)
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removesetting_failed)

async def admin(context, *args, **kwargs):
    #need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].raw_mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)
    
    userid = context["message"].raw_mentions[0]
    userlevel = koduck.getuserlevel(userid)
    
    #already an admin
    if userlevel == 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addadmin_failed.format(settings.botname))
    else:
        koduck.updateuserlevel(userid, 2)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addadmin_success.format(userid, settings.botname))

async def unadmin(context, *args, **kwargs):
    #need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].raw_mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)
    
    userid = context["message"].raw_mentions[0]
    userlevel = koduck.getuserlevel(userid)
    
    #not an admin
    if userlevel < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeadmin_failed.format(settings.botname))
    else:
        koduck.updateuserlevel(userid, 1)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeadmin_success.format(userid, settings.botname))

#Searches through the past settings.purgesearchlimit number of messages in this channel and deletes given number of bot messages
async def purge(context, *args, **kwargs):
    try:
        limit = int(args[0])
    except (IndexError, ValueError):
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_purge_invalidparam)
    
    counter = 0
    async for message in context["message"].channel.history(limit=settings.purgesearchlimit):
        if counter >= limit:
            break
        if message.author.id == koduck.client.user.id:
            await message.delete()
            counter += 1

async def restrictuser(context, *args, **kwargs):
    #need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].raw_mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)
    
    userid = context["message"].raw_mentions[0]
    userlevel = koduck.getuserlevel(userid)
    
    #already restricted
    if userlevel == 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_restrict_failed)
    #don't restrict high level users
    elif userlevel >= 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_restrict_failed2.format(settings.botname))
    else:
        koduck.updateuserlevel(userid, 0)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_restrict_success.format(userid, settings.botname))

async def unrestrictuser(context, *args, **kwargs):
    #need exactly one mentioned user (the order in the mentioned list is unreliable)
    if len(context["message"].raw_mentions) != 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser)
    
    userid = context["message"].raw_mentions[0]
    userlevel = koduck.getuserlevel(userid)
    
    if userlevel != 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_unrestrict_failed)
    else:
        koduck.updateuserlevel(userid, 1)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_unrestrict_success.format(userid, settings.botname))

#When someone says a trigger message, respond with a custom response!
async def customresponse(context, *args, **kwargs):
    response = yadon.ReadRowFromTable(settings.customresponsestablename, context["command"])
    if response:
        return await koduck.sendmessage(context["message"], sendcontent=response[0])

async def addresponse(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addresponse_noparam)
    trigger = args[0].lower()
    response = context["paramline"][context["paramline"].index(settings.paramdelim)+1:].strip()
    result = yadon.AppendRowToTable(settings.customresponsestablename, trigger, [response])
    if result == -1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addresponse_failed)
    else:
        yadon.WriteRowToTable(settings.commandstablename, trigger, ["customresponse", "match", "1"])
        koduck.addcommand(trigger, customresponse, "match", 1)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addresponse_success.format(trigger, response))

async def removeresponse(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeresponse_noparam)
    trigger = args[0].lower()
    result = yadon.RemoveRowFromTable(settings.customresponsestablename, trigger)
    if result == -1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeresponse_failed.format(trigger))
    else:
        yadon.RemoveRowFromTable(settings.commandstablename, trigger)
        koduck.removecommand(trigger)
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removeresponse_success)

async def oops(context, *args, **kwargs):
    try:
        THEmessage = koduck.outputhistory[context["message"].author.id].pop()
    except (KeyError, IndexError):
        return settings.message_oops_failed
    try:
        await THEmessage.delete()
        return settings.message_oops_success
    except discord.errors.NotFound:
        return await oops(context, *args, **kwargs)

async def commands(context, *args, **kwargs):
    #filter out the commands that the user doesn't have permission to run
    #group the commands by function, multiple aliases for one function will be put in parentheses to indicate that fact to the user
    currentlevel = koduck.getuserlevel(context["message"].author.id)
    availablecommands = {}
    for commandname, command in koduck.commands.items():
        if command[2] <= currentlevel and command[1] == "prefix":
            try:
                availablecommands[command[0]].append(commandname)
            except KeyError:
                availablecommands[command[0]] = [commandname]
    output = ""
    for function, commandnames in availablecommands.items():
        if len(commandnames) > 1:
            output += "({}), ".format(", ".join(commandnames))
        else:
            output += "{}, ".format(commandnames[0])
    output = output[:-2]
    return await koduck.sendmessage(context["message"], sendcontent=output)

async def help(context, *args, **kwargs):
    messagename = args[0] if len(args) > 0 else ""
    helpmessage = gethelpmessage(messagename)
    if not helpmessage:
        helpmessage = gethelpmessage("unknowncommand")
    if helpmessage:
        return await koduck.sendmessage(context["message"], sendcontent=helpmessage)

async def userinfo(context, *args, **kwargs):
    #if there is no mentioned user, use the message sender instead
    if len(context["message"].raw_mentions) == 0:
        if context["message"].guild is None:
            user = context["message"].author
        else:
            user = context["message"].guild.get_member(context["message"].author.id)
            if user is None:
                user = context["message"].author
    elif len(context["message"].raw_mentions) == 1:
        if context["message"].guild is None:
            user = await koduck.client.get_user(context["message"].raw_mentions[0])
        else:
            user = context["message"].guild.get_member(context["message"].raw_mentions[0])
            if user is None:
                user = await koduck.client.get_user(context["message"].raw_mentions[0])
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser2)
    
    username = user.name
    discr = user.discriminator
    avatar = user.avatar_url
    creationdate = user.created_at
    
    #these properties only appear in Member object (subclass of User) which is only available from Servers
    if isinstance(user, discord.Member):
        activities = user.activities
        joindate = user.joined_at
        color = user.color
        if len(activities) == 0:
            embed = discord.Embed(title="{}#{}".format(username, discr), description=str(user.status), color=color)
        else:
            desc = ""
            for activity in activities:
                if isinstance(activity, discord.CustomActivity):
                    desc += "{}\n".format(activity)
                else:
                    typestring = {discord.ActivityType.playing: "Playing", discord.ActivityType.streaming: "Streaming", discord.ActivityType.listening: "Listening", discord.ActivityType.watching: "Watching", discord.ActivityType.unknown: "unknown"}[activity.type]
                    desc += "{} {}\n".format(typestring, activity.name)
            embed = discord.Embed(title="{}#{}".format(username, discr), description=desc, color=color)
        embed.add_field(name="Account creation date", value=creationdate.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.add_field(name="Server join date", value=joindate.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.set_thumbnail(url=avatar)
        return await koduck.sendmessage(context["message"], sendembed=embed)
    else:
        embed = discord.Embed(title="{}#{}".format(username, discr), description="Account creation date: {}".format(creationdate.strftime("%Y-%m-%d %H:%M:%S UTC")))
        embed.set_thumbnail(url=avatar)
        return await koduck.sendmessage(context["message"], sendembed=embed)

async def roll(context, *args, **kwargs):
    if len(args) > 0:
        try:
            max = int(args[0])
        except ValueError:
            max = settings.rolldefaultmax
    else:
        max = settings.rolldefaultmax
    
    if max >= 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_rollresult.format(context["message"].author.mention, random.randint(0, max)))
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_rollresult.format(context["message"].author.mention, random.randint(max, 0)))

def gethelpmessage(messagename):
    if messagename:
        helpmessage = yadon.ReadRowFromTable(settings.helpmessagestablename, "message_help_" + messagename)
    #Default message if no parameter is given
    else:
        helpmessage = yadon.ReadRowFromTable(settings.helpmessagestablename, "message_help")
    
    #Use {cp} for command prefix and {pd} for parameter delimiter
    if helpmessage:
        return helpmessage[0].replace("{cp}", settings.commandprefix).replace("{pd}", settings.paramdelim).replace("\\n", "\n").replace("\\t", "\t")
    else:
        return None

async def embed(context, *args, **kwargs):
    if "paramline" not in context:
        return await koduck.sendmessage(context["message"], sendcontent="I need a json to parse!")
    try:
        THEjson = json.loads(context["paramline"])
    except json.JSONDecodeError:
        return await koduck.sendmessage(context["message"], sendcontent="Failed to parse json")
    
    embed = discord.Embed(title="", description="")
    if "title" in THEjson:
        embed.title = THEjson["title"]
    if "description" in THEjson:
        embed.description = THEjson["description"]
    if "url" in THEjson:
        embed.url = THEjson["url"]
    if "image" in THEjson:
        embed.set_image(url=THEjson["image"])
    if "thumbnail" in THEjson:
        embed.set_thumbnail(url=THEjson["thumbnail"])
    
    if "color" in THEjson:
        embedcolor = THEjson["color"]
        try:
            embedcolor = int(embedcolor)
            embed.color = embedcolor
        except (TypeError, ValueError):
            try:
                embedcolorred = embedcolor["red"] if "red" in embedcolor else 0
                try:
                    embedcolorred = int(embedcolorred)
                except (TypeError, ValueError):
                    embedcolorred = 0
                embedcolorgreen = embedcolor["green"] if "green" in embedcolor else 0
                try:
                    embedcolorgreen = int(embedcolorgreen)
                except (TypeError, ValueError):
                    embedcolorgreen = 0
                embedcolorblue = embedcolor["blue"] if "blue" in embedcolor else 0
                try:
                    embedcolorblue = int(embedcolorblue)
                except (TypeError, ValueError):
                    embedcolorblue = 0
                embed.color = (embedcolorred * 256 * 256) + (embedcolorgreen * 256) + embedcolorblue
            except TypeError:
                pass
    
    if "footer" in THEjson:
        footer = THEjson["footer"]
        footertext = footer["text"] if "text" in footer else discord.Embed.Empty
        footericon = footer["icon"] if "icon" in footer else discord.Embed.Empty
        embed.set_footer(text=footertext, icon_url=footericon)
    
    if "author" in THEjson:
        author = THEjson["author"]
        authorname = author["name"] if "name" in author else ""
        authorurl = author["url"] if "url" in author else discord.Embed.Empty
        authoricon = author["icon"] if "icon" in author else discord.Embed.Empty
        embed.set_author(name=authorname, url=authorurl, icon_url=authoricon)
    
    if "fields" in THEjson:
        fields = THEjson["fields"]
        if isinstance(fields, list):
            for field in fields:
                try:
                    fieldname = field["name"] if "name" in field else ""
                    fieldvalue = field["value"] if "value" in field else ""
                    fieldinline = field["inline"] if "inline" in field else False
                    embed.add_field(name=fieldname, value=fieldvalue, inline=fieldinline)
                except TypeError:
                    pass
    
    if "channel" in THEjson:
        THEchannel = koduck.client.get_channel(THEjson["channel"])
        return await koduck.sendmessage(context["message"], sendchannel=THEchannel, sendembed=embed)
    else:
        return await koduck.sendmessage(context["message"], sendembed=embed)

async def bugreport(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent="no")
    channelid = 420089322524377088
    THEchannel = koduck.client.get_channel(channelid)
    originchannel = "<#{}>".format(context["message"].channel.id) if isinstance(context["message"].channel, discord.TextChannel) else ""
    embed = discord.Embed(description="Bug report from {} <@{}>: {}".format(originchannel, context["message"].author.id, context["paramline"]))
    await koduck.sendmessage(context["message"], sendchannel=THEchannel, sendembed=embed, ignorecd=True)
    return await koduck.sendmessage(context["message"], sendcontent="Bug report submitted. Thanks!")

############################
# POKEMON SHUFFLE COMMANDS #
############################
async def emojify2(context, *args, **kwargs):
    emojifiedmessage = emojify(context["paramline"], checkaliases=True)
    return await koduck.sendmessage(context["message"], sendcontent=emojifiedmessage)

async def addalias(context, *args, **kwargs):
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addalias_noparam)
    if len(args) > settings.managealiaslimit + 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_addalias_toomanyparams.format(settings.managealiaslimit))
    
    #parse params
    aliases = {k.lower():v[0] for k,v in yadon.ReadTable(settings.aliasestable).items()}
    try:
        original = aliases[args[0].lower()]
    except KeyError:
        original = args[0]
    
    #action
    succeeded = []
    failed = []
    failed2 = []
    for alias in args[1:]:
        if alias.lower() in aliases.keys():
            failed.append(alias)
        else:
            try:
                yadon.AppendRowToTable(settings.aliasestable, alias, [original])
                succeeded.append(alias)
            except OSError:
                failed2.append(alias)
    
    returnmessage = ""
    for s in succeeded:
        returnmessage += settings.message_addalias_success.format(original, s) + "\n"
    for f in failed:
        returnmessage += settings.message_addalias_failed.format(f, aliases[f.lower()]) + "\n"
    for f in failed2:
        returnmessage += settings.message_addalias_failed2.format(f) + "\n"
    
    return await koduck.sendmessage(context["message"], sendcontent=returnmessage)

async def removealias(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removealias_noparam)
    if len(args) > settings.managealiaslimit:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_removealias_toomanyparams.format(settings.managealiaslimit))
    
    aliases = {k.lower():v[0] for k,v in yadon.ReadTable(settings.aliasestable).items()}
    helper = {k.lower():k for k in yadon.ReadTable(settings.aliasestable).keys()}
    
    succeeded = []
    failed = []
    failed2 = []
    for alias in args:
        if alias.lower() not in aliases.keys():
            failed.append(alias)
        else:
            original = aliases[alias.lower()]
            try:
                yadon.RemoveRowFromTable(settings.aliasestable, helper[alias.lower()])
                succeeded.append((original, alias))
            except OSError:
                failed2.append(alias)
    
    returnmessage = ""
    for s in succeeded:
        returnmessage += settings.message_removealias_success.format(s[0], s[1]) + "\n"
    for f in failed:
        returnmessage += settings.message_removealias_failed.format(f) + "\n"
    for f in failed2:
        returnmessage += settings.message_removealias_failed2.format(f) + "\n"
    
    return await koduck.sendmessage(context["message"], sendcontent=returnmessage)

async def listaliases(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_listaliases_noparam)
    
    #parse params
    aliases = {k.lower():v[0] for k,v in yadon.ReadTable(settings.aliasestable).items()}
    try:
        original = aliases[args[0].lower()]
    except KeyError:
        original = args[0]
    
    #action
    results = []
    for k,v in yadon.ReadTable(settings.aliasestable).items():
        if original.lower() == v[0].lower():
            results.append(k)
    if len(results) == 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_listaliases_noresult)
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_listaliases_result.format(original, ", ".join(results)))

async def pokemon(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_pokemon_noparam)
    
    #parse params
    querypokemon = await pokemonlookup(context, query=args[0])
    if querypokemon is None:
        return "Unrecognized Pokemon"
    
    #retrieve data
    values = yadon.ReadRowFromTable(settings.pokemontable, querypokemon)
    if values is None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_pokemon_noresult.format(querypokemon))
    
    return await koduck.sendmessage(context["message"], sendembed=formatpokemonembed([querypokemon] + values))

async def skill(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_skill_noparam)
    
    #parse params
    queryskill = await pokemonlookup(context, query=args[0], skilllookup=True)
    if queryskill is None:
        return "Unrecognized Skill"
    
    #retrieve data
    values = yadon.ReadRowFromTable(settings.skillstable, queryskill)
    if values is None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_skill_noresult.format(queryskill))
    
    return await koduck.sendmessage(context["message"], sendembed=formatskillembed([queryskill] + values))

async def ap(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_ap_noparam)
    
    querybp = args[0]
    if querybp not in ["30", "40", "50", "60", "70", "80", "90"]:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_ap_invalidparam)
    aplist = yadon.ReadRowFromTable(settings.aptable, querybp)
    
    if len(args) >= 2:
        try:
            querylevel = int(args[1])
        except ValueError:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_ap_invalidparam2)
        if querylevel not in range(1, 31):
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_ap_invalidparam2)
        return await koduck.sendmessage(context["message"], sendcontent=aplist[querylevel-1])
    else:
        desc = "```"
        for i in range(len(aplist)):
            if i % 10 == 0:
                desc += "\n"
            if int(aplist[i]) >= 100:
                desc += "{} ".format(aplist[i])
            else:
                desc += " {} ".format(aplist[i])
        desc += "\n```"
        return await koduck.sendmessage(context["message"], sendcontent=desc)

async def exp(context, *args, **kwargs):
    #allow space delimited parameters
    if len(args) == 1:
        args = args[0].split(" ")
    
    if len(args) < 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_exp_noparam)
    
    #parse params
    querybp = args[0]
    if querybp not in ["30", "40", "50", "60", "70", "80", "90"]:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_exp_invalidparam)
    querybp = int(querybp)
    
    if len(args) == 2:
        querylevel1 = 1
        try:
            querylevel2 = int(args[1])
        except ValueError:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_exp_invalidparam2)
    else:
        try:
            querylevel1 = int(args[1])
            querylevel2 = int(args[2])
        except ValueError:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_exp_invalidparam2)
    if querylevel1 not in range(1, 31) or querylevel2 not in range(1, 31):
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_exp_invalidparam2)
    
    #retrieve data
    startexp = int(yadon.ReadRowFromTable(settings.exptable, str(querybp))[querylevel1])
    endexp = int(yadon.ReadRowFromTable(settings.exptable, str(querybp))[querylevel2])
    startap = int(yadon.ReadRowFromTable(settings.aptable, str(querybp))[querylevel1 - 1])
    endap = int(yadon.ReadRowFromTable(settings.aptable, str(querybp))[querylevel2 - 1])
    
    return await koduck.sendmessage(context["message"], sendcontent=settings.message_exp_result.format(querybp, endexp-startexp, querylevel1, startap, querylevel2, endap))

async def type(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_type_noparam)
    querytype = args[0].lower().capitalize()
    values = yadon.ReadRowFromTable(settings.typestable, querytype)
    if values is None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_type_invalidparam)
    else:
        return await koduck.sendmessage(context["message"], sendembed=formattypeembed([querytype] + values))

async def stage(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_stage_noparam)
    
    #allow space delimited parameters
    if len(args) == 1:
        temp = args[0].split(" ")
        if len(temp) > 1 and temp[-1].isdigit():
            args = ["".join(temp[:-1]), temp[-1]]
    
    resultnumber = 0
    try:
        shorthand = kwargs["shorthand"]
    except KeyError:
        shorthand = False
    try:
        startingboard = kwargs["startingboard"]
    except KeyError:
        startingboard = False
    
    #parse params
    querypokemon = args[0]
    if querypokemon.isdigit():
        stagetype = "main"
        stageindex = int(querypokemon)
    elif querypokemon.lower().startswith("ex") and querypokemon[2:].isdigit():
        stagetype = "expert"
        stageindex = int(querypokemon[2:])
    elif querypokemon.lower().startswith("s") and querypokemon[1:].isdigit():
        stagetype = "event"
        stageindex = int(querypokemon[1:])
    else:
        stagetype = "all"
    if len(args) >= 2:
        try:
            resultnumber = int(args[1])
            if resultnumber <= 0:
                return await koduck.sendmessage(context["message"], sendcontent=settings.message_stage_invalidparam)
        except ValueError:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_stage_invalidparam)
    
    results = []
    #retrieve data
    if stagetype == "main":
        values = yadon.ReadRowFromTable(settings.mainstagestable, str(stageindex))
        if values is None:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_stage_main_invalidparam.format(settings.mainstagesminindex, settings.mainstagesmaxindex))
        results.append([str(stageindex)] + values)
    elif stagetype == "expert":
        values = yadon.ReadRowFromTable(settings.expertstagestable, str(stageindex))
        if values is None:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_stage_expert_invalidparam.format(settings.expertstagesminindex + 1, settings.expertstagesmaxindex + 1))
        results.append(["ex{}".format(stageindex)] + values)
    elif stagetype == "event":
        values = yadon.ReadRowFromTable(settings.eventstagestable, str(stageindex))
        if values is None:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_stage_event_invalidparam.format(settings.eventstagesminindex, settings.eventstagesmaxindex))
        results.append(["s{}".format(stageindex)] + values)
    elif stagetype == "all":
        querypokemon = await pokemonlookup(context, query=querypokemon)
        if querypokemon is None:
            return "Unrecognized Pokemon"
        allstages = [(v[0],[str(k)]+v) for k,v in yadon.ReadTable(settings.mainstagestable).items()] + [(v[0],["ex{}".format(k)]+v) for k,v in yadon.ReadTable(settings.expertstagestable).items()] + [(v[0],["s{}".format(k)]+v) for k,v in yadon.ReadTable(settings.eventstagestable).items()]
        results = []
        for pokemon, values in allstages:
            if pokemon.lower() == querypokemon.lower():
                results.append(values)
    
    if len(results) == 0:
        noresultmessage = await koduck.sendmessage(context["message"], sendcontent=settings.message_stage_noresult.format(querypokemon))
    
    #if a result number is given
    elif resultnumber != 0:
        try:
            if startingboard:
                return await koduck.sendmessage(context["message"], sendembed=formatstartingboardembed(results[resultnumber-1]))
            else:
                return await koduck.sendmessage(context["message"], sendembed=formatstageembed(results[resultnumber-1], shorthand=shorthand))
        except IndexError:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_stage_resulterror.format(len(results)))
    
    elif len(results) == 1:
        if startingboard:
            return await koduck.sendmessage(context["message"], sendembed=formatstartingboardembed(results[0]))
        else:
            return await koduck.sendmessage(context["message"], sendembed=formatstageembed(results[0], shorthand=shorthand))
    
    elif len(results) > 1:
        indices = []
        outputstring = ""
        for i in range(len(results)):
            values = results[i]
            indices.append(values[0])
            if i < settings.choicereactlimit:
                outputstring += "\n{} {}".format(numberemojis[i+1], indices[i])
        
        choice = await choicereact(context, min(len(indices), settings.choicereactlimit), settings.message_stage_multipleresults+outputstring)
        if choice is None:
            return
        elif startingboard:
            return await koduck.sendmessage(context["message"], sendembed=formatstartingboardembed(results[choice]))
        else:
            return await koduck.sendmessage(context["message"], sendembed=formatstageembed(results[choice], shorthand=shorthand))

async def stageshorthand(context, *args, **kwargs):
    kwargs["shorthand"] = True
    return await stage(context, *args, **kwargs)

async def startingboard(context, *args, **kwargs):
    kwargs["startingboard"] = True
    return await stage(context, *args, **kwargs)

async def disruptionpattern(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_dp_noparam)
    
    #parse params
    try:
        queryindex = int(args[0])
    except ValueError:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_dp_invalidparam.format(settings.disruptionpatternsminindex, settings.disruptionpatternsmaxindex))
    
    if queryindex % 6 != 0 or queryindex < settings.disruptionpatternsminindex or queryindex > settings.disruptionpatternsmaxindex:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_dp_invalidparam.format(settings.disruptionpatternsminindex, settings.disruptionpatternsmaxindex))
    
    embed = discord.Embed()
    embed.set_image(url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Disruption Patterns/Pattern Index {}.png".format(queryindex).replace(" ", "%20"))
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def event(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_event_noparam)
    
    #allow space delimited parameters
    if len(args) == 1:
        temp = args[0].split(" ")
        if len(temp) > 1 and temp[-1].isdigit():
            args = ["".join(temp[:-1]), temp[-1]]
    
    resultnumber = 1
    
    #parse params
    if len(args) >= 2:
        try:
            resultnumber = int(args[1])
            if resultnumber <= 0:
                return await koduck.sendmessage(context["message"], sendcontent=settings.message_event_invalidparam)
        except ValueError:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_event_invalidparam)
    querypokemon = await pokemonlookup(context, query=args[0])
    if querypokemon is None:
        return "Unrecognized Pokemon"
    
    #retrieve data
    results = []
    for k,v in yadon.ReadTable(settings.eventstable).items():
        eventpokemon = [x.lower() for x in v[1].split("/")]
        if querypokemon.lower() in eventpokemon:
            results.append([k]+v)
    
    try:
        values = results[resultnumber-1]
    except IndexError:
        if len(results) != 0:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_event_resulterror.format(len(results)))
        else:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_event_noresult.format(querypokemon))
    
    if len(results) > 1:
        return await koduck.sendmessage(context["message"], sendcontent="Showing result {} of {}".format(resultnumber, len(results)), sendembed=formateventembed(values))
    else:
        return await koduck.sendmessage(context["message"], sendembed=formateventembed(values))

async def query(context, *args, **kwargs):
    try:
        useemojis = kwargs["useemojis"]
    except KeyError:
        useemojis = False
    
    #initialize query values to blank
    queries = {"dex":"", "type":"", "bp":"", "rmls":"", "maxap":"", "skill":"", "sortby":""}
    operations = {"bp":"", "rmls":"", "maxap":""}
    
    #parse params, put values into query values
    subqueries = context["params"]
    #allow space delimited parameters
    if len(subqueries) == 1:
        subqueries = subqueries[0].split(" ")
        newsubqueries = []
        for subquery in subqueries:
            if "=" not in subquery and len(newsubqueries) > 0:
                newsubqueries[-1] = newsubqueries[-1] + " " + subquery
            else:
                newsubqueries.append(subquery)
        subqueries = newsubqueries
                
    for subquery in subqueries:
        subquery = subquery.strip()
        #accept five (seven) different operations
        operation = ""
        for op in [">=", "<=", "=>", "=<", ">", "<", "="]:
            if len(subquery.split(op)) == 2:
                operation = op
                break
        if operation == "":
            continue
        
        #split
        left = subquery.split(operation)[0].lower()
        
        #sorta an exception
        if left == "rml":
            left = "rmls"
        
        #skills maybe used an alias
        if left == "skill":
            right = alias(subquery.split(operation)[1].lower())
        #make sure these are integers...
        elif left in ["bp", "rmls", "maxap"]:
            try:
                right = int(subquery.split(operation)[1])
            except ValueError:
                right = ""
        else:
            right = subquery.split(operation)[1]
        
        #assign values
        try:
            queries[left]
            queries[left] = right
            operations[left] = operation
        except KeyError:
            continue
    
    #generate a string to show which filters were recognized
    querystring = ""
    if "mega" in args:
        querystring += "mega and "
    for key in queries.keys():
        value = queries[key]
        if value != "":
            try:
                querystring += "{}{}{} and ".format(key, operations[key], value)
            except KeyError:
                querystring += "{}={} and ".format(key, value)
    if querystring != "":
        querystring = querystring[:-5]
    else:
        querystring = "[no filters recognized]"
    
    hits, hitsbp, hitsmaxap, hitstype = pokemonfilter(queries, operations, "mega" in args)
    
    #sort results and create a string to send
    if len(hits) > settings.queryresultlimit:
        outputstring = settings.message_query_toomanyresults.format(querystring, len(hits))
    elif len(hits) == 0:
        outputstring = settings.message_query_noresult.format(querystring)
    else:
        outputstring = settings.message_query_result.format(querystring, len(hits))
        
        #format output depending on which property to sort by
        if queries["sortby"] == "bp":
            buckets = {k:sorted(hitsbp[k]) for k in sorted(hitsbp.keys())}
        elif queries["sortby"] == "maxap":
            buckets = {k:sorted(hitsmaxap[k]) for k in sorted(hitsmaxap.keys())}
        elif queries["sortby"] == "type":
            buckets = {k:sorted(hitstype[k]) for k in sorted(hitstype.keys())}
        else:
            buckets = {"Results":sorted(hits)}
        
        for bucketkey in buckets.keys():
            outputstring += "\n**{}**: ".format(bucketkey)
            for item in buckets[bucketkey]:
                if useemojis:
                    try:
                        #surround ss pokemon with parentheses (instead of boldifying it, because, y'know... can't boldify emojis)
                        if item.find("**") != -1:
                            outputstring += "([{}])".format(item[:-2])
                        else:
                            outputstring += "[{}]".format(item)
                    except KeyError:
                        outputstring += "{} ".format("**" + item if item.find("**") != -1 else item)
                else:
                    outputstring += "{}, ".format("**" + item if item.find("**") != -1 else item)
            if not useemojis:
                outputstring = outputstring[:-2]
            else:
                outputstring = emojify(outputstring)
    
    return await koduck.sendmessage(context["message"], sendcontent=outputstring)

async def querywithemojis(context, *args, **kwargs):
    kwargs["useemojis"] = True
    return await query(context, *args, **kwargs)

async def skillwithpokemon(context, *args, **kwargs):
    try:
        useemojis = kwargs["useemojis"]
    except KeyError:
        useemojis = False
    
    queries = {"dex":"", "type":"", "bp":"", "rmls":"", "maxap":"", "skill":"", "sortby":""}
    operations = {"bp":"", "rmls":"", "maxap":""}
    
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_skill_noparam)
    
    #allow space delimited parameters
    if len(args) == 1:
        args = args[0].split(" ")
    
    queryskill = args[0]
    querytype = ""
    if len(args) > 1:
        #try to validate type, if not valid, assume it's part of skill name
        querytype = args[-1].lower().capitalize()
        values = yadon.ReadRowFromTable(settings.typestable, querytype)
        if values is None:
            querytype = ""
            queryskill = " ".join(args)
        else:
            queryskill = " ".join(args[:-1])
    
    #lookup and validate skill
    queryskill = await pokemonlookup(context, query=queryskill, skilllookup=True)
    if queryskill is None:
        return "Unrecognized Skill"
    
    #retrieve skill data
    values = yadon.ReadRowFromTable(settings.skillstable, queryskill)
    if values is None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_skill_noresult.format(queryskill))
    
    #query for pokemon with this skill
    queries["skill"] = queryskill
    if len(args) >= 2:
        queries["type"] = querytype
    hits, _, hitsmaxap, _ = pokemonfilter(queries, operations)
    
    #format output
    if len(hits) == 0:
        outputstring = "None"
    else:
        outputstring = ""
        buckets = {k:sorted(hitsmaxap[k]) for k in sorted(hitsmaxap.keys())}
        for bucketkey in buckets.keys():
            outputstring += "\n**{}**: ".format(bucketkey)
            for item in buckets[bucketkey]:
                if useemojis:
                    try:
                        #surround ss pokemon with parentheses (instead of boldifying it, because, y'know... can't boldify emojis)
                        if item.find("**") != -1:
                            outputstring += "([{}])".format(item[:-2])
                        else:
                            outputstring += "[{}]".format(item)
                    except KeyError:
                        outputstring += "{} ".format("**" + item if item.find("**") != -1 else item)
                else:
                    outputstring += "{}, ".format("**" + item if item.find("**") != -1 else item)
            if not useemojis:
                outputstring = outputstring[:-2]
            else:
                outputstring = emojify(outputstring)
    
    embed = formatskillembed([queryskill] + values)
    embed.add_field(name="Pokemon with this skill sorted by max AP", value=outputstring)
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def skillwithpokemonwithemojis(context, *args, **kwargs):
    kwargs["useemojis"] = True
    return await skillwithpokemon(context, *args, **kwargs)

#Helper function for query command
def pokemonfilter(queries, operations, mega=False):
    hits = []
    hitsbp = {}
    hitstype = {}
    hitsmaxap = {}
    
    #check each pokemon
    pokedex = yadon.ReadTable(settings.pokemontable)
    for name, values in pokedex.items():
        dex, type, bp, rmls, maxap, skill, ss, icons, msu, megapower = values
        bp = int(bp)
        rmls = int(rmls)
        maxap = int(maxap)
        
        if not mega and megapower:
            continue
        if mega and not megapower:
            continue
        
        tempss = [x.lower() for x in ss.split("/")]
        
        if queries["dex"] != "" and queries["dex"] != "{:03d}".format(int(dex)):
            continue
        if queries["bp"] != "":
            if operations["bp"] in [">=", "=>"] and bp < queries["bp"]:
                continue
            elif operations["bp"] in ["<=", "=<"] and bp > queries["bp"]:
                continue
            elif operations["bp"] == ">" and bp <= queries["bp"]:
                continue
            elif operations["bp"] == "<" and bp >= queries["bp"]:
                continue
            elif operations["bp"] == "=" and bp != queries["bp"]:
                continue
        if queries["rmls"] != "":
            if operations["rmls"] in [">=", "=>"] and rmls < queries["rmls"]:
                continue
            elif operations["rmls"] in ["<=", "=<"] and rmls > queries["rmls"]:
                continue
            elif operations["rmls"] == ">" and rmls <= queries["rmls"]:
                continue
            elif operations["rmls"] == "<" and rmls >= queries["rmls"]:
                continue
            elif operations["rmls"] == "=" and rmls != queries["rmls"]:
                continue
        if queries["maxap"] != "":
            if operations["maxap"] in [">=", "=>"] and maxap < queries["maxap"]:
                continue
            elif operations["maxap"] in ["<=", "=<"] and maxap > queries["maxap"]:
                continue
            elif operations["maxap"] == ">" and maxap <= queries["maxap"]:
                continue
            elif operations["maxap"] == "<" and maxap >= queries["maxap"]:
                continue
            elif operations["maxap"] == "=" and maxap != queries["maxap"]:
                continue
        if queries["type"] != "" and queries["type"].lower() != type.lower():
            continue
        if queries["skill"] != "" and queries["skill"].lower() != skill.lower() and queries["skill"].lower() not in tempss:
            continue
        
        #if skill is used, boldify pokemon with ss
        #it can't start with ** because it needs to be sorted by name
        if queries["skill"] != "" and queries["skill"].lower() in tempss:
            hitname = "{}**".format(name)
        else:
            hitname = name
        
        try:
            hitsbp[bp].append(hitname)
        except KeyError:
            hitsbp[bp] = [hitname]
        
        try:
            hitsmaxap[maxap].append(hitname)
        except KeyError:
            hitsmaxap[maxap] = [hitname]
        
        try:
            hitstype[type].append(hitname)
        except KeyError:
            hitstype[type] = [hitname]
        
        hits.append(hitname)
    
    return (hits, hitsbp, hitsmaxap, hitstype)

async def ebrewards(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_ebrewards_noparam)
    
    #parse params
    querypokemon = await pokemonlookup(context, query=args[0])
    if querypokemon is None:
        return "Unrecognized Pokemon"
    
    #retrieve data
    ebrewards = yadon.ReadRowFromTable(settings.ebrewardstable, querypokemon)
    if ebrewards is None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_ebrewards_noresult.format(querypokemon))
    
    return await koduck.sendmessage(context["message"], sendembed=formatebrewardsembed([querypokemon] + ebrewards))

async def ebdetails(context, *args, **kwargs):
    if len(args) < 1:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_eb_noparam)
    
    #allow space delimited parameters
    if len(args) == 1:
        temp = args[0].split(" ")
        if len(temp) > 1 and temp[-1].isdigit():
            args = ["".join(temp[:-1]), temp[-1]]
    
    querylevel = 0
    if len(args) >= 2:
        querylevel = args[1]
        try:
            if int(querylevel) <= 0:
                return await koduck.sendmessage(context["message"], sendcontent=settings.message_eb_invalidparam)
            querylevel = int(querylevel)
        except ValueError:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_eb_invalidparam)
    
    #parse params
    querypokemon = await pokemonlookup(context, query=args[0])
    if querypokemon is None:
        return "Unrecognized Pokemon"
    
    ebdetails = yadon.ReadRowFromTable(settings.ebdetailstable, querypokemon)
    if ebdetails is None:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_eb_noresult.format(querypokemon))
    
    #optional level param which will return a stage embed instead
    if querylevel > 0:
        #should be in increasing order
        for levelset in ebdetails:
            startlevel, endlevel, stageindex = levelset.split("/")
            if int(endlevel) < 0 or querylevel < int(endlevel):
                break
        values = yadon.ReadRowFromTable(settings.eventstagestable, stageindex)
        
        #extra string to show level range of this eb stage
        if int(startlevel) == int(endlevel) - 1:
            extra = " (Level {})".format(startlevel)
        elif int(endlevel) < 0:
            extra = " (Levels {}+)".format(startlevel)
        else:
            extra = " (Levels {} to {})".format(startlevel, int(endlevel) - 1)
        
        try:
            shorthand = kwargs["shorthand"]
        except KeyError:
            shorthand = False
        
        return await koduck.sendmessage(context["message"], sendembed=formatstageembed(["s{}".format(stageindex)] + values, extra=extra, shorthand=shorthand))
    
    else:
        return await koduck.sendmessage(context["message"], sendembed=formatebdetailsembed([querypokemon] + ebdetails))

async def ebdetailsshorthand(context, *args, **kwargs):
    kwargs["shorthand"] = True
    return await ebdetails(context, *args, **kwargs)

async def week(context, *args, **kwargs):
    if len(args) < 1:
        queryweek = currentweek()
    else:
        try:
            queryweek = int(args[0])
        except ValueError:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_week_invalidparam.format(settings.numweeks, settings.numweeks))
        if queryweek < 1 or queryweek > settings.numweeks:
            return await koduck.sendmessage(context["message"], sendcontent=settings.message_week_invalidparam.format(settings.numweeks, settings.numweeks))
    
    return await koduck.sendmessage(context["message"], sendembed=formatweekembed(queryweek))

async def smrewards(context, *args, **kwargs):
    table = yadon.ReadTable(settings.smrewardstable)
    level = ""
    firstclear = ""
    repeatclear = ""
    for k,v in table.items():
        level += "{}\n".format(k)
        firstclear += emojify("[{}] x{}\n".format(v[0], v[1]))
        repeatclear += emojify("[{}] x{}\n".format(v[2], v[3]))
    
    embed = discord.Embed(title="Survival Mode Rewards", color=0xff0000)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="First Clear", value=firstclear, inline=True)
    embed.add_field(name="Repeat Clear", value=repeatclear, inline=True)
    return await koduck.sendmessage(context["message"], sendembed=embed)

async def drainlist(context, *args, **kwargs):
    #allow space delimited parameters
    if len(args) == 1:
        args = args[0].split(" ")
    
    #first arg script name, second arg hp, third arg moves
    if len(args) != 2:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_drainlist_noparam)
 
    try:
        hp = int(args[0])
        moves = int(args[1])
    except ValueError:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_drainlist_invalidparam)
    
    if hp <= 0 or moves <= 0:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_drainlist_invalidparam)
    
    if moves > 55:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_drainlist_invalidparam2)
 
    output = "```\nhp:    {}\nmoves: {}\n\n".format(str(hp), str(moves))
 
    for i in range(moves):
        drainAmount = int(floor(float(hp) * 0.1))
        output += '{:>2}: {:>5} ({:>6} => {:>6})\n'.format(moves - i, drainAmount, hp, hp - drainAmount)
        hp -= drainAmount
    
    output += "```"
    
    return await koduck.sendmessage(context["message"], sendcontent=output)

#Look up a queried Pokemon to see if it exists as an alias (and/or in an additionally provided list), provide some suggestions to the user if it doesn't, and return the corrected query, otherwise None
async def pokemonlookup(context, query=None, enableDYM=True, skilllookup=False, *args, **kwargs):
    if query is None:
        query = args[0]
    
    aliases = {k.lower():v[0] for k,v in yadon.ReadTable(settings.aliasestable).items()}
    try:
        query = aliases[query.lower()]
    except KeyError:
        pass
    
    pokemondict = {k.lower():k for k in yadon.ReadTable(settings.pokemontable).keys()}
    skilldict = {k.lower():k for k in yadon.ReadTable(settings.skillstable).keys()}
    #get properly capitalized name
    try:
        if skilllookup:
            query = skilldict[query.lower()]
        else:
            query = pokemondict[query.lower()]
    except KeyError:
        pass
    
    if (not skilllookup and query.lower() not in pokemondict.keys()) or (skilllookup and query.lower() not in skilldict.keys()):
        if not enableDYM:
            return
        
        if skilllookup:
            add = skilldict.values()
        else:
            add = pokemondict.values()
        
        closematches = difflib.get_close_matches(query, list(aliases.keys()) + list(add), n=settings.DYMlimit, cutoff=settings.DYMthreshold)
        if len(closematches) == 0:
            await koduck.sendmessage(context["message"], sendcontent=settings.message_pokemonlookup_noresult.format("Skill" if skilllookup else "Pokemon", query))
            return
        
        choices = []
        noduplicates = []
        for closematch in closematches:
            try:
                if aliases[closematch].lower() not in noduplicates:
                    choices.append((closematch, aliases[closematch]))
                    noduplicates.append(aliases[closematch].lower())
            except KeyError:
                if closematch.lower() not in noduplicates:
                    choices.append((closematch, closematch))
                    noduplicates.append(closematch.lower())
        
        outputstring = ""
        for i in range(len(choices)):
            outputstring += "\n{} {}".format(numberemojis[i+1], choices[i][0] if choices[i][0] == choices[i][1] else "{} ({})".format(choices[i][0], choices[i][1]))
        result = await choicereact(context, len(choices), settings.message_pokemonlookup_noresult.format("Skill" if skilllookup else "Pokemon", query)+"\n"+settings.message_pokemonlookup_suggest+outputstring)
        if result is None:
            return
        else:
            return choices[result][1]
    
    else:
        return query

async def botstats(context, *args, **kwargs):
    #if there is no mentioned user, use the message sender instead
    if len(context["message"].raw_mentions) == 0:
        targetauthorid = context["message"].author.id
    elif len(context["message"].raw_mentions) == 1:
        targetauthorid = context["message"].raw_mentions[0]
    else:
        return await koduck.sendmessage(context["message"], sendcontent=settings.message_nomentioneduser2)

    validcommands = [commandname for commandname, commanddetails in koduck.commands.items()]
    stats = yadon.ReadTable("log")
    ans = {}
    validcount = 0
    invalidcount = 0
    for key, values in stats.items():
        if len(values) < 6:
            authorid = values[2]
            THEcommand = values[3]
            commandresult = values[4]
        else:
            authorid = values[3]
            THEcommand = values[4]
            commandresult = values[5]
        
        if authorid != targetauthorid:
            continue
        
        if THEcommand.startswith(settings.commandprefix):
            THEcommand = THEcommand[1:]
        if THEcommand.find(" ") != -1:
            THEcommand = THEcommand[:THEcommand.index(" ")]
        
        if THEcommand in validcommands:
            if THEcommand not in ans:
                ans[THEcommand] = 0
            ans[THEcommand] += 1
            validcount += 1
        
        if commandresult == settings.message_unknowncommand or commandresult == settings.message_cooldownactive or commandresult == settings.message_restrictedaccess:
            invalidcount += 1
            validcount -= 1
    sortedans = OrderedDict(sorted(ans.items(), key=lambda x: x[1], reverse=True))
    
    outputstring = "Bot stats for <@!{}>\n".format(targetauthorid)
    for key, value in sortedans.items():
        outputstring += "{}: **{}**, ".format(key, value)
    outputstring = outputstring[:-2]
    if validcount > 0:
        outputstring += "\nvalid commands: **{}**".format(validcount)
    if invalidcount > 0:
        outputstring += "\ninvalid commands: **{}**".format(invalidcount)
    
    return await koduck.sendmessage(context["message"], sendcontent=outputstring)

async def totalbotstats(context, *args, **kwargs):
    validcommands = [commandname for commandname, commanddetails in koduck.commands.items()]
    stats = yadon.ReadTable("log")
    ans = {}
    validcount = 0
    invalidcount = 0
    for key, values in stats.items():
        if len(values) < 6:
            THEcommand = values[3]
            commandresult = values[4]
        else:
            THEcommand = values[4]
            commandresult = values[5]
        
        if THEcommand.startswith(settings.commandprefix):
            THEcommand = THEcommand[1:]
        if THEcommand.find(" ") != -1:
            THEcommand = THEcommand[:THEcommand.index(" ")]
        
        if THEcommand in validcommands:
            if THEcommand not in ans:
                ans[THEcommand] = 0
            ans[THEcommand] += 1
            validcount += 1
        
        if commandresult == settings.message_unknowncommand or commandresult == settings.message_cooldownactive or commandresult == settings.message_restrictedaccess:
            invalidcount += 1
            validcount -= 1
    sortedans = OrderedDict(sorted(ans.items(), key=lambda x: x[1], reverse=True))
    
    outputstring = "Bot stats\n"
    for key, value in sortedans.items():
        outputstring += "{}: **{}**, ".format(key, value)
    outputstring = outputstring[:-2]
    if validcount > 0:
        outputstring += "\nvalid commands: **{}**".format(validcount)
    if invalidcount > 0:
        outputstring += "\ninvalid commands: **{}**".format(invalidcount)
    
    return await koduck.sendmessage(context["message"], sendcontent=outputstring)

async def choicereact(context, numchoices, questionstring):
    #there are only 9 (10) number emojis :(
    numchoices = min(numchoices, 9)
    numchoices = min(numchoices, settings.choicereactlimit)
    THEmessage = await koduck.sendmessage(context["message"], sendcontent=questionstring)
    choiceemojis = numberemojis[:numchoices+1]
    
    #add reactions
    for i in range(len(choiceemojis)):
        await THEmessage.add_reaction(choiceemojis[i])
    
    #wait for reaction (with timeout)
    def check(reaction, user):
        return user == context["message"].author and str(reaction.emoji) in choiceemojis
    try:
        reaction, _ = await koduck.client.wait_for('reaction_add', timeout=settings.DYMtimeout, check=check)
    except asyncio.TimeoutError:
        reaction = None
    
    #remove reactions
    for i in range(len(choiceemojis)):
        try:
            await THEmessage.remove_reaction(choiceemojis[i], koduck.client.user)
        except discord.errors.NotFound:
            break
    
    #return the chosen answer if there was one
    if reaction is None:
        return
    resultemoji = reaction.emoji
    choice = choiceemojis.index(resultemoji)
    if choice == 0:
        return
    else:
        return choice-1

####################
# EMBED GENERATORS #
####################
def formatpokemonembed(values):
    name, dex, type, bp, rmls, maxap, skill, _, icons, msu, megapower = values
    ss = values[7].split("/")
    if megapower:
        stats = "**Dex**: {:03d}\n**Type**: {}\n**Icons**: {}\n**MSUs**: {}\n**Mega Effects**: {}".format(int(dex), type, icons, msu, megapower)
    else:
        stats = "**Dex**: {:03d}\n**Type**: {}\n**BP**: {}\n**RMLs**: {}\n**Max AP**: {}\n**Skill**: {}".format(int(dex), type, bp, rmls, maxap, skill)
        if len(ss) > 0 and ss[0]:
            stats += " ({})".format(", ".join(ss))
    
    embed = discord.Embed(title=name, color=typecolor[type], description=stats)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/Icons/{}.png".format(name.replace(":", "").replace(" ", "%20")))
    return embed

def formatskillembed(values):
    name, desc, rate1, rate2, rate3, type, multiplier, bonuseffect, bonus1, bonus2, bonus3, bonus4, sp1, sp2, sp3, sp4 = values
    notes = yadon.ReadRowFromTable(settings.skillnotestable, name)
    
    stats = "**Description**: {}\n".format(desc)
    if notes is not None:
        stats += "**Notes**: {}\n".format(emojify(notes[0]))
    stats += "**Activation Rates**: {}% / {}% / {}%\n".format(rate1, rate2, rate3)
    if type != "Mega Boost":
        stats += "**Damage Multiplier**: x{}\n".format(multiplier)
    if (bonuseffect == "Activation Rate"):
        stats += "**SL{} Bonus**: +{:0.0f}% ({:0.0f}% / {:0.0f}% / {:0.0f}%)\n".format(2, float(bonus1), min(100, int(rate1) + float(bonus1)) if rate1 != "0" else 0, min(100, int(rate2) + float(bonus1)) if rate2 != "0" else 0, min(100, int(rate3) + float(bonus1)) if rate3 != "0" else 0)
        stats += "**SL{} Bonus**: +{:0.0f}% ({:0.0f}% / {:0.0f}% / {:0.0f}%)\n".format(3, float(bonus2), min(100, int(rate1) + float(bonus2)) if rate1 != "0" else 0, min(100, int(rate2) + float(bonus2)) if rate2 != "0" else 0, min(100, int(rate3) + float(bonus2)) if rate3 != "0" else 0)
        stats += "**SL{} Bonus**: +{:0.0f}% ({:0.0f}% / {:0.0f}% / {:0.0f}%)\n".format(4, float(bonus3), min(100, int(rate1) + float(bonus3)) if rate1 != "0" else 0, min(100, int(rate2) + float(bonus3)) if rate2 != "0" else 0, min(100, int(rate3) + float(bonus3)) if rate3 != "0" else 0)
        stats += "**SL{} Bonus**: +{:0.0f}% ({:0.0f}% / {:0.0f}% / {:0.0f}%)\n".format(5, float(bonus4), min(100, int(rate1) + float(bonus4)) if rate1 != "0" else 0, min(100, int(rate2) + float(bonus4)) if rate2 != "0" else 0, min(100, int(rate3) + float(bonus4)) if rate3 != "0" else 0)
    elif (bonuseffect == "Multiply Damage"):
        stats += "**SL{} Bonus**: x{:0.2f} (x{:0.2f})\n".format(2, float(bonus1), float(multiplier) * float(bonus1))
        stats += "**SL{} Bonus**: x{:0.2f} (x{:0.2f})\n".format(3, float(bonus2), float(multiplier) * float(bonus2))
        stats += "**SL{} Bonus**: x{:0.2f} (x{:0.2f})\n".format(4, float(bonus3), float(multiplier) * float(bonus3))
        stats += "**SL{} Bonus**: x{:0.2f} (x{:0.2f})\n".format(5, float(bonus4), float(multiplier) * float(bonus4))
    elif (bonuseffect == "Add Damage"):
        stats += "**SL{} Bonus**: +{:0.2f} (x{:0.2f})\n".format(2, float(bonus1), float(multiplier) + float(bonus1))
        stats += "**SL{} Bonus**: +{:0.2f} (x{:0.2f})\n".format(3, float(bonus2), float(multiplier) + float(bonus2))
        stats += "**SL{} Bonus**: +{:0.2f} (x{:0.2f})\n".format(4, float(bonus3), float(multiplier) + float(bonus3))
        stats += "**SL{} Bonus**: +{:0.2f} (x{:0.2f})\n".format(5, float(bonus4), float(multiplier) + float(bonus4))
    stats += "**SP Requirements**: {} => {} => {} => {} (Total: {})\n".format(int(sp1), int(sp2) - int(sp1), int(sp3) - int(sp2), int(sp4) - int(sp3), int(sp4))
    
    THEcolor = {"Offensive":0xff0000, "Defensive":0x0000ff, "Mega Boost":0x00ff00}[type]
    embed = discord.Embed(title=name, color=THEcolor, description=stats)
    return embed

def formattypeembed(values):
    type, se, nve, weak, res, imm = values
    embed = discord.Embed(title=type, color=typecolor[type])
    embed.add_field(name="Super Effective Against", value=se)
    embed.add_field(name="Not Very Effective Against", value=nve)
    embed.add_field(name="Weaknesses", value=weak)
    embed.add_field(name="Resistances", value=res)
    embed.add_field(name="Status Effect Immunities", value=imm)
    return embed

def formatstageembed(values, extra="", shorthand=False):
    index, pokemon, hp, hpmobile, moves, seconds, exp, basecatch, bonuscatch, basecatchmobile, bonuscatchmobile, defaultsupports, srank, arank, brank, numsrankstounlock, ispuzzlestage, extrahp, layoutindex, costtype, attemptcost, drop1item, drop1amount, drop2item, drop2amount, drop3item, drop3amount, drop1rate, drop2rate, drop3rate, items, rewards, rewardsUX, cd1, cd2, cd3 = values
    notes = yadon.ReadRowFromTable(settings.stagenotestable, index)
    
    if index.isdigit():
        stagetype = "Main"
    elif index.startswith("ex"):
        stagetype = "Expert"
        index = index[2:]
    elif index.startswith("s"):
        stagetype = "Event"
        index = index[1:]
    
    stats = "**HP**: {}{}{}{}".format(hp, " (UX: {})".format(int(hp) * 3) if stagetype == "Main" and ispuzzlestage != "Puzzle" else "", " + {}".format(extrahp) if extrahp != "0" else "", " (Mobile: {}{})".format(hpmobile, " (UX: {})".format(int(hpmobile) * 3) if stagetype == "Main" and ispuzzlestage != "Puzzle" else "") if hp != hpmobile else "")
    stats += "\n**{}**: {}\n**Experience**: {}\n**Catchability**: {}% + {}%/{}".format("Moves" if moves != "0" else "Seconds", moves if moves != "0" else seconds, exp, basecatch, bonuscatch, "move" if moves != "0" else "3sec")
    if basecatch != basecatchmobile or bonuscatch != bonuscatchmobile:
        stats += " (Mobile: {}% + {}%/{})".format(basecatchmobile, bonuscatchmobile, "move" if moves != "0" else "3sec")
    stats += "\n**Default Supports**: {}".format(emojify("".join(["[{}]".format(p) for p in defaultsupports.split("/")])))
    stats += "\n**Rank Requirements**: {} / {} / {}".format(srank, arank, brank)
    if stagetype == "Expert":
        stats += "\n**S-Ranks to unlock**: {}".format(numsrankstounlock)
    stats += "\n**Attempt Cost**: {} x{}".format(emojify("[{}]".format(costtype)), attemptcost)
    if drop1item != "Nothing" or drop2item != "Nothing" or drop3item != "Nothing":
        stats += "\n**Drop Items**: {}{} / {}{} / {}{}\n**Drop Rates**: {}% / {}% / {}%".format(emojify("[{}]".format(drop1item)), " x{}".format(drop1amount) if drop1amount != "1" else "", emojify("[{}]".format(drop2item)), " x{}".format(drop2amount) if drop2amount != "1" else "", emojify("[{}]".format(drop3item)), " x{}".format(drop3amount) if drop3amount != "1" else "", drop1rate, drop2rate, drop3rate)
    #auto remove c-1 if less than 4 supports
    if len(defaultsupports.split("/")) < 4 and "C-1" in items.split("/"):
        temp = items.split("/")
        temp.remove("C-1")
        stats += "\n**Items**: {}".format(emojify("".join(["[{}]".format(item) for item in temp])))
    else:
        stats += "\n**Items**: {}".format(emojify("".join(["[{}]".format(item) for item in items.split("/")])))
    if rewards != "Nothing":
        stats += "\n**Initial clear reward**: {}".format(emojify(rewards))
    if rewardsUX != "Nothing":
        stats += "\n**UX Initial clear reward**: {}".format(emojify(rewardsUX))
    if notes is not None:
        stats += "\n**Notes**: {}".format(emojify(notes[0]).replace("\\n", "\n"))
    
    header = "{} Stage {}: {}{}{}".format(stagetype, index, pokemon, " " + emojify("[{}]".format(pokemon)), extra)
    type = yadon.ReadRowFromTable(settings.pokemontable, pokemon)[1]
    embed = discord.Embed(title=header, color=typecolor[type], description=stats)
    if not shorthand:
        if layoutindex != "0":
            embed.set_thumbnail(url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/{} Stages Layouts/Layout Index {}.png".format(stagetype, layoutindex).replace(" ", "%20"))
            embed.url = "https://raw.githubusercontent.com/Chupalika/Kaleo/icons/{} Stages Layouts/Layout Index {}.png".format(stagetype, layoutindex).replace(" ", "%20")
        if cd1 != "Nothing":
            embed.add_field(name="**Countdown 1**", value=emojify(cd1.replace("\\n", "\n")), inline=False)
        if cd2 != "Nothing":
            embed.add_field(name="**Countdown 2**", value=emojify(cd2.replace("\\n", "\n")), inline=False)
        if cd3 != "Nothing":
            embed.add_field(name="**Countdown 3**", value=emojify(cd3.replace("\\n", "\n")), inline=False)
    return embed

def formatstartingboardembed(values):
    index, pokemon, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, layoutindex, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = values
    
    if index.isdigit():
        stagetype = "Main"
    elif index.startswith("ex"):
        stagetype = "Expert"
        index = index[2:]
    elif index.startswith("s"):
        stagetype = "Event"
        index = index[1:]
    
    header = "{} Stage Index {}: {} {}".format(stagetype, index, pokemon, emojify("[{}]".format(pokemon)))
    type = yadon.ReadRowFromTable(settings.pokemontable, pokemon)[1]
    embed = discord.Embed(title=header, color=typecolor[type])
    if layoutindex != 0:
        embed.set_image(url="https://raw.githubusercontent.com/Chupalika/Kaleo/icons/{} Stages Layouts/Layout Index {}.png".format(stagetype, layoutindex).replace(" ", "%20"))
    else:
        embed.add_field(name="No initial board layout", value=None, inline=False)
    return embed

def formateventembed(values):
    index, stagetype, eventpokemon, _, repeattype, repeatparam1, repeatparam2, starttime, endtime, durationstring, coststring, attemptsstring, encounterrates = values
    
    eventpokemon = eventpokemon.split("/")
    encounterrates = encounterrates.split("/")
    coststring = "" if coststring == "Nothing" else coststring
    attemptsstring = "" if attemptsstring == "Nothing" else attemptsstring

    eventpokemonstring = ""
    if stagetype == "Daily":
        header = "Daily Pokémon"
        for i in range(len(eventpokemon)):
            eventpokemonstring += "{}: {} [{}]\n".format(["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][(i+1)%7], eventpokemon[i], eventpokemon[i])
    elif stagetype == "Escalation":
        header = "Escalation Battles: {} [{}]".format(eventpokemon[0], eventpokemon[0])
    elif stagetype == "Safari":
        header = "Pokémon Safari"
        for i in range(len(eventpokemon) - 1):
            #For some reason the first pokemon is duplicated here
            eventpokemonstring += "[{}] {} ({}%)\n".format(eventpokemon[i+1], eventpokemon[i+1], encounterrates[i])
    elif stagetype == "Monthly":
        header = "Monthly Challenge"
        for i in range(len(eventpokemon)):
            eventpokemonstring += "[{}] {} ({}%)\n".format(eventpokemon[i], eventpokemon[i], encounterrates[i])
    else:
        header = "{} [{}]".format(eventpokemon[0], eventpokemon[0])
    
    dateheader = "{} Event".format(repeattype)
    if repeattype == "Rotation":
        dateheader += ": Week {}/24".format(int(repeatparam1) + 1)
    
    if repeattype != "Weekly":
        st = starttime.split("/")
        et = endtime.split("/")
        if repeattype == "Rotation":
            starttime = datetime.datetime(int(st[0]), int(st[1]), int(st[2]), int(st[3]), int(st[4]), tzinfo=pytz.utc)
            endtime = datetime.datetime(int(et[0]), int(et[1]), int(et[2]), int(et[3]), int(et[4]), tzinfo=pytz.utc)
            while endtime < datetime.datetime.now(tz=pytz.utc):
                starttime = starttime + datetime.timedelta(168)
                endtime = endtime + datetime.timedelta(168)
            starttime = starttime.strftime("%Y/%m/%d %H:%M UTC")
            endtime = endtime.strftime("%Y/%m/%d %H:%M UTC")
        else:
            starttime = "{}/{}/{} {}:{} UTC".format(st[0], st[1], st[2], st[3], st[4])
            endtime = "{}/{}/{} {}:{} UTC".format(et[0], et[1], et[2], et[3], et[4])
    
    embed = discord.Embed(title=emojify(header), color={"Unknown":0xa0aab4, "Challenge":0x00aaff, "Daily":0xff9400, "Meowth":0xfff9b7, "Competitive":0xe44406, "Escalation":0x4e7e4e, "Safari":0x108632, "Items":0x00aaff, "Monthly":0x00aaff}[stagetype])
    if eventpokemonstring:
        embed.add_field(name="Event Pokémon", value=emojify(eventpokemonstring), inline=False)
    embed.add_field(name=dateheader, value="Event duration: {}".format("{} to {} ({})".format(starttime, endtime, durationstring)), inline=False)
    if coststring != "" or attemptsstring != "":
        embed.add_field(name="Misc. Details", value=emojify(coststring+"\n"+attemptsstring), inline=False)
    return embed

def formatebrewardsembed(values):
    pokemon = values[0]
    rewards = values[1:]
    
    stats = ""
    for entry in rewards:
        level, rewarditem, rewardamount = entry.split("/")
        stats += "Level {} reward: {} x{}\n".format(level, emojify("[{}]".format(rewarditem)), rewardamount)
    stats = stats[:-1]
    
    embed = discord.Embed(title="{} Escalation Battles Rewards".format(pokemon), color=0x4e7e4e, description=stats)
    return embed

def formatebdetailsembed(values):
    pokemonname = values[0]
    levelsets = values[1:]
    
    stats = ""
    for levelset in levelsets:
        startlevel, endlevel, stageindex = levelset.split("/")
        stagevalues = yadon.ReadRowFromTable(settings.eventstagestable, stageindex)
        
        if endlevel == "-1":
            levels = "**Levels {}+**".format(startlevel)
        elif int(startlevel) == int(endlevel) - 1:
            levels = "**Level {}**".format(startlevel)
        else:
            levels = "**Levels {} to {}**".format(startlevel, int(endlevel) - 1)
        
        extra = ""
        defaultsupports = stagevalues[10].split("/")
        if len(defaultsupports) == 3:
            extra = " **(3 supports)**"
        elif len(defaultsupports) == 5:
            extra = emojify(" **(5th support: [{}])**".format(defaultsupports[0]))
        
        stats += "{}: {}{} / {}{}\n".format(levels, stagevalues[1], " + {}".format(stagevalues[16]) if stagevalues[16] != "0" else "", stagevalues[4] if stagevalues[4] != "0" else stagevalues[3], extra)
    
    embed = discord.Embed(title="{} Escalation Battles Details".format(pokemonname), color=0x4e7e4e, description=stats)
    return embed

def formatweekembed(queryweek):
    comp = ""
    daily = ""
    oad = ""
    gc = ""
    eb = ""
    safari = ""
    
    events = yadon.ReadTable(settings.eventstable)
    for index, values in events.items():
        stagetype, eventpokemon, stageindices, repeattype, repeatparam1, repeatparam2, _, _, _, coststring, _, encounterrates = values
        if repeattype != "Rotation" or int(repeatparam1)+1 != queryweek:
            continue
        
        eventpokemon = eventpokemon.split("/")
        stagevalues = yadon.ReadRowFromTable(settings.eventstagestable, stageindices.split("/")[0])
        _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, costtype, attemptcost, drop1item, drop1amount, drop2item, drop2amount, drop3item, drop3amount, drop1rate, drop2rate, drop3rate, items, _, _, _, _, _ = stagevalues
        
        dropsstring = ""
        attemptcoststring = ""
        unlockcoststring = ""
        if drop1item != "Nothing" or drop2item != "Nothing" or drop3item != "Nothing":
            #need to add this because sometimes it goes over the character limit...
            if drop1item == drop2item == drop3item and drop1amount == drop2amount == drop3amount:
                dropsstring += " [{}{} {}% / {}% / {}%]".format(emojify("[{}]".format(drop1item)), " x{}".format(drop1amount) if drop1amount != "1" else "", drop1rate, drop2rate, drop3rate)
            else:
                dropsstring += " [{}{} {}% / {}{} {}% / {}{} {}%]".format(emojify("[{}]".format(drop1item)), " x{}".format(drop1amount) if drop1amount != "1" else "", drop1rate, emojify("[{}]".format(drop2item)), " x{}".format(drop2amount) if drop2amount != "1" else "", drop2rate, emojify("[{}]".format(drop3item)), " x{}".format(drop3amount) if drop3amount != "1" else "", drop3rate)
        if attemptcost != "1" or costtype != "Heart":
            attemptcoststring += " ({} x{})".format(emojify("[{}]".format(costtype)), attemptcost)
        if coststring != "Nothing":
            unlockcoststring += " ({} {})".format(emojify(coststring.split(" ")[1]), coststring.split(" ")[2])
        
        #Challenge
        if stagetype == "Challenge":
            gc += "- {}{}{}{}\n".format(emojify("[{}]".format(eventpokemon[0])), dropsstring, attemptcoststring, unlockcoststring)
        #Daily
        if stagetype == "Daily":
            eventpokemon = removeduplicates(eventpokemon)
            if len(eventpokemon) == 1:
                oad += "- {}{}{}".format(emojify("[{}]".format(eventpokemon[0])), dropsstring, attemptcoststring)
            else:
                daily += "- "
                for pokemon in eventpokemon:
                    daily += emojify("[{}]".format(pokemon))
                daily += dropsstring
        #Competition
        if stagetype == "Competitive":
            #There are duplicate entries... grab only one of them
            if comp == "":
                itemsstring = ""
                for item in items.split("/"):
                    itemsstring += emojify("[{}]".format(item))
                comp += "- {} ({})".format(emojify("[{}]".format(eventpokemon[0])), itemsstring)
        #EB
        if stagetype == "Escalation":
            eb += "- {}{}".format(emojify("[{}]".format(eventpokemon[0])), dropsstring)
        #Safari
        if stagetype == "Safari":
            #For some reason the first pokemon is duplicated here
            eventpokemon = eventpokemon[1:]
            encounterrates = encounterrates.split("/")
            safari += "- "
            for j in range(len(eventpokemon)):
                safari += "{} ({}%), ".format(emojify("[{}]".format(eventpokemon[j])), encounterrates[j])
            safari = safari[:-2]
            safari += dropsstring
    
    embed = discord.Embed(title="Event Rotation Week {}".format(queryweek), color=0xff0000)
    if comp != "":
        embed.add_field(name="Competitive Stage", value=comp, inline=False)
    embed.add_field(name="Challenges", value=gc, inline=False)
    if eb != "":
        embed.add_field(name="Escalation Battles", value=eb, inline=False)
    if safari != "":
        embed.add_field(name="Safari", value=safari, inline=False)
    embed.add_field(name="One Chance a Day!", value=oad, inline=False)
    embed.add_field(name="Daily", value=daily, inline=False)
    
    return embed

##################
# MISC FUNCTIONS #
##################
def alias(query):
    aliases = {k.lower():v[0] for k,v in yadon.ReadTable(settings.aliasestable).items()}
    try:
        return aliases[query.lower()]
    except KeyError:
        return query

def strippunctuation(string):
    return string.replace(" ", "").replace("(", "").replace(")", "").replace("-", "").replace("'", "").replace("é", "e").replace(".", "").replace("%", "").replace("+", "").replace(":", "").replace("#", "")

def removeduplicates(list):
    ans = []
    for item in list:
        if item not in ans:
            ans.append(item)
    return ans

def emojify(THEmessage, checkaliases=False):
    emojifiedmessage = THEmessage
    
    possibleemojis = re.findall(r"\[[^\[\]]*\]", THEmessage)
    possibleemojis = removeduplicates(possibleemojis)
    
    #for each of the strings that were in []
    for i in range(len(possibleemojis)):
        raw = possibleemojis[i][1:-1]
        #figure out the string that is trying to be emojified
        if checkaliases:
            try:
                emojiname = alias(raw)
            except:
                emojiname = raw
        else:
            emojiname = raw
        #replace it with the emoji if it exists
        try:
            emojifiedmessage = emojifiedmessage.replace("[{}]".format(raw), emojis[strippunctuation(emojiname.lower())])
        except KeyError:
            emojifiedmessage = emojifiedmessage.replace("[{}]".format(raw), raw)
    
    return emojifiedmessage

def currentweek():
    ERstarttime = datetime.datetime(settings.ERstartyear, settings.ERstartmonth, settings.ERstartday, settings.ERstarthour, tzinfo=pytz.utc)
    currenttime = datetime.datetime.now(tz=pytz.utc)
    td = currenttime - ERstarttime
    queryweek = ((td.days // 7) % 24) + 1
    return queryweek

def setup():
    koduck.addcommand("updatecommands", updatecommands, "prefix", 3)

setup()
koduck.client.run(settings.token)