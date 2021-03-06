#!/usr/bin/python
# -*- coding: utf-8 -*-
from ConfigParser import SafeConfigParser
from Crypto.Cipher import AES
from pkcs7 import *
from wckey import *
import StringIO
import gzip
import json
import sys
import base64
import urllib2
import zlib
import time
import cookielib
import random
import subprocess

DEBUG = False #False #True

ENABLE_PROXY = False #False #True
PROXY_SERVER = 'http://192.168.11.1:8080'

configFile = 'wc.conf'
config = SafeConfigParser()

false = False
true = True

wc_category = [  
  {'id': 1, 'weapon_name': '剣'},
  {'id': 2, 'weapon_name': '拳'},
  {'id': 3, 'weapon_name': '斧'},
  {'id': 4, 'weapon_name': '槍'},    
  {'id': 5, 'weapon_name': '弓'},    
  {'id': 6, 'weapon_name': '魔'},    
]

def wc_request(session,endpoint,data_original=None,debug=False):
  cookies = cookielib.CookieJar()
  if ENABLE_PROXY:
    proxy_handler = urllib2.ProxyHandler({"http" : PROXY_SERVER})
  else:
    proxy_handler = urllib2.ProxyHandler({})
  opener = urllib2.build_opener(proxy_handler,urllib2.HTTPCookieProcessor(cookies))
  
  if session is None:
    uh = None
    cookie = ''
  else:
    uh = session['uh']
    cookie = session['cookie']  

#  POST http://wcat.colopl.jp/ajax/regist/checkregister HTTP/1.1
  headers = { 
    'X-Unity-Version' : '4.5.0f6',
    'Content-Type' : 'application/x-www-form-urlencoded',
    'apv' : WC_APP_VERSION,
    'Cookie ' : cookie,
    'User-Agent' : 'Dalvik/1.6.0 (Linux; U; Android 4.4.4; C6806_GPe Build/KTU84P.S1)',
#    'Connection' : 'Keep-Alive',
    'Accept-Encoding' : 'gzip',
#    'Content-Length': '8'
    'Host' : 'wcat.colopl.jp',
  }
  if data_original is not None:
    data = 'data=' + quote(wc_encrypt(data_original,uh)) + '&' 
  else:
    data = ''
  data += 'app=wcat'
  url = 'http://wcat.colopl.jp/' + endpoint 
  req = urllib2.Request(url, data, headers)

  if data_original != None:
    text = 'endpoint: \'%s\', data: \'%s\'' % (endpoint,data_original)
  else:
    text = 'endpoint: \'%s\'' % endpoint
  print_color(text,"1;34")

  response = opener.open(req)
  
  for item in cookies:
    set_conf('cookie', item.name, item.value.rstrip('%3A1'))
    
  if response.info().get('Content-Encoding') == 'gzip':
    buf = StringIO.StringIO( response.read() )
    f = gzip.GzipFile(fileobj=buf)
    response_data = f.read()
  else:
    response_data = response.read()
  
  try:
    response_json = json.loads(zlib.decompress(wc_decrypt(response_data,uh)))
  except:
    print '\033[1;37;41m' + ' DECRYPT FALSE ' + '\033[m'
    return False
    
  if DEBUG or debug == True:
    print_color(response_json,"1;33")
  else:
    if response_json["error"] != 0:
      print_color(response_json,"1;31")
      
  return response_json
    
def get_conf(section,option):
  config.read(configFile)
  if not config.has_section(section): 
    return None
  elif not config.has_option(section, option):
    return None
  return config.get(section, option)
  
def set_conf(section,option,value):
  config.read(configFile)
  if not config.has_section(section): 
    config.add_section(section)
  config.set(section, option, value)
  fp = open(configFile, 'wb')
  config.write(fp)
  return config.get(section, option)
  
def quote(s, safe = ''):
  always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                 'abcdefghijklmnopqrstuvwxyz'
                 '0123456789' '_.-')
  safe = always_safe + safe
  if s == None:
    print 'WARRING: quote(s), s is not None!'
    return 'NONE'
  res = list(s)
  for i in range(len(res)):
    c = res[i]
    if c not in safe:
     res[i] = '%%%02x' % ord(c)
  return ''.join(res)

