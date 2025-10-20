# co-compose
A UI for co-creating music with AI

This repository is still a work in progress.

This repository contains two parts:
- `server`: A python server where you can run your own music generation model
- `ui`: A Vue UI that allows users to interact with the music generation model on a browser

## Usage

1. Build the ui (frontend):
```bash
cd ui
npm install
npm run build
```

2. Define the server by overriding the `generate` method:
```python
from music_gen_server import MusicGenServer, GenerateParams
import miditoolkit.midi.parser
import asyncio

class MyServer(MusicGenServer):

    async def generate(self, midi: miditoolkit.midi.parser.MidiFile, params: GenerateParams, cancel_event: asyncio.Event):
        # generate music here
        # yield the generated notes in the format of (onset, pitch, velocity, duration)
        for i in range(params.range.end - params.range.start):
            await asyncio.sleep(0.1)
            yield (params.range.start + i, 60 + i, 100, 1.0)

server = MyServer()
server.run('localhost', 8000)
```