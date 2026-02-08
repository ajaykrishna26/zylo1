import io
import re
import numpy as np
import soundfile as sf
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from phonemizer import phonemize
from dtw import dtw
import warnings
warnings.filterwarnings('ignore')


class Wav2Vec2PronunciationModel:

    def __init__(self, model_name="facebook/wav2vec2-base-960h"):
        print("Loading wav2vec2 model...")
        self.processor = Wav2Vec2Processor.from_pretrained(model_name)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_name)
        self.model.eval()

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print("Wav2vec2 ready")

    # ---------- AUDIO ----------
    def load_audio_from_bytes(self, audio_bytes):
        """Load and resample audio to 16kHz"""
        try:
            # Debug: Save audio to file to check quality
            self.save_debug_audio(audio_bytes, "before_processing.wav")
            
            # Load audio
            audio, sr = sf.read(io.BytesIO(audio_bytes))
            
            print(f"DEBUG: Original audio - Shape: {audio.shape}, SR: {sr}, Duration: {len(audio)/sr:.2f}s")
            
            # Convert to mono if stereo
            if len(audio.shape) > 1:
                print(f"DEBUG: Converting stereo to mono")
                audio = audio.mean(axis=1)
            
            # Resample to 16kHz if needed
            if sr != 16000:
                print(f"DEBUG: Resampling from {sr}Hz to 16000Hz")
                import librosa
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
                sr = 16000
            
            # Normalize audio
            if len(audio) > 0:
                max_val = np.max(np.abs(audio))
                print(f"DEBUG: Max audio value before normalization: {max_val}")
                if max_val > 0:
                    audio = audio / (max_val + 1e-8)
                    print(f"DEBUG: Audio normalized")
            
            # Trim silence
            audio = self.trim_silence(audio)
            print(f"DEBUG: After trimming - Length: {len(audio)}, Duration: {len(audio)/sr:.2f}s")
            
            # Save processed audio for debugging
            self.save_audio_to_file(audio, sr, "after_processing.wav")
            
            return audio, sr
        except Exception as e:
            print(f"Error loading audio: {e}")
            import traceback
            traceback.print_exc()
            return np.array([]), 16000
    
    def save_debug_audio(self, audio_bytes, filename):
        """Save audio bytes to file for debugging"""
        try:
            with open(filename, "wb") as f:
                f.write(audio_bytes)
            print(f"DEBUG: Saved raw audio to {filename} ({len(audio_bytes)} bytes)")
        except Exception as e:
            print(f"DEBUG: Failed to save audio: {e}")
    
    def save_audio_to_file(self, audio, sr, filename):
        """Save numpy audio array to file"""
        try:
            sf.write(filename, audio, sr)
            print(f"DEBUG: Saved processed audio to {filename}")
        except Exception as e:
            print(f"DEBUG: Failed to save processed audio: {e}")
    
    def trim_silence(self, audio, threshold=0.02):
        """Remove leading and trailing silence"""
        if len(audio) == 0:
            return audio
        
        # Find where audio exceeds threshold
        audio_abs = np.abs(audio)
        mask = audio_abs > threshold
        indices = np.where(mask)[0]
        
        if len(indices) > 0:
            start = max(0, indices[0] - 500)  # Keep a small buffer
            end = min(len(audio), indices[-1] + 500)
            trimmed = audio[start:end]
            print(f"DEBUG: Trimmed silence - Original: {len(audio)}, Trimmed: {len(trimmed)}")
            return trimmed
        return audio

    # ---------- ASR ----------
    def transcribe(self, audio):
        """Transcribe audio to text"""
        if len(audio) == 0:
            print("DEBUG: Empty audio, cannot transcribe")
            return ""
        
        try:
            print(f"DEBUG: Transcribing audio of length {len(audio)}")
            
            # Ensure audio is float32
            audio = audio.astype(np.float32)
            
            # Check audio statistics
            print(f"DEBUG: Audio stats - Min: {audio.min():.4f}, Max: {audio.max():.4f}, Mean: {audio.mean():.4f}")
            
            # Play audio for debugging (optional)
            self.play_audio_for_debug(audio, 16000)
            
            inputs = self.processor(
                audio,
                sampling_rate=16000,
                return_tensors="pt",
                padding=True
            )

            print(f"DEBUG: Input shape to model: {inputs.input_values.shape}")
            
            with torch.no_grad():
                logits = self.model(inputs.input_values.to(self.device)).logits

            pred_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.decode(pred_ids[0])
            
            print(f"DEBUG: Raw transcription: '{transcription}'")
            return transcription.lower().strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def play_audio_for_debug(self, audio, sr):
        """Play audio for debugging (optional)"""
        try:
            import sounddevice as sd
            print(f"DEBUG: Playing audio for {len(audio)/sr:.2f} seconds...")
            sd.play(audio, sr)
            # Don't wait for playback to complete
            # sd.wait()
        except Exception as e:
            print(f"DEBUG: Could not play audio: {e}")

    # ---------- PHONEMES ----------
    def word_to_phonemes(self, text):
        """Convert text to phonemes"""
        if not text or len(text.strip()) == 0:
            return []
        try:
            print(f"DEBUG: Converting to phonemes: '{text}'")
            ph = phonemize(
                text,
                language="en-us",
                backend="espeak",
                strip=True,
                preserve_punctuation=False,
                with_stress=True
            )
            # Split by spaces, filter empty strings
            phonemes = [p for p in ph.split() if p]
            print(f"DEBUG: Phonemes: {phonemes}")
            return phonemes
        except Exception as e:
            print(f"Phonemizer failed: {e}")
            return []

    # ---------- SIMPLIFIED SCORING ----------
    def pronunciation_score_simple(self, expected, spoken):
        """Simplified scoring - more reliable"""
        if not expected or not spoken:
            print(f"DEBUG: Missing text - Expected: {expected}, Spoken: {spoken}")
            return 0.0, [], []
        
        print(f"\n{'='*30} SCORING {'='*30}")
        print(f"Original Expected: '{expected}'")
        print(f"Original Spoken: '{spoken}'")
        
        # Clean texts
        clean_exp = re.sub(r'[^\w\s]', '', expected.lower()).strip()
        clean_spk = re.sub(r'[^\w\s]', '', spoken.lower()).strip()
        
        print(f"Cleaned Expected: '{clean_exp}'")
        print(f"Cleaned Spoken: '{clean_spk}'")
        
        # 1. Exact word match (for short words/phrases)
        if clean_exp == clean_spk:
            print("DEBUG: Perfect match!")
            return 1.0, [], []
        
        # 2. Use SequenceMatcher for similarity
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, clean_exp, clean_spk).ratio()
        print(f"DEBUG: SequenceMatcher similarity: {similarity:.4f}")
        
        # 3. Check for partial matches
        exp_words = clean_exp.split()
        spk_words = clean_spk.split()
        
        print(f"DEBUG: Expected words: {exp_words}")
        print(f"DEBUG: Spoken words: {spk_words}")
        
        if len(exp_words) > 0 and len(spk_words) > 0:
            # Calculate word-level accuracy
            correct_words = 0
            for exp_word in exp_words:
                # Check if this expected word appears in spoken words
                for spk_word in spk_words:
                    if exp_word == spk_word:
                        correct_words += 1
                        break
                    # Partial match (substring)
                    elif exp_word in spk_word or spk_word in exp_word:
                        correct_words += 0.5
                        break
            
            word_accuracy = correct_words / len(exp_words) if exp_words else 0
            print(f"DEBUG: Word-level accuracy: {word_accuracy:.4f} ({correct_words}/{len(exp_words)})")
            
            # Calculate character-level accuracy
            char_similarity = SequenceMatcher(None, clean_exp.replace(" ", ""), 
                                            clean_spk.replace(" ", "")).ratio()
            print(f"DEBUG: Character-level similarity: {char_similarity:.4f}")
            
            # Combine scores with weights
            final_score = (
                similarity * 0.3 + 
                word_accuracy * 0.4 + 
                char_similarity * 0.3
            )
        else:
            final_score = similarity
        
        print(f"DEBUG: Final calculated score: {final_score:.4f}")
        print(f"{'='*70}\n")
        
        # Get phonemes for feedback
        exp_ph = self.word_to_phonemes(expected)
        spk_ph = self.word_to_phonemes(spoken)
        
        return round(final_score, 2), exp_ph, spk_ph

    # ---------- SENTENCE-LEVEL EVALUATION ----------
    def evaluate_sentence(self, audio_bytes, expected_sentence):
        """Evaluate pronunciation of a full sentence"""
        print(f"\n{'='*50}")
        print(f"EVALUATION STARTED")
        print(f"Expected sentence: '{expected_sentence}'")
        print(f"Audio bytes received: {len(audio_bytes)} bytes")
        
        # Check if audio_bytes is valid
        if audio_bytes is None or len(audio_bytes) < 100:
            print("ERROR: No audio bytes or too short")
            return {
                "expected_sentence": expected_sentence,
                "spoken_text": "",
                "score": 0.0,
                "status": "error",
                "feedback": "No audio recorded. Please click the record button and speak clearly.",
                "debug": "No audio bytes or too short"
            }
        
        # Load and transcribe audio
        print("Loading audio...")
        audio, sr = self.load_audio_from_bytes(audio_bytes)
        
        if len(audio) < 800:  # Less than 0.05 second at 16kHz
            print(f"ERROR: Audio too short after processing: {len(audio)} samples")
            return {
                "expected_sentence": expected_sentence,
                "spoken_text": "",
                "score": 0.0,
                "status": "error",
                "feedback": "Audio recording was too short. Please speak for at least 1-2 seconds.",
                "debug": f"Audio too short: {len(audio)} samples"
            }
        
        print(f"Audio loaded successfully: {len(audio)} samples, {sr} Hz")
        print(f"Audio duration: {len(audio)/sr:.2f} seconds")
        
        # Transcribe using wav2vec2
        print("\nTranscribing with wav2vec2...")
        spoken_text = self.transcribe(audio)
        print(f"Wav2Vec2 transcription: '{spoken_text}'")
        
        # If transcription is poor, try Google fallback
        should_use_fallback = (
            not spoken_text or 
            len(spoken_text) < len(expected_sentence) * 0.3 or
            spoken_text.strip() == ""
        )
        
        if should_use_fallback:
            print("\nTranscription poor, trying Google fallback...")
            google_text = self.google_fallback_safe(audio, sr)
            if google_text and len(google_text) > 0:
                print(f"Google fallback result: '{google_text}'")
                # Use Google if it's better
                if len(google_text) > len(spoken_text) * 1.2:
                    spoken_text = google_text
                    print("Using Google transcription")
                else:
                    print("Keeping wav2vec2 transcription")
        
        # If still empty, provide helpful feedback
        if not spoken_text or spoken_text.strip() == "":
            print("ERROR: No transcription obtained")
            return {
                "expected_sentence": expected_sentence,
                "spoken_text": "",
                "score": 0.0,
                "status": "mispronounced",
                "feedback": f"Could not understand your speech. Please speak clearly and try saying: '{expected_sentence}'",
                "debug": "No transcription obtained from any service"
            }
        
        print(f"\nFinal transcription to evaluate: '{spoken_text}'")
        
        # Calculate pronunciation score
        score, exp_ph, spk_ph = self.pronunciation_score_simple(
            expected_sentence,
            spoken_text
        )
        
        print(f"\nSCORE CALCULATION COMPLETE")
        print(f"Expected: '{expected_sentence}'")
        print(f"Heard: '{spoken_text}'")
        print(f"Score: {score:.2f}/1.00")
        
        # Determine feedback based on score
        if score >= 0.85:
            status = "excellent"
            feedback = f"Perfect! You pronounced it correctly: '{expected_sentence}'"
        elif score >= 0.70:
            status = "good"
            feedback = f"Good job! You said: '{spoken_text}'. Very close to: '{expected_sentence}'"
        elif score >= 0.50:
            status = "fair"
            feedback = f"Almost there! You said: '{spoken_text}'. Try to match: '{expected_sentence}'"
        elif score >= 0.30:
            status = "needs_improvement"
            feedback = f"Getting closer. You said: '{spoken_text}'. Listen to the example and repeat: '{expected_sentence}'"
        else:
            status = "mispronounced"
            feedback = f"Let's try again. You said: '{spoken_text}'. Please listen carefully and repeat: '{expected_sentence}'"
        
        # Add phoneme feedback if available
        if exp_ph and spk_ph and len(exp_ph) > 0 and len(spk_ph) > 0:
            if exp_ph != spk_ph:
                feedback += f"\nPhonemes: Expected {exp_ph}, Heard {spk_ph}"
        
        print(f"Status: {status}")
        print(f"Feedback: {feedback}")
        print(f"{'='*50}\n")
        
        return {
            "expected_sentence": expected_sentence,
            "spoken_text": spoken_text,
            "score": float(score),
            "status": status,
            "expected_phonemes": exp_ph,
            "spoken_phonemes": spk_ph,
            "feedback": feedback,
            "debug_info": {
                "audio_samples": len(audio),
                "audio_duration": f"{len(audio)/sr:.2f}s",
                "sample_rate": sr,
                "model_used": "wav2vec2 with Google fallback"
            }
        }

    def google_fallback_safe(self, audio, sr):
        """Safer Google fallback using speech_recognition"""
        try:
            print("DEBUG: Attempting Google Speech Recognition fallback...")
            import speech_recognition as sr_module
            
            # Normalize audio to int16 for WAV format
            if len(audio) == 0:
                print("DEBUG: Empty audio for Google fallback")
                return ""
            
            # Scale to int16 range
            if np.max(np.abs(audio)) > 0:
                audio_normalized = (audio / np.max(np.abs(audio))) * 32767
            else:
                audio_normalized = audio * 32767
            
            audio_int16 = audio_normalized.astype(np.int16)
            
            # Create in-memory WAV file
            import wave
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 2 bytes for int16
                wav_file.setframerate(sr)
                wav_file.writeframes(audio_int16.tobytes())
            
            wav_data = wav_io.getvalue()
            
            # Save for debugging
            with open("google_fallback_input.wav", "wb") as f:
                f.write(wav_data)
            print("DEBUG: Saved audio for Google fallback to 'google_fallback_input.wav'")
            
            # Use speech_recognition
            recognizer = sr_module.Recognizer()
            audio_data = sr_module.AudioData(wav_data, sample_rate=sr, sample_width=2)
            
            text = recognizer.recognize_google(audio_data, language="en-US")
            print(f"DEBUG: Google recognition successful: '{text}'")
            return text.lower().strip()
            
        except sr_module.UnknownValueError:
            print("DEBUG: Google Speech Recognition could not understand audio")
            return ""
        except sr_module.RequestError as e:
            print(f"DEBUG: Google Speech Recognition request error: {e}")
            return ""
        except Exception as e:
            print(f"DEBUG: Google fallback failed: {e}")
            import traceback
            traceback.print_exc()
            return ""

    # ---------- LEGACY COMPATIBILITY ----------
    def evaluate(self, audio_bytes, expected_word):
        """Alias for backward compatibility"""
        return self.evaluate_sentence(audio_bytes, expected_word)


