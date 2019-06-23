import arrow
import aiohttp
import aiocron
from aiohttp import web

records = { }

session = aiohttp.ClientSession()

@aiocron.crontab('*/15 * * * *')
async def crawl():
    async with session.post('http://booking.tpsc.sporetrofit.com/Home/loadLocationPeopleNum') as resp:
        data = await resp.json()
        for center in data['locationPeopleNums']:
            name = center['LID']
            now = arrow.get().to('Asia/Taipei').format('YYYY-MM-DDTHH:mm:ssZ')
            if name in records:
                records[name]['gym' ][now] = int(center['gymPeopleNum'])
                records[name]['pool'][now] = int(center['swPeopleNum' ])
            else:
                records[name] = { 'gym': { now: int(center['gymPeopleNum']) }, 'pool': { now:  int(center['swPeopleNum']) } }

async def prepare(request):
    name, type = request.query['name'], request.query['type']
    stats = { }
    for key in records[name][type]:
        if key[11:13] in stats:
            stats[key[11:13]] += [records[name][type][key]]
        else:
            stats[key[11:13]] = [records[name][type][key]]
    for key in stats:
        stats[key] = (lambda x: round(sum(x) / len(x), 2))(stats[key])
    return web.json_response(data=stats)

app = web.Application()
app.add_routes([
    web.get('/prepare', prepare)
])
web.run_app(app, port=5000)