def wc_decrypt(secret_text, key_text = None, iv_text = None):
  if key_text is None:
    key_text = WC_APP_KEY
  if iv_text is None:
    iv_text = WC_APP_IV
  mode = AES.MODE_CBC
  cipher_text = base64.b64decode(secret_text)
  f = AES.new(key_text, mode, iv_text)
  padded_text = f.decrypt(cipher_text)
  encoder = PKCS7Encoder()
  return encoder.decode(padded_text)
  
def wc_encrypt(text, key_text = None, iv_text = None):
  if key_text is None:
    key_text = WC_APP_KEY
  if iv_text is None:
    iv_text = WC_APP_IV
  encoder = PKCS7Encoder()
  padded_text = encoder.encode(text)
  mode = AES.MODE_CBC
  f = AES.new(key_text, mode, iv_text)
  cipher_text = f.encrypt(padded_text)
  return base64.b64encode(cipher_text)

def generate_qt():
  import uuid
  return str(uuid.uuid4()).replace('-', '')
     
def print_color(target,color=33):
  if type(target) is dict:
    print '\033[0;' + str(color) + 'm' + json.dumps(target, ensure_ascii=False).encode('utf8').replace('\\"', '"').replace(', ', ',').replace(': ', ':') + '\033[m'
  else:
    print '\033[0;' + str(color) + 'm' + target + '\033[m'

def wc_load_session():
  session = {}
  session['cookie'] = 'wcatpt=' + get_conf('cookie','wcatpt').rstrip('%3A1') + '%3A1'
  session['uh'] = get_conf('device','uh')
  return session  


def func_send_google_forms(formsName, device_uuid, magic_stone, user_id, gachas, quest):
  import urllib2
  gachas_name = [
    'entry.2091703694',
    'entry.1009913173',
    'entry.1511949002',
    'entry.1364225177',
    'entry.835795136',
    'entry.53675612',
    'entry.1243528485',
    'entry.1614942825',
    'entry.1667097283',
    'entry.216898254',
  ]
  curlCommand = 'curl --compressed -k '
  curlCommand += '-d "entry.1502468719=' + quote(str(device_uuid)) + '&entry.1950034398=' + quote(str(magic_stone)) + '&entry.120539106=' + quote(str(user_id)) + '&entry.494056752=' + quote(str(quest))
  for n in range(0,len(gachas_name),1):
    if n < len(gachas):
      #print gachas[n]
      curlCommand += '&' + gachas_name[n] + '=' + quote(gachas[n])
  curlCommand += '" "https://docs.google.com/forms/d/' + formsName + '/formResponse" > /dev/null 2> /dev/null '
  subprocess.Popen(args=curlCommand, shell=True)
  
def func_list_to_string(ids):
  return str(ids).replace('u\'', '\"').replace('\'', '"').replace(' ', '')
      