# Test function with actual recording simulation
def test_with_real_audio():
    """Test with a real audio file or simulated recording"""
    model = Wav2Vec2PronunciationModel()
    
    # Option 1: Load from existing WAV file
    try:
        print("\nTest 1: Loading from test_audio.wav")
        with open("test_audio.wav", "rb") as f:
            audio_bytes = f.read()
        
        result = model.evaluate_sentence(
            audio_bytes=audio_bytes,
            expected_sentence="The quick brown fox jumps over the lazy dog"
        )
        
    except FileNotFoundError:
        print("\nTest 1: test_audio.wav not found, using simulated audio")
        # Option 2: Create simulated audio (silence with a beep)
        import wave
        import struct
        import math
        
        # Create a simple beep sound
        sample_rate = 16000
        duration = 2.0  # seconds
        freq = 440.0  # Hz
        
        # Generate sine wave
        samples = []
        for i in range(int(duration * sample_rate)):
            value = math.sin(2 * math.pi * freq * i / sample_rate) * 0.5
            samples.append(value)
        
        # Convert to bytes
        audio_io = io.BytesIO()
        with wave.open(audio_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            
            # Convert to int16
            int_samples = [int(s * 32767) for s in samples]
            byte_samples = struct.pack('<' + ('h' * len(int_samples)), *int_samples)
            wav_file.writeframes(byte_samples)
        
        audio_bytes = audio_io.getvalue()
        
        # Save the test audio
        with open("test_generated.wav", "wb") as f:
            f.write(audio_bytes)
        print("Saved generated test audio to 'test_generated.wav'")
        
        result = model.evaluate_sentence(
            audio_bytes=audio_bytes,
            expected_sentence="Hello world"
        )
    
    # Print results
    print("\n" + "="*60)
    print("FINAL TEST RESULTS:")
    print("="*60)
    for key, value in result.items():
        if key != "debug_info":
            print(f"{key}: {value}")
        else:
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
    
    return result


# Quick diagnostic function
def diagnose_audio_recording(audio_bytes, expected_text="test"):
    """Quick diagnostic to check audio quality"""
    print("\n" + "="*60)
    print("AUDIO DIAGNOSTIC")
    print("="*60)
    
    if audio_bytes is None:
        print("ERROR: No audio bytes provided")
        return
    
    print(f"Audio bytes size: {len(audio_bytes)} bytes")
    
    # Try to load and analyze
    try:
        audio, sr = sf.read(io.BytesIO(audio_bytes))
        print(f"Successfully loaded audio:")
        print(f"  Shape: {audio.shape}")
        print(f"  Sample rate: {sr} Hz")
        print(f"  Duration: {len(audio)/sr:.2f} seconds")
        
        if len(audio.shape) > 1:
            print(f"  Channels: {audio.shape[1]} (stereo)")
            print(f"  Mono conversion needed")
        else:
            print(f"  Channels: 1 (mono)")
        
        # Check audio levels
        if len(audio) > 0:
            max_val = np.max(np.abs(audio))
            print(f"  Max amplitude: {max_val:.4f}")
            if max_val < 0.01:
                print("  WARNING: Audio may be too quiet!")
            
            # Check for silence
            rms = np.sqrt(np.mean(audio**2))
            print(f"  RMS level: {rms:.6f}")
            if rms < 0.001:
                print("  WARNING: Audio may be silent or too quiet!")
    
    except Exception as e:
        print(f"ERROR loading audio: {e}")
    
    print("="*60)


if __name__ == "__main__":
    print("Wav2Vec2 Pronunciation Model")
    print("To test, run: test_with_real_audio()")
    print("For diagnostics, run: diagnose_audio_recording(audio_bytes)")
    
    # Create a simple CLI for testing
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_with_real_audio()