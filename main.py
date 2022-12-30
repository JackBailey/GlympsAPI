import os, json, logging, requests, threading, time,datetime

from flask import Flask, render_template, jsonify, request, send_file
from gevent.pywsgi import WSGIServer
from flask_cors import CORS
import sys, os
from PIL import Image
import os
import mimetypes
import string
from hurry.filesize import size
from dotenv import load_dotenv

load_dotenv()

print(os.environ.get("STEAM_API_KEY"))

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

startingImages = 0
endingImages = 0
#sorted(data.values(), key=itemgetter(name))

def diff(before,after):
	return str(size(before)) + " => " + str(size(after)) + " (" + str(round(((before - after)/before)*100,1)) + "%) " 

def imgConv(url, game):
	global startingImages, endingImages
	directory = "img/"
	response = requests.get(url)
	img_data = response.content
	content_type = response.headers['content-type']
	extension = mimetypes.guess_extension(content_type)
	allowedChars = [str(c) for c in range(0,9)] + list(string.ascii_lowercase)
	name = ""
	for char in game:
		if char == " ":
			name += "_"
		elif char.lower() not in allowedChars:
			name += ""
		else:
			name += char
	imgIn = directory + name + extension
	with open(imgIn, 'wb') as handler:
		handler.write(img_data)

	before = os.path.getsize(imgIn)
	startingImages += before
	## Compress + Reduce image
	image = Image.open(imgIn)
	image.thumbnail((860, 300)) # Resize
	image = image.convert('RGB') # Convert to webp
	output = directory + name + ".webp"
	image.save(output, 'webp',optimize=True,quality=60,subsampling=0) # compress
	after = os.path.getsize(output)
	endingImages += after
	#print(diff(before,after)," - ", str(name))
	os.remove(imgIn)

	return "https://api.glymps.xyz/"+ directory + name


def pretty(jsonIn):
		return json.dumps(jsonIn, indent=1, sort_keys=True)

def background():
	print("***** RAN *******")


	while True:
		timeStart = datetime.datetime.now()
		#### CONFIG

		gamesToList = 80 ## Default if it isn't specified
		steamID = 76561198363384787

		####

		gamesToList += 1
		
		url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=" + os.environ.get("STEAM_API_KEY") + f"&steamid={steamID}&format=json"
		r = requests.get(url)
		dictResult = json.loads(r.text)["response"]["games"]
		
		with open('manualGames.json') as json_file:
			manualGames = json.load(json_file)

		with open('cache.json') as json_file:
			cache = json.load(json_file)

		for game in manualGames:
			dictResult.append(game)

		sort = sorted(dictResult, key=lambda k: k['playtime_forever'])
		gameData = []
		gameList = sort[:gamesToList*-1:-1]

		for item in range(len(gameList)):
			try:
				currentGame = gameList[item]
				try:
					platform = currentGame["platform"]
				except:
					platform = "steam"
				if platform == "steam":
					with open('steamstore.json') as json_file:
						data = json.load(json_file)
					try:
						gameInfo = data[str(currentGame["appid"])]
					except Exception as e:
						
						print("New Game, adding to database")
						url = "https://api.jackbailey.uk/steamstore/"+str(currentGame["appid"])
						r = requests.get(url)
						gameInfo = r.json()["data"]
						#print(int(currentGame["appid"]))

						data[int(currentGame["appid"])] = gameInfo

						try:
							with open("steamstore.json", "w") as outfile: 
								
								json.dump(data, outfile)
						except Exception as e:
							exc_type, exc_obj, exc_tb = sys.exc_info()
							fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
							print(exc_type, fname, exc_tb.tb_lineno)

					### Download + add new image

					outputImage = imgConv(gameInfo["header_image"],gameInfo["name"])


					newGame = {
						"name":gameInfo["name"],
						"image":outputImage,
						"playtime_forever": currentGame["playtime_forever"],
						"platform": "Steam",
						"link":"https://store.steampowered.com/app/"+ str(currentGame["appid"])
					}

				else:
					
					outputImage = imgConv(currentGame["image"],currentGame["name"])
					newGame = {
						"name": currentGame["name"],
						"image": outputImage,
						"playtime_forever": currentGame["playtime_forever"],
						"platform": currentGame["platform"],
						"link":currentGame["link"]
					}
				gameData.append(newGame)
				name = newGame["name"]
				#print(f" {name}")
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)


		with open("cache.json", "w") as outfile: 
			json.dump(gameData, outfile)

		#print(diff(startingImages,endingImages))
		timeEnd = datetime.datetime.now()
		time.sleep(900)

def flaskBG():
	app = Flask('app')
	CORS(app)

	@app.route('/')
	def index():
		return render_template("index.html")

	@app.route("/top<path:path>games")
	def topgames(path):
		with open('cache.json') as json_file:
			data = json.load(json_file)
		response = jsonify(data[0:int(path)])
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response

	@app.route("/img/<path:path>")
	def img(path):
		path = "img/" + path
		filetype = mimetypes.guess_type(path)[1] 
		return send_file(path + ".webp", mimetype='filetype')	

	@app.route("/topgames")
	def defaulttopgames():
		with open('cache.json') as json_file:
			data = json.load(json_file)
		response = jsonify(data[0:10])
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response

	@app.route("/totalhours")
	def totalHours():
		with open('cache.json') as json_file:
			data = json.load(json_file)
		jsonData = {
			"minutes":0,
			"hours":0,
		}
		for game in data:
			jsonData["minutes"] += game["playtime_forever"]

		jsonData["hours"] = round(jsonData["minutes"]/60)
		
		response = jsonify(jsonData)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response

	http_server = WSGIServer(('', 5000), app)
	http_server.serve_forever()


b = threading.Thread(name='background', target=background)
f = threading.Thread(name='flaskBG', target=flaskBG)
cli = threading.Thread(name='cli', target=cli)


b.start()
f.start()
cli.start()