def wc_quest_generate_complete(session,qid,did=0,fid=0,fcid=0,hard=0,debug=False):
  if fid == 0 and fcid == 0:
    quest_list_resp = wc_request(session,'ajax/quest/list', '{"wid":1,"aid":1,"hard":0}') 
    rand = random.randrange(0, len(quest_list_resp["result"]["friends"]), 1)
    fid = quest_list_resp["result"]["friends"][rand]["userInfo"]["id"]
    fcid = quest_list_resp["result"]["friends"][rand]["card"]["cId"]
  qt = generate_qt()
  quest_generate_resp = wc_request(session,'ajax/quest/generate', '{"qt":"' + str(qt) + '","qid":' + str(qid) + ',"did":' + str(did) + ',"fid":' + str(fid) + ',"fcid":' + str(fcid) + ',"hard":' + str(hard) + '}')
 
  itemIds = []
  weaponIds = []
  ornamentIds = []
  cardIds = []
  destroyEnemyIds = []
  destroyObjectIds = []  
  openTreasureIds = []   
  gold = 0
  exp = 0
  
  for stageData in quest_generate_resp["result"]["stageDatas"]:
    #print_color(stageData,"1;36")
    if stageData.has_key('stageEnemyParams'):
      stageData['stageEnemyParams']
    if stageData.has_key('stageEnemies'):
      for stageEnemie in stageData["stageEnemies"]:
        if stageEnemie.has_key('itemId'):
          itemIds.append(stageEnemie["itemId"])
        if stageEnemie.has_key('weaponId'):
          weaponIds.append(stageEnemie["weaponId"])
        if stageEnemie.has_key('cardId'):
          cardIds.append(stageEnemie["cardId"])
        destroyEnemyIds.append(stageEnemie["id"])
        for stageEnemyParam in stageData['stageEnemyParams']:
          if stageEnemyParam["smonId"] == stageEnemie["smonId"]:
            gold += stageEnemyParam["gold"]
            exp += stageEnemyParam["exp"]
    if stageData.has_key('stageTreasures'):
      for stageTreasure in stageData["stageTreasures"]:
        if stageTreasure["dropId"] != 8 and stageTreasure["dropId"] != 2: 
          print_color(stageTreasure)
        if stageTreasure["dropId"] == 2: 
          gold += stageTreasure["dropNum"]
        elif stageTreasure["dropId"] == 8:    
          itemIds.append(stageTreasure["itemId"])
        #elif stageTreasure["dropId"] == 6:    
        #  weaponIds.append(stageTreasure["weaponId"])
        openTreasureIds.append(stageTreasure["id"])
  
  itemIdsString = ""
  for itemId in itemIds:
    if itemId % 100 == 30:
      itemIdsString += '\033[1;31m' + str(itemId) + '\033[m' + ","
    else:
      itemIdsString += str(itemId) + ","
    
  if debug:
    print "gold            : " + str(gold)
    print "soul            : " + str(exp)
    print "cardIds         : " + func_list_to_string(cardIds).lstrip('[').rstrip(']')
    print "weaponIds       : " + func_list_to_string(weaponIds).lstrip('[').rstrip(']')
    print "ornamentIds     : " + func_list_to_string(ornamentIds).lstrip('[').rstrip(']')
    print "itemIds         : " + itemIdsString.rstrip(',') #func_list_to_string(itemIds).lstrip('[').rstrip(']')
    print "destroyEnemyIds : " + func_list_to_string(destroyEnemyIds).lstrip('[').rstrip(']')
    print "destroyObjectIds: " + func_list_to_string(destroyObjectIds).lstrip('[').rstrip(']')
    print "openTreasureIds : " + func_list_to_string(openTreasureIds).lstrip('[').rstrip(']')
  time.sleep(10)
    
  return wc_request(session,'ajax/quest/complete', '{"qt":"' + quest_generate_resp["result"]["qt"] + '","gold":' + str(gold) + ',"soul":' + str(exp) + ',"cardIds":' + func_list_to_string(cardIds) + ',"weaponIds":' + func_list_to_string(weaponIds) + ',"ornamentIds":[],"itemIds":' + func_list_to_string(itemIds) + ',"destroyEnemyIds":' + func_list_to_string(destroyEnemyIds) + ',"destroyObjectIds":[],"openTreasureIds":' + func_list_to_string(openTreasureIds) + ',"totalDamageCount":0,"totalDamageAmount":0,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":0,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')     

def wc_regist_checkregister_resp(session):
  return wc_request(session,'ajax/regist/checkregister', None)             

def wc_receive(session):
  while True:
    presents_resp = wc_request(session,'ajax/present/list', '{"page":0}')
    ids = []
    for present in presents_resp["result"]["userPresents"]:
      ids.append(present["id"])
    if ids == []:
      break
    receive_resp = wc_request(session,'ajax/present/receive', '{"ids":' + func_list_to_string(ids) + '}')

