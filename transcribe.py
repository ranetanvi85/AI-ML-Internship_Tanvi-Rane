from faster_whisper import WhisperModel

def transcribe_audio(audio_file):
    output_text = ""
    try:
        model_size = "small"
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_file, beam_size=5, language="en")
        
        for segment in segments:
            output_text += segment.text + " "

        return output_text.strip(), None
    except Exception as e:
        return None, str(e)
