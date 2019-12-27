import subprocess
import os

from platform import python_version
from telegram import Update, Bot, Message, Chat
from telegram.ext import CommandHandler, run_async, Filters

from axel import dispatcher, OWNER_ID, SUDO_USERS
from axel.modules.helper_funcs.filters import CustomFilters
from axel.modules.disable import DisableAbleCommandHandler

def pingme():
    out = ""
    under = False
    if os.name == 'nt':
        output = subprocess.check_output("ping -n 1 1.0.0.1 | findstr time*", shell=True).decode()
        outS = output.splitlines()
        out = outS[0]
    else:
        out = subprocess.check_output("ping -c 1 1.0.0.1 | grep time=", shell=True).decode()
    splitOut = out.split(' ')
    stringtocut = ""
    for line in splitOut:
        if(line.startswith('time=') or line.startswith('time<')):
            stringtocut=line
            break
    newstra=stringtocut.split('=')
    if len(newstra) == 1:
        under = True
        newstra=stringtocut.split('<')
    newstr=""
    if os.name == 'nt':
        newstr=newstra[1].split('ms')
    else:
        newstr=newstra[1].split(' ') #redundant split, but to try and not break windows ping
    ping_time = float(newstr[0])
    return ping_time

@run_async
def status(bot: Bot, update: Update):
    pingSpeed = pingme()
    reply = "System Status: operational\n\n"
    reply += "Python version: "+python_version()+"\n"
    reply += "Ping speed: "+str(pingSpeed)+"ms\n"
    update.effective_message.reply_text(reply)


STATUS_HANDLER = CommandHandler("status", status, filters=CustomFilters.sudo_filter)

dispatcher.add_handler(STATUS_HANDLER)