def func_daily(formsName,cookie_uh):
  #formsName = '1gRXqjsvXoaFyZfxJHJncCjk96L1NDL5-gNs-8t5-D3Y'
  set_conf('device', 'uh', cookie_uh.split(',')[1])
  set_conf('cookie', 'wcatpt', cookie_uh.split(',')[0])
  session = wc_load_session()
  if wc_request(session,'ajax/user/loginbonus', None) == False:
    return False
  wc_receive(session)
  regist_checkregister_resp = wc_request(session,'ajax/regist/checkregister', None)
  characters = []
  for card in regist_checkregister_resp["result"]["cards"]:
    #print "%dS%s %s%s" % (card["rar"],func_select('id',card["weaponId"],wc_category)['weapon_name'],card["preName"].encode('utf-8'),card["name"].encode('utf-8'))
    if card["rar"] >= 2:
      characters.append( "%dS%s %s%s" % (card["rar"],func_select('id',card["weaponId"],wc_category)['weapon_name'],card["preName"].encode('utf-8'),card["name"].encode('utf-8')) )
  characters = sorted(characters, reverse=True)
  weapons = []
  for weapon in regist_checkregister_resp["result"]["weapons"]:
    #print "%dS%s %s" % (weapon["rar"],func_select('id',weapon["category"],wc_category)['weapon_name'],weapon["name"].encode('utf-8'))
    weapons.append( "%dS%s %s" % (weapon["rar"],func_select('id',weapon["category"],wc_category)['weapon_name'],weapon["name"].encode('utf-8')) )
  weapons = sorted(weapons, reverse=True)    
  func_send_google_forms(formsName, session['cookie'].lstrip('wcatpt=').rstrip('%3A1') + ',' + session['uh'], regist_checkregister_resp["result"]["userStatus"]["crystal"], regist_checkregister_resp["result"]["userInfo"]["inviteCode"], characters, weapons[0])

  return True

def wc_units(session):
  if wc_request(session,'ajax/user/loginbonus', None) == False:
    return False
  regist_checkregister_resp = wc_request(session,'ajax/regist/checkregister', None)
  for card in regist_checkregister_resp["result"]["cards"]:
    print "%dS%s %s%s" % (card["rar"],func_select('id',card["weaponId"],wc_category)['weapon_name'],card["preName"].encode('utf-8'),card["name"].encode('utf-8'))
  for weapon in regist_checkregister_resp["result"]["weapons"]:
    print "%dS%s %s" % (weapon["rar"],func_select('id',weapon["category"],wc_category)['weapon_name'],weapon["name"].encode('utf-8'))

def func_daily_main(daily_configFile, function = 'update'):
  import time
  daily_config = SafeConfigParser()
  daily_config.optionxform = str
  daily_config.read(daily_configFile)
  accountList = daily_config.items('account')
  loop = daily_config.get('round', 'loop')
  loop_max = daily_config.get('round', 'loop_max')
  return_url = daily_config.get('round', 'return_url')
  if function == 'update':
    #print loop_max
    #print loop
    if int(loop) < int(loop_max):
      for accountItem in accountList:
        account = accountItem[0] 
        if int(accountItem[1]) <= int(loop):
          print '\033[1;33m' 'ROUND %s ' % accountItem[1]  + account + '\033[m'
          if int(loop) - int(accountItem[1]) > 1:
            print '\033[1;31m' 'warring - loop number is too large' + '\033[m'
          res = func_daily(return_url, account)
          if res == True:
            daily_config.set('account', account, str(int(accountItem[1])+1))
            fp = open(daily_configFile, 'wb')
            daily_config.write(fp)
          else:
            daily_config.set('account', account, '8591')
            fp = open(daily_configFile, 'wb')
            daily_config.write(fp)
        #else:
          print '\033[1;33m' 'ROUND %s ' % accountItem[1]  + account + '\033[m'      
          #print '\033[1;33m' + 'SKIP\n' + '\033[m'          
      daily_config.set('round', 'loop', str(int(loop)+1))
      fp = open(daily_configFile, 'wb')
      daily_config.write(fp)
    else:
      print '=== DAILY END ==='
      time.sleep(86400)
  elif function == 'day':
    daily_config.set('round', 'loop_max', str(int(loop_max)+1))
    fp = open(daily_configFile, 'wb')
    daily_config.write(fp) 


def func_select(where_title,where_value,from_table):
  for row in from_table:
    if row[where_title] == where_value:
      return row
  return None
    
