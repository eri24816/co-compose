from co_compose import CoComposeServer, GenerateParams
import miditoolkit.midi.parser
import asyncio

class MyServer(CoComposeServer):

    async def generate(self, midi: miditoolkit.midi.parser.MidiFile, params: GenerateParams, cancel_event: asyncio.Event):
        # generate music here
        # yield the generated notes in the format of (onset, pitch, velocity, duration)
        for i in range(params.range.end - params.range.start):
            await asyncio.sleep(0.1)
            yield (params.range.start + i, 60 + i, 100, 1.0)

server = MyServer()
server.run('localhost', 8000)