# co-compose
A UI for co-creating music with AI.

This project is initially developed for [Segment-Factorized Full-Song Generation on Symbolic Piano Music](https://github.com/eri24816/segmented-full-song-gen) as a frontend for the proposed SFS model. However, it is designed to be easily adapted to other music generation models as backend.

The UI provides a piano roll editor where user and AI collaborate on music. Both user and AI can create and edit the musical content.

## Build frontend (run once before use)
```bash
cd ui
npm install
npm run build
```


## Using a custom backend

1. Install Python dependencies:
    ```bash
    pip install -e server
    ```

2. Wrap your music generation model in the `CoComposeServer.generate` method and run the server.

    The following example implements a "generation algorithm" that always generates a chromatic scale regardless of the surrounding context:
    ```python
    from co_compose import CoComposeServer, GenerateParams
    import miditoolkit.midi.parser
    import asyncio

    class MyServer(CoComposeServer):

        async def generate(self, midi: miditoolkit.midi.parser.MidiFile, params: GenerateParams, cancel_event: asyncio.Event):
            for i in range(params.range.end - params.range.start):
                yield (params.range.start + i, 60 + i, 100, 1.0) # (onset, pitch, velocity, duration)

    server = MyServer()
    server.run('localhost', 8000)
    ```

    The `generate` method expects you to implement a music infilling algorithm. 
    - `midi` is the current content on the piano roll.
    - `params.range` is the range to generate in beats.
    - `params.song_duration` is the total duration of the song in beats.
    - `params.segments` provides the form information of the song. It is used by the SFS model and can be ignored if your model does not use it.
    - `cancel_event` fires when the user cancels the current generation and you can return immediately.
    - The method should yield the generated notes in the format of (onset, pitch, velocity, duration). The yielded notes are streamed to the frontend in real-time. `onset` and `duration` are in beats.

## Using pretrained [Segment Full Song (SFS) model](https://github.com/eri24816/segmented-full-song-gen) as backend

1. Install the SFS model:
    ```bash
    pip install git+https://github.com/eri24816/segmented-full-song-gen.git
    ```

2. Download the [pretrained checkpoint](https://drive.google.com/file/d/1kisry4OwprXKMq4AlRqNlbBh8gRO9iZf/view?usp=drive_link) to the `sfs_server` directory.

4. Run the server:
    ```bash
    cd sfs_server
    python main.py
    ```

## UI Usage


### Structure Editor
Define your song structure, which serves as a condition for generation. The structure can be specified beforehand or adjusted during composition.

- Drag the left or right edge of a segment to resize it  
- Click a segment to assign its label

### Piano Roll
The workspace where users and AI collaborate on music. *Note that the seed segment should be composed prior to other segments.*

- Space bar: Toggle play  
- Click on empty space: Create a note  
- Drag: Move a note  
- Right-click: Delete a note  
- Scroll wheel: Pan  
- Control + scroll: Zoom

### Assets
Provides several 8-bar MIDI assets that users can drag into the piano roll.

- Drag assets into the piano roll as starting material or to combine with existing composition  
- Import additional assets from your disk  
- Click on an asset to preview it

### Bar Selection
Enables quick selection of one or multiple bars, which can then be used with the command palette.

### Command Palette
Click *Generate!* to let the AI generate content for the selected range, or use other buttons to perform different operations.