def main():
  if not len(sys.argv) >= 2:
    return
    
  elif sys.argv[1] == 'decrypt' or sys.argv[1] == 'de':
    if not len(sys.argv) >= 2:
      print 'wc decrypt [data] [uh]'
      return
    if len(sys.argv) >= 4:
      uh = sys.argv[3]
    else:
      uh = None
    #print uh
    res = sys.argv[2].find('app=wcat')
    if res == -1:
      text = wc_decrypt(sys.argv[2],uh)
    else:
      tempArray = sys.argv[2].split('&')
      raw = ''
      for temp in tempArray:
        res = temp.find('data')
        if res >= 0:
          target = urllib2.unquote(temp.split('=')[1])
          text = wc_decrypt(target,uh)
          break  
    try:
      text2 = json.loads( zlib.decompress(text) ) 
    except:
      text2 = text
    print_color(text2)

  elif sys.argv[1] == 'takeover' or sys.argv[1] == 'ta':
    session = wc_load_session()
    if not len(sys.argv) >= 3:
      emailaddr = str(wc_regist_checkregister_resp(session)["result"]["userId"]) + '@wcat.co.jp'
    else:
      emailaddr = sys.argv[2]
    print '{"email":"' + emailaddr + '","password":"1234qwer","confirmPassword":"1234qwer","secretQuestionType":7,"secretQuestionAnswer":"kawasaki"}'
    print_color(wc_request(session,'ajax/regist/createwcataccount','{"email":"' + emailaddr + '","password":"1234qwer","confirmPassword":"1234qwer","secretQuestionType":7,"secretQuestionAnswer":"kawasaki"}'))
    
  elif sys.argv[1] == 'tutorial' or sys.argv[1] == 'tu':
    inviteCode = "CBWP2M7BP"
    
    resp = wc_request(None,'ajax/regist/create', '{"d":"b0edac6f610d2fda75e2c8763372f8b3b24a39e97b2bdf69e2eccbda1e250fb37e96b91d6e81612b0e576c113366186a","fromCode":"","fromParam":"","fromAffiliate":""}')
    set_conf('device', 'uh', resp["result"]["uh"])
    
    #custom_uh = "6e750540d57ed37bed323a082f18e1a1"
    #custom_cookie = "74fGSqsfX7RsQRerg5TaSVJkTWpglF6AcO298HlbWaLvJrGHBO_mzz3Y7MuvWku966NSHdST8UAipf4BfZ3kdjdFb1NXHmuv%3A1"
    #set_conf('device', 'uh', custom_uh)
    #set_conf('cookie', 'wcatpt', custom_cookie.rstrip('%3A1'))
    
    session = wc_load_session()
    
    print_color(session)
    
    if wc_request(session,'ajax/assetbundle/version', None) == False:
      exit()
    wc_request(session,'ajax/deck/defaultweapon', None)
    wc_request(session,'ajax/quest/getdream', None)
    
    wc_request(session,'ajax/quest/generate','{"qt":"' + generate_qt() + '","qid":9999999,"did":0,"fid":6877844,"fcid":10100440,"hard":0}') 
    
    quest_list_resp = wc_request(session,'ajax/quest/list', '{"wid":1,"aid":1,"hard":0}') 
    
    wc_quest_generate_complete(session,1,0,1,10400010,0)
    #qt = generate_qt()
    #wc_request(session,'ajax/quest/generate','{"qt":"' + qt + '","qid":1,"did":0,"fid":1,"fcid":10400010,"hard":0}')
    #time.sleep(10)
    #wc_request(session,'ajax/quest/complete', '{"qt":"' + qt + '","gold":324,"soul":23,"cardIds":[],"weaponIds":[],"ornamentIds":[],"itemIds":[100110,100110,100110],"destroyEnemyIds":[1,2,3,6,4,5,8,7,12,10,11,13,9,14],"destroyObjectIds":[],"openTreasureIds":[1,2],"totalDamageCount":3,"totalDamageAmount":5,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":0,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')
    
    wc_request(session,'ajax/user/updatename', '{"name":"カオル"}')
    wc_request(session,'ajax/quest/talkread', '{"qid":1,"baType":1,"hard":0}')
    wc_request(session,'ajax/quest/talkread', '{"qid":2,"baType":0,"hard":0}')

    wc_quest_generate_complete(session,2,0,0,0,0)    
    #qt = generate_qt()
    #wc_request(session,'ajax/quest/generate', '{"qt":"' + qt + '","qid":2,"did":0,"fid":2325920,"fcid":20600000,"hard":0}')
    #time.sleep(10)
    #wc_request(session,'ajax/quest/complete', '{"qt":"' + qt + '","gold":343,"soul":22,"cardIds":[],"weaponIds":[],"ornamentIds":[],"itemIds":[100110,100310],"destroyEnemyIds":[16,17,21,23,19,20,18,22,15,24,30,25,27,29,26,28,32,33,31,34],"destroyObjectIds":[],"openTreasureIds":[3],"totalDamageCount":5,"totalDamageAmount":20,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":0,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')
    
    wc_quest_generate_complete(session,3,0,0,0,0)    
    #qt = generate_qt()
    #wc_request(session,'ajax/quest/generate', '{"qt":"' + qt + '","qid":3,"did":0,"fid":2762707,"fcid":10100000,"hard":0}')
    #time.sleep(10)
    #wc_request(session,'ajax/quest/complete', '{"qt":"' + qt + '","gold":479,"soul":28,"cardIds":[],"weaponIds":[],"ornamentIds":[],"itemIds":[100610,100110,100110,100110,100410,100110,100410],"destroyEnemyIds":[36,44,40,41,39,43,42,37,38,45,46,53,54,52,47,49,51,50,48,57,56,55,60,61,59,58],"destroyObjectIds":[],"openTreasureIds":[4,5],"totalDamageCount":17,"totalDamageAmount":95,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":0,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')
    
    wc_request(session,'ajax/quest/talkread', '{"qid":2,"baType":1,"hard":0}')   
    wc_request(session,'ajax/quest/talkread', '{"qid":3,"baType":1,"hard":0}')
    
    weapon1_resp = wc_request(session,'ajax/gacha/weaponexe', '{"gId":100,"nowCrystal":0}')
    print_color(weapon1_resp,"1;32")
    wc_request(session,'ajax/deck/compoweapon', '{"uwId":"' + str(weapon1_resp["result"]["weapon"]["uwId"]) + '"}')
    
    wc_quest_generate_complete(session,108,0,0,0,0)    
    #qt = generate_qt() 
    #wc_request(session,'ajax/quest/generate', '{"qt":"' + qt + '","qid":108,"did":0,"fid":2781705,"fcid":10100000,"hard":0}')
    #time.sleep(10)
    #wc_request(session,'ajax/quest/complete', '{"qt":"' + qt + '","gold":593,"soul":39,"cardIds":[],"weaponIds":[],"ornamentIds":[],"itemIds":[100110,100110,100110,100110,100510,100410,100110,100110,100410,100410],"destroyEnemyIds":[2944,2947,2950,2952,2949,2953,2946,2951,2945,2954,2948,2955,2959,2958,2957,2963,2956,2962,2961,2964,2965,2960,2970,2969,2968,2967,2966,2975,2974,2971,2972,2973],"destroyObjectIds":[],"openTreasureIds":[275,277,276],"totalDamageCount":17,"totalDamageAmount":91,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":0,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')
    
    gacha1_resp = wc_request(session,'ajax/gacha/exe', '{"id":100,"nowCrystal":0}')
    print_color(gacha1_resp, '1;32')
    
    alllist_resp = wc_request(session,'ajax/deck/alllist', None)     
    wc_request(session,'ajax/deck/updatedeck','{"dn":0,"ueid0":"' + str(alllist_resp["result"]["cards"][1]['ucId']) + '","ueid1":"' + str(alllist_resp["result"]["cards"][0]['ucId']) + '","ueid2":"-1","ueid3":"-1"}')
    
    wc_request(session,'ajax/quest/talkread', '{"qid":5,"baType":0,"hard":0}')	
    
    wc_quest_generate_complete(session,5,0,0,0,0)    
    #qt = generate_qt() 
    #wc_request(session,'ajax/quest/generate', '{"qt":"' + qt + '","qid":5,"did":0,"fid":5061559,"fcid":20100060,"hard":0}')
    #time.sleep(10)
    #wc_request(session,'ajax/quest/complete', '{"qt":"' + qt + '","gold":635,"soul":63,"cardIds":[],"weaponIds":[],"ornamentIds":[],"itemIds":[100410,100110,100110,100410,100110,100110],"destroyEnemyIds":[62,64,63,67,65,66,70,69,68,72,71,74,73,76,75,78,77,79,81,80,82],"destroyObjectIds":[],"openTreasureIds":[6,7],"totalDamageCount":14,"totalDamageAmount":76,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":1,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')
    
    wc_request(session,'ajax/quest/talkread', '{"qid":5,"baType":1,"hard":0}')
    wc_request(session,'ajax/quest/talkread', '{"qid":109,"baType":0,"hard":0}')
    
    wc_quest_generate_complete(session,109,0,1,10400010,0)    
    #qt = generate_qt() 
    #wc_request(session,'ajax/quest/generate', '{"qt":"' + qt + '","qid":109,"did":0,"fid":1,"fcid":10400010,"hard":0}')
    #time.sleep(10)
    #wc_request(session,'ajax/quest/complete', '{"qt":"' + qt + '","gold":981,"soul":89,"cardIds":[],"weaponIds":[],"ornamentIds":[],"itemIds":[100610,100610,100110,100610,100610,100610,100610,100210,100610,100610,100610,100610,100610,100210,100110,100120],"destroyEnemyIds":[2976,2978,2979,2980,2981,2982,2977,2984,2983,2986,2987,2985,2993,2992,2989,2990,2991,2988,3005],"destroyObjectIds":[],"openTreasureIds":[278,279,280,281,282],"totalDamageCount":25,"totalDamageAmount":102,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":3,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}')
    
    wc_request(session,'ajax/quest/talkread', '{"qid":109,"baType":1,"hard":0}')

    wc_request(session,'ajax/city/info', None)
    build_resp = wc_request(session,'ajax/city/build', '{"path":"ajax/city/build","bId":18,"posX":17,"posZ":27}')
    time.sleep(5)    
    wc_request(session,'ajax/city/complete', '{"path":"ajax/city/complete","ubId":' + str(build_resp["result"]["ubId"]) + ',"bUseCrystal":0,"nowCrystal":0}')
    wc_request(session,'ajax/quest/list', '{"wid":1,"aid":1,"hard":0}')
    wc_request(session,'ajax/world/list', None)
    wc_request(session,'ajax/area/list', '{"wid":1}')
    wc_request(session,'ajax/quest/list', '{"wid":1,"aid":2,"hard":0}')
    
    wc_request(session,'ajax/quest/talkread', '{"qid":7,"baType":0,"hard":0}')
    wc_request(session,'ajax/quest/talkread', '{"qid":1,"baType":0,"hard":1}')
    
    inputinvitecode_resp = wc_request(session,'ajax/user/inputinvitecode', '{"URL":"ajax/user/inputinvitecode","inviteCode":"' + inviteCode + '"}')
    print_color(inputinvitecode_resp)
    wc_request(session,'ajax/user/loginbonus', None)
    wc_receive(session)
    crystal = receive_resp["result"]["userStatus"]["crystal"]
    print 'crystal: ' + str(crystal)
    gacha2_resp = wc_request(session,'ajax/gacha/exe', '{"id":2,"nowCrystal":' + str(crystal) + '}')
    print_color(gacha2_resp, '1;32')
    gacha3_resp = wc_request(session,'ajax/gacha/exe', '{"id":2,"nowCrystal":' + str(crystal-25) + '}')
    print_color(gacha3_resp, '1;32') 

    weapon2_resp = wc_request(session,'ajax/gacha/weaponexe', '{"gId":1,"nowCrystal":' + str(crystal-50) + '}')
    print_color(weapon2_resp,"1;32")	
    
    func_daily('15nmwq0piVOrjDWV67DPbczdHAnIXYXwcUOqxjsldJXs', session['cookie'].lstrip('wcatpt=').rstrip('%3A1') + ',' + session['uh'])
    
  elif sys.argv[1] == 'test' or sys.argv[1] == 'te':
    session = wc_load_session()
    #wc_quest_generate_complete(session,10022,0,0,0,1,True)
    #wc_quest_generate_complete(session,10023,0,0,0,1,True)
    #wc_quest_generate_complete(session,10024,0,0,0,1,True)
    #wc_quest_generate_complete(session,10046,0,0,0,1,True)
    #wc_quest_generate_complete(session,10026,0,0,0,1,True)

    #wc_quest_generate_complete(session,10057,0,0,0,0,True)
    #wc_quest_generate_complete(session,10058,0,0,0,0,True)
    #wc_quest_generate_complete(session,10059,0,0,0,0,True)
    #wc_quest_generate_complete(session,10060,0,0,0,0,True)
    #wc_quest_generate_complete(session,10061,0,0,0,0,True)
    
    #wc_quest_generate_complete(session,10062,0,0,0,0,True)
    #wc_quest_generate_complete(session,10063,0,0,0,0,True)
    #wc_quest_generate_complete(session,10064,0,0,0,0,True)
    #wc_quest_generate_complete(session,10065,0,0,0,0,True)
    #wc_quest_generate_complete(session,10066,0,0,0,0,True)
    
    wc_quest_generate_complete(session,10078,0,0,0,0,True)
    wc_quest_generate_complete(session,10079,0,0,0,0,True)
    wc_quest_generate_complete(session,10080,0,0,0,0,True)
    wc_quest_generate_complete(session,10081,0,0,0,0,True)
    wc_quest_generate_complete(session,10082,0,0,0,0,True)
   
    #wc_quest_generate_complete(session,10007,0,0,0,0,True)
    #wc_quest_generate_complete(session,10008,0,0,0,0,True)
    #wc_quest_generate_complete(session,10009,0,0,0,0,True)
    #wc_quest_generate_complete(session,10033,0,0,0,0,True)
    #wc_quest_generate_complete(session,10041,0,0,0,0,True)
    
  elif sys.argv[1] == 'daily':
    func_daily_main(sys.argv[2],sys.argv[3])
    
  elif sys.argv[1] == 'cookie_uh' or sys.argv[1] == 'cu':
    cookie_uh = sys.argv[2]
    set_conf('device', 'uh', cookie_uh.split(',')[1])
    set_conf('cookie', 'wcatpt', cookie_uh.split(',')[0])
    session = wc_load_session()
    wc_request(session,'ajax/assetbundle/version', None)
    
  elif sys.argv[1] == 'units' or sys.argv[1] == 'un':
    session = wc_load_session()
    wc_units(session)
    
  elif sys.argv[1] == 'quest' or sys.argv[1] == 'qe':
    session = wc_load_session()
    wc_quest_generate_complete(session,int(sys.argv[2]),0,0,0,0,True)
                      
  elif sys.argv[1] == 'eventlist' or sys.argv[1] == 'ev':
    session = wc_load_session()
    quest_eventlist = wc_request(session,'ajax/quest/eventlist', None)
    for event in quest_eventlist["result"]["events"]:
      print event["name"] + " (" + event["limitTimeInfo"] + ")" #event["locationId"] + " - " + 
      for quest in quest_eventlist["result"]["quests"]:
        if event["locationId"] == quest["locationId"]:
          print "  " + str(quest["questId"]) + " - " + quest["name"]
      print 
  elif sys.argv[1] == 'demo': 
    session = wc_load_session()
    wc_request(session,'ajax/quest/complete','{"qt":"a4a98989498f45948ad1618edaeddb76","gold":6367,"soul":626,"cardIds":[],"weaponIds":[100330],"ornamentIds":[],"itemIds":[100410,100610,100410,100410,100310,100320,100410,100410,100510,100410,100410,100420,100320,100420,100410,100610,100430,100620,100410,100310,100510,100510,100420,100420],"destroyEnemyIds":[7865,7866,7867,7868,7869,7870,7871,7872,7873,7874,7875,7876,7877,7878,7879,7880,7881,7882,7883,7884,7885,7886,7887,7888,7889,7890,7891,7892,7893,7894,7895,7896,7897,7898,7899,7900,7901,7902,7903,7904,7905,7906,7907,7908],"destroyObjectIds":[],"openTreasureIds":[617,618,619,620,621,622,623],"totalDamageCount":0,"totalDamageAmount":0,"totalDamageCountFromPlacementObject":0,"totalDeadCount":0,"totalHelperDeadCount":0,"totalBadStatusCount":0,"totalActionSkillUseCount":0,"totalAllAttackUseCount":0,"isDestroyBossAtActionSkill":false,"isDestroyBossAtAllAttack":false,"maxChainNum":0,"routeId":0}',True)

    
  elif sys.argv[1] == 'recv' or sys.argv[1] == 're':
    session = wc_load_session()
    wc_receive(session)
    
if __name__ == "__main__":
  main()
