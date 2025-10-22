import asyncio
import threading
import traceback
from typing import cast
from music_data_analysis import Pianoroll
from co_compose import CoComposeServer, GenerateParams
import safetensors.torch
import miditoolkit.midi.parser
from segment_full_song import SegmentFullSongModel, create_model

class MyQueue(asyncio.Queue):
    def __init__(self):
        super().__init__()
        self.eventloop = asyncio.get_event_loop()

    def __aiter__(self):
        return self

    def put_nowait(self, item):
        self.eventloop.call_soon_threadsafe(super().put_nowait, item)

    async def get(self):
        return await super().get()

    async def __anext__(self):
        item = await self.get()
        if item is None:
            raise StopAsyncIteration
        return item

class SegmentFullSongServer(CoComposeServer):
    def __init__(self, device="cuda"):
        super().__init__()
        print('creating model')
        self.model = cast(SegmentFullSongModel,create_model('segment_full_song.yaml'))
        print('loading model')
        self.model.load_state_dict(safetensors.torch.load_file('epoch=384-step=2000000.safetensors'))
        self.model.eval() 
        self.model.to(device)
        print('model loaded')

    async def generate(self, midi: miditoolkit.midi.parser.MidiFile, params: GenerateParams, cancel_event: asyncio.Event):
        frames_per_beat = 8
        beats_per_bar = 4
        pr = Pianoroll.from_midi(midi, frames_per_beat=frames_per_beat, beats_per_bar=beats_per_bar)
        pr.duration=params.song_duration * frames_per_beat

        segments = []
        for segment in params.segments:
            segments.append({
                "start_bar": segment.start // beats_per_bar,
                "end_bar": segment.end // beats_per_bar,
                "label": segment.label,
                "is_seed": segment.is_seed,
            })

        seed_start_bar = None
        for segment in segments:
            if segment["is_seed"]:
                seed_start_bar = segment["start_bar"]
                break


        generate_note_queue = MyQueue()
        def generate_note_callback(note: tuple[int, int, int, int]):
            onset, pitch, velocity, duration = note
            generate_note_queue.put_nowait((onset / frames_per_beat, pitch, velocity, duration / frames_per_beat))
 
        def inference_thread_task():
            try: 
                self.model.generate(segments, existing_pianoroll=pr, target_start_bar=params.range.start // beats_per_bar, target_end_bar=params.range.end // beats_per_bar, generate_note_callback=generate_note_callback, seed_start_bar=seed_start_bar,top_p=0.975)

            except Exception:
                traceback.print_exc()

            generate_note_queue.put_nowait(None)
        threading.Thread(target=inference_thread_task).start()

        async for note in generate_note_queue:
            if note is None:
                break
            yield note
            if cancel_event.is_set():
                print("cancelling generation")
                break


server = SegmentFullSongServer()
app = server.get_app()


if __name__ == "__main__":
    server.run()

# usage: either one of
# python main.py
# uvicorn main:app