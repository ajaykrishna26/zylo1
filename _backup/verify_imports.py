
import sys
import os

print(f"Python: {sys.version}")
print(f"CWD: {os.getcwd()}")

try:
    import flask
    print(f"Flask: OK ({flask.__version__})")
except ImportError as e:
    print(f"Flask: FAIL ({e})")

try:
    import numpy
    print(f"Numpy: OK ({numpy.__version__})")
except ImportError as e:
    print(f"Numpy: FAIL ({e})")

try:
    import soundfile
    print(f"Soundfile: OK")
except ImportError as e:
    print(f"Soundfile: FAIL ({e})")

try:
    import torch
    print(f"Torch: OK ({torch.__version__})")
except ImportError as e:
    print(f"Torch: FAIL ({e})")

try:
    import transformers
    print(f"Transformers: OK ({transformers.__version__})")
except ImportError as e:
    print(f"Transformers: FAIL ({e})")

try:
    import scipy
    print(f"Scipy: OK")
except ImportError as e:
    print(f"Scipy: FAIL ({e})")

try:
    from dtw import dtw
    print(f"dtw-python: OK")
except ImportError as e:
    print(f"dtw-python: FAIL ({e})")

try:
    from phonemizer import phonemize
    print(f"phonemizer: OK")
except ImportError as e:
    print(f"phonemizer: FAIL ({e})")

print("All verification completed.")
