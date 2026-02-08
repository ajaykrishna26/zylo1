import React, { useEffect, useRef, useState, useCallback } from "react";
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set worker source
// Set worker source dynamically to match version
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

const DocumentReader = ({
  onClose,
  sentences: parentSentences,
  currentIndex: parentIndex,
  onJumpTo,
  currentPdfName,
  pdfUrl,
  isReading: parentIsReading,
  readingSpeed = 120,
  onReadAloud,
  onPractice,
  onSpeedChange,
  isProcessing,
  practiceResult,
  wordFeedback: parentWordFeedback,
  stats // Add stats to props
}) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [loading, setLoading] = useState(true);

  // Audio refs
  const utteranceRef = useRef(null);
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);

  // --- STATE ---
  // --- STATE ---
  const [domItemsMap, setDomItemsMap] = useState([]); // Array of arrays: sentenceIdx -> element list

  // Simplified: use currentIndex directly from props
  const activeSentenceIndex = parentIndex || 0;

  // --- RECORDING STATE ---
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingTimeoutRef = useRef(null); // Ref for auto-stop timeout

  // Magnifier Lens Ref
  const lensRef = useRef(null);

  // Load voices
  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
      if (availableVoices.length > 0 && !selectedVoice) {
        const preferred = availableVoices.find(v => v.name.includes("Google US English") || v.name.includes("Zira"));
        setSelectedVoice(preferred || availableVoices[0]);
      }
    };
    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
  }, []);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setLoading(false);
  };

  // --- RECORDING LOGIC ---
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      recorder.onstop = async () => {
        const webmBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

        try {
          // Convert WebM to WAV (16kHz mono) for backend compatibility
          console.log("Converting recording to WAV...");
          const wavBlob = await convertToWav(webmBlob);
          onPractice(wavBlob);
        } catch (err) {
          console.error("WAV Conversion error:", err);
          // Fallback to original blob if conversion fails
          onPractice(webmBlob);
        }

        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      setIsRecording(true);

      // Auto-stop after 10 seconds timeout
      if (recordingTimeoutRef.current) clearTimeout(recordingTimeoutRef.current);
      recordingTimeoutRef.current = setTimeout(() => {
        if (isRecording) {
          console.log("[RECORDING] Auto-stopping due to 10s timeout");
          stopRecording();
          if (recognitionRef.current) recognitionRef.current.stop();
        }
      }, 10000);

    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Could not access microphone. Please check permissions.");
    }
  };

  const convertToWav = async (blob) => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    const arrayBuffer = await blob.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

    // Get PCM data from mono (or first channel)
    const pcmData = audioBuffer.getChannelData(0);

    // Check for silence (is the peak amplitude too low?)
    let maxAmp = 0;
    for (let i = 0; i < pcmData.length; i++) {
      const absVal = Math.abs(pcmData[i]);
      if (absVal > maxAmp) maxAmp = absVal;
    }

    console.log(`[AUDIO] Peak amplitude: ${maxAmp}`);
    if (maxAmp < 0.01) {
      console.warn("Audio seems very quiet or silent.");
      // We still proceed, but the backend might fail.
    }

    const wavBuffer = encodeWav(pcmData, 16000);
    return new Blob([wavBuffer], { type: 'audio/wav' });
  };

  const encodeWav = (samples, sampleRate) => {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    // RIFF identifier
    writeString(view, 0, 'RIFF');
    // RIFF chunk length
    view.setUint32(4, 36 + samples.length * 2, true);
    // RIFF type
    writeString(view, 8, 'WAVE');
    // format chunk identifier
    writeString(view, 12, 'fmt ');
    // format chunk length
    view.setUint32(16, 16, true);
    // sample format (raw)
    view.setUint16(20, 1, true);
    // channel count
    view.setUint16(22, 1, true);
    // sample rate
    view.setUint32(24, sampleRate, true);
    // byte rate (sample rate * block align)
    view.setUint32(28, sampleRate * 2, true);
    // block align (channel count * bytes per sample)
    view.setUint16(32, 2, true);
    // bits per sample
    view.setUint16(34, 16, true);
    // data chunk identifier
    writeString(view, 36, 'data');
    // data chunk length
    view.setUint32(40, samples.length * 2, true);

    // Write the PCM samples
    let offset = 44;
    for (let i = 0; i < samples.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }

    return buffer;
  };

  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  const stopRecording = () => {
    if (recordingTimeoutRef.current) {
      clearTimeout(recordingTimeoutRef.current);
      recordingTimeoutRef.current = null;
    }
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // --- STREAMING RECOGNITION (Web Speech API) ---
  const recognitionRef = useRef(null);
  const [liveSpokenWords, setLiveSpokenWords] = useState([]);

  useEffect(() => {
    if (window.webkitSpeechRecognition || window.SpeechRecognition) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      const rec = new SpeechRecognition();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = 'en-US';

      rec.onresult = (event) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        const words = transcript.toLowerCase().replace(/[^\w\s]/g, '').split(/\s+/).filter(Boolean);
        setLiveSpokenWords(words);

        // Auto-stop if user has spoken as many words as in current sentence
        const expectedText = parentSentences[parentIndex]?.text || "";
        const expectedWordCount = expectedText.split(/\s+/).filter(Boolean).length;

        if (words.length >= expectedWordCount && expectedWordCount > 0) {
          console.log("[RECORDING] Auto-stopping: All words detected");
          // Small delay to ensure last word is captured in media recorder
          setTimeout(() => {
            stopRecording();
            rec.stop();
          }, 500);
        }
      };

      recognitionRef.current = rec;
    }
  }, []);

  const handlePracticeClick = () => {
    if (isRecording) {
      stopRecording();
      if (recognitionRef.current) recognitionRef.current.stop();
    } else {
      setLiveSpokenWords([]);
      startRecording();
      if (recognitionRef.current) {
        try { recognitionRef.current.start(); } catch (e) { console.error("Recognition start error:", e); }
      }
    }
  };

  // --- LISTEN FEATURE (Backend TTS) ---
  const [isTtsLoading, setIsTtsLoading] = useState(false);
  const audioPlayerRef = useRef(new Audio());

  const handleListenClick = async () => {
    if (!parentSentences[activeSentenceIndex]) return;

    // Stop browser voice reading
    window.speechSynthesis.cancel();

    setIsTtsLoading(true);
    try {
      const text = parentSentences[activeSentenceIndex].text;
      const response = await fetch('/api/practice/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        audioPlayerRef.current.src = url;
        audioPlayerRef.current.play();
      }
    } catch (err) {
      console.error("TTS Fetch error:", err);
    } finally {
      setIsTtsLoading(false);
    }
  };

  // --- CORE LOGIC: SENTENCE HIGHLIGHTING ---

  const onPageLoadSuccess = useCallback(async (page) => {
    try {
      const textContent = await page.getTextContent();
      const items = textContent.items;
      if (items.length === 0) return;

      // Map backend sentences (lines) for THIS page to DOM spans
      // We wait for DOM to be ready (increased delay for complex PDFs)
      setTimeout(() => mapSentencesToDom(items), 1500);

    } catch (e) {
      console.error("Error loading text content:", e);
    }
  }, [pageNumber, parentSentences]);

  const mapSentencesToDom = (textContentItems) => {
    const container = document.querySelector('.react-pdf__Page__textContent');
    if (!container) {
      console.warn("[DocumentReader] Text container not found for highlighting.");
      return;
    }

    // Clear old highlights first
    container.querySelectorAll('.sentence-active').forEach(el => {
      el.classList.remove('sentence-active');
    });

    const spans = Array.from(container.querySelectorAll('span'));
    console.log(`[DocumentReader] Found ${spans.length} spans in PDF text layer.`);

    // Group spans into lines based on Y-coordinate (using offsetTop for more stability)
    let currentLineY = -1;
    let lineSpans = [];
    let linesInDom = [];

    spans.forEach((span) => {
      // Use offsetTop relative to parent for more stable grouping
      const top = span.offsetTop;

      // Filter out empty elements
      if (span.innerText.trim().length === 0) return;

      if (currentLineY === -1 || Math.abs(top - currentLineY) < 10) {
        lineSpans.push(span);
        if (currentLineY === -1) currentLineY = top;
      } else {
        linesInDom.push([...lineSpans]);
        lineSpans = [span];
        currentLineY = top;
      }
    });
    if (lineSpans.length > 0) linesInDom.push(lineSpans);

    console.log(`[DocumentReader] Detected ${linesInDom.length} lines in PDF DOM.`);

    // Map linesInDom to our backend sentences for this page
    const pageSentences = (parentSentences || []).filter(s => s.page === pageNumber);
    console.log(`[DocumentReader] Backend has ${pageSentences.length} sentences for page ${pageNumber}.`);

    const map = pageSentences.map((s, idx) => {
      const elements = linesInDom[idx] || [];
      elements.forEach(el => {
        el.classList.add('sentence-token');
        el.classList.add('interactive-token');
        el.onclick = (e) => {
          e.stopPropagation();
          if (onJumpTo) onJumpTo(s.global_index);
        };
      });
      return { global_index: s.global_index, elements };
    });

    setDomItemsMap(map);
  };


  // Highlighting Effect
  useEffect(() => {
    const container = document.querySelector('.react-pdf__Page__textContent');

    if (domItemsMap.length === 0) {
      // Remove focus mode if no map
      if (container) container.classList.remove('focus-mode');
      return;
    }

    // Focus mode is now always enabled in reader view
    if (container) {
      container.classList.add('focus-mode');
    }

    domItemsMap.forEach((mapItem) => {
      const isActive = mapItem.global_index === activeSentenceIndex;
      mapItem.elements.forEach(el => {
        if (isActive) {
          el.classList.add('sentence-active');

          // Apply word-level coloring if practiceResult exists for this sentence
          if (practiceResult && practiceResult.word_feedback) {
            applyWordColoringToElement(el, practiceResult.word_feedback);
          } else {
            // Reset element content to original text if no feedback
            if (el.dataset.originalText) {
              el.innerText = el.dataset.originalText;
            }
          }
        } else {
          el.classList.remove('sentence-active');
          // Reset non-active lines
          if (el.dataset.originalText) {
            el.innerText = el.dataset.originalText;
          }
        }
      });

      if (isActive && mapItem.elements[0]) {
        mapItem.elements[0].scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Update Magnifier Lens Position
        if (lensRef.current) {
          const container = document.querySelector('.react-pdf__Page__textContent');
          if (container) {
            // Calculate bounding box of all elements in the active sentence
            let minTop = Infinity;
            let maxBottom = -Infinity;
            let minLeft = Infinity;
            let maxRight = -Infinity;

            mapItem.elements.forEach(el => {
              const rect = el.getBoundingClientRect();
              const containerRect = container.getBoundingClientRect();

              const relativeTop = rect.top - containerRect.top;
              const relativeLeft = rect.left - containerRect.left;

              minTop = Math.min(minTop, relativeTop);
              maxBottom = Math.max(maxBottom, relativeTop + rect.height);
              minLeft = Math.min(minLeft, relativeLeft);
              maxRight = Math.max(maxRight, relativeLeft + rect.width);
            });

            // Add padding for the "lens" look
            const paddingX = 50; // Increased padding for full coverage
            const paddingY = 30; // Increased padding for vertical room

            // Note: getBoundingClientRect() ALREADY includes the CSS scale transform.
            // We capture the visual bounds of the zoomed spans.

            lensRef.current.style.display = 'block';
            lensRef.current.style.top = `${minTop - paddingY}px`;
            lensRef.current.style.left = `${minLeft - paddingX}px`;
            lensRef.current.style.width = `${(maxRight - minLeft) + (paddingX * 2)}px`;
            lensRef.current.style.height = `${(maxBottom - minTop) + (paddingY * 2)}px`;
            lensRef.current.style.opacity = '1';
          }
        }
      }
    });

    // If no active sentence, hide lens
    const hasActive = domItemsMap.some(m => m.global_index === activeSentenceIndex);
    if (!hasActive && lensRef.current) {
      lensRef.current.style.opacity = '0';
      lensRef.current.style.display = 'none';
    }

    // Simplified: No longer applying word-level colors to PDF layer
    function applyWordColoringToElement(element, wordFeedback) {
      if (!element.dataset.originalText) {
        element.dataset.originalText = element.innerText;
      }
      // Just ensure the text is reset to original (no spans/colors)
      element.innerText = element.dataset.originalText;
    }

    // Handle Page Advance: if current sentence is on a different page, flip page
    const currentSentence = parentSentences[activeSentenceIndex];
    if (currentSentence && currentSentence.page !== pageNumber) {
      setPageNumber(currentSentence.page);
    }
  }, [activeSentenceIndex, domItemsMap, pageNumber, parentSentences, parentIsReading, isRecording, practiceResult]);



  // Auto-Read useEffect removed to enforce manual line-by-line reading.

  // --- LIVELY CORRECTION LOGIC ---
  const getWordFeedback = () => {
    if (!parentSentences[activeSentenceIndex]) return [];

    // Original words
    const expected = parentSentences[activeSentenceIndex].text.split(/\s+/);

    // 1. If we have final results from backend, use them
    if (practiceResult && practiceResult.word_feedback) {
      return practiceResult.word_feedback; // Should already be [{word, status}]
    }

    // 2. Otherwise, if we are currently recording, use live streaming data
    if (isRecording) {
      return expected.map(word => {
        const clean = word.toLowerCase().replace(/[^\w\s]/g, '');
        return {
          word,
          status: liveSpokenWords.includes(clean) ? 'correct' : 'pending'
        };
      });
    }

    return expected.map(word => ({ word, status: 'none' }));
  };

  const wordFeedback = getWordFeedback();

  // Auto-correction audio
  useEffect(() => {
    if (practiceResult && !practiceResult.is_correct) {
      const missedWords = wordFeedback
        .filter(w => w.status !== 'correct' && w.status !== 'pending' && w.status !== 'none')
        .map(w => w.word);

      if (missedWords.length > 0) {
        window.speechSynthesis.cancel();
        const correctionText = `Let's try these words again: ${missedWords.join(", ")}`;
        const utterance = new SpeechSynthesisUtterance(correctionText);
        if (selectedVoice) utterance.voice = selectedVoice;
        utterance.rate = 0.9; // Slightly slower for correction

        setTimeout(() => {
          window.speechSynthesis.speak(utterance);
        }, 1000);
      }
    }
  }, [practiceResult]);

  const handleNextSentence = () => {
    if (activeSentenceIndex < (parentSentences || []).length - 1) {
      if (onJumpTo) onJumpTo(activeSentenceIndex + 1);
    }
  };

  const handlePrevSentence = () => {
    if (activeSentenceIndex > 0) {
      if (onJumpTo) onJumpTo(activeSentenceIndex - 1);
    }
  };

  return (
    <div className="document-reader fade-in" style={{ backgroundColor: '#2d3748', height: '100vh', display: 'flex', flexDirection: 'row' }}>

      <div className="reader-sidebar glass" style={{ width: '320px', flexShrink: 0, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <button className="btn btn-secondary" onClick={onClose} style={{ alignSelf: 'flex-start' }}>← Back</button>
        <div>
          <h3 className="gradient-text" style={{ fontSize: '1.5rem', marginBottom: '5px' }}>Reader</h3>
          <p className="stat-label">{currentPdfName}</p>
        </div>

        <div className="stats-container" style={{ padding: '15px', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '8px', marginBottom: '10px' }}>
          <h4 style={{ margin: '0 0 10px 0', fontSize: '1rem', color: '#a0aec0' }}>Session Stats</h4>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
            <span>Completed:</span>
            <span style={{ fontWeight: 'bold' }}>{stats?.completedSentences || 0}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Accuracy:</span>
            <span style={{ fontWeight: 'bold', color: '#48BB78' }}>
              {stats?.totalAttempts > 0
                ? Math.round((stats.correctAttempts / stats.totalAttempts) * 100)
                : 0}%
            </span>
          </div>
        </div>

        <div className="control-group box" style={{ padding: '15px', backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <button className="btn btn-sm btn-secondary" onClick={handlePrevSentence} disabled={activeSentenceIndex <= 0}>◀</button>
            <span className="stat-value" style={{ flex: 1, textAlign: 'center' }}>{activeSentenceIndex + 1} / {(parentSentences || []).length}</span>
            <button className="btn btn-sm btn-secondary" onClick={handleNextSentence} disabled={activeSentenceIndex >= (parentSentences || []).length - 1}>▶</button>
          </div>

          <div style={{ fontSize: '1.1rem', color: '#e2e8f0', backgroundColor: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '10px', minHeight: '100px', display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
            {(parentSentences || []).length > 0 ? (
              wordFeedback.map((w, i) => (
                <span
                  key={i}
                  className="practice-word"
                  style={{
                    color: '#E2E8F0',
                    transition: 'all 0.3s ease',
                    padding: '2px 4px',
                    borderRadius: '4px'
                  }}
                >
                  {w.word}
                </span>
              ))
            ) : (
              <div style={{ color: '#a0aec0' }}>
                {loading ? "Loading PDF..." : "Extracting text..."}
              </div>
            )}
          </div>

          {practiceResult && (
            <div className="practice-feedback fade-in" style={{ marginTop: '10px', padding: '10px', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
                <span style={{ fontSize: '0.8rem', color: '#a0aec0' }}>Accuracy Score:</span>
                <span style={{ fontWeight: 'bold', color: practiceResult.is_correct ? '#48BB78' : '#ED8936' }}>
                  {Math.round(practiceResult.score * 100)}%
                </span>
              </div>
              <p style={{ fontSize: '0.9rem', margin: 0, fontStyle: 'italic', color: '#fff' }}>
                {practiceResult.feedback}
              </p>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '15px' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handleListenClick}
                className="btn btn-secondary"
                style={{ flex: 1 }}
                disabled={isTtsLoading}
              >
                {isTtsLoading ? '...' : '🔊 Listen'}
              </button>
              <button
                onClick={handlePracticeClick}
                className={`btn ${isRecording ? 'btn-danger pulse' : 'btn-primary'}`}
                style={{ flex: 2 }}
                disabled={isProcessing}
              >
                {isRecording ? '⏹ Stop' : '🎤 Practice'}
              </button>
            </div>
            <button onClick={handleNextSentence} className="btn btn-success" style={{ width: '100%', backgroundColor: '#48BB78' }}>Continue ➡</button>
          </div>
          {isRecording && <p style={{ color: '#ff5252', fontSize: '0.8rem', textAlign: 'center', marginTop: '5px' }}>Recording in progress...</p>}
        </div>

        <div className="control-group">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <select className="btn btn-secondary" value={readingSpeed} onChange={(e) => onSpeedChange(Number(e.target.value))}>
              <option value={80}>Slow</option>
              <option value={120}>Normal</option>
              <option value={160}>Fast</option>
            </select>
            <select className="btn btn-secondary" onChange={(e) => {
              const v = voices.find(vo => vo.name === e.target.value);
              setSelectedVoice(v);
            }}>
              {voices.map(v => <option key={v.name} value={v.name}>{v.name.replace(/Microsoft |Google /, '')}</option>)}
            </select>
          </div>
        </div>

        <div className="stat-item" style={{ marginTop: 'auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'center' }}>
            <button className="btn btn-secondary" disabled={pageNumber <= 1} onClick={() => setPageNumber(p => p - 1)}>◀</button>
            <span className="stat-value">{pageNumber} / {numPages || '--'}</span>
            <button className="btn btn-secondary" disabled={pageNumber >= numPages} onClick={() => setPageNumber(p => p + 1)}>▶</button>
          </div>
        </div>
      </div>

      <div className="reader-content" style={{ flex: 1, padding: '40px', display: 'flex', justifyContent: 'center', overflow: 'auto', backgroundColor: '#525659' }}>
        <Document
          file={pdfUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          loading={<div className="text-white">Loading Document...</div>}
          className="pdf-document"
        >
          <Page
            pageNumber={pageNumber}
            onLoadSuccess={onPageLoadSuccess}
            className="pdf-page shadow-2xl"
            width={850}
            renderTextLayer={true}
            renderAnnotationLayer={false}
          >
            <div ref={lensRef} className="magnifier-container" style={{ display: 'none', opacity: 0 }} />
          </Page>
        </Document>
      </div>

    </div>
  );
};

export default DocumentReader;
