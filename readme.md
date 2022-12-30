# Glymps API

Used for https://glymps.xyz

Rename .example.env to .env and set your `STEAM_API_KEY` from [here](https://steamcommunity.com/dev/apikey)

## Adding additional games

In `manualGames.json` follow this format:

```json
[
	{
		"name": "Red Dead Redemption 2",
		"image": "https://cdn.akamai.steamstatic.com/steam/apps/1174180/header.jpg?t=1618851907",
		"playtime_forever": 9720,
		"platform": "Stadia",
		"link": "https://stadia.google.com/store/details/2152a1e96d5b47b18a5df7ca9bb0751frcp1/sku/f790e37b6161477188923408085528a1"
	},
	{
		"name": "Minecraft",
		"image": "https://store-images.s-microsoft.com/image/apps.608.13510798887677013.5c7792f0-b887-4250-8c4e-4617af9c4509.bcd1385a-ad15-450c-9ddd-3ee80c37121a?mode=scale&q=90&h=1080&w=1920",
		"playtime_forever": 391920,
		"platform": "Estimated",
		"link": "https://minecraft.net"
	}
]
```
