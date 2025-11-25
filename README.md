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

2. Install Python dependencies:
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
