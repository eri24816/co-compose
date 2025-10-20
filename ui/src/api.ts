import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

type RangeToGenerate = {
  start: number;
  end: number;
};

type SegmentInfo = {
  start: number;
  end: number;
  label: string;
};

type GenerateParams = {
  range: RangeToGenerate;
  segments: SegmentInfo[];
  song_duration: number;
}

const clientId = uuidv4();

/**
 * Generates a new MIDI file from an existing one.
 * @param midiFile - The MIDI file to transform
 * @returns Promise containing the generated MIDI file as a Blob
 */
export async function generate(midi: Blob, params: GenerateParams): Promise<Response> {
  const formData = new FormData();
  formData.append('midi_file', midi);
  formData.append('params', JSON.stringify(params));
  formData.append('client_id', clientId);
  return fetch('/api/generate/', {
    method: 'POST',
    body: formData
  });
}
