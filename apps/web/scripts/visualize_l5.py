import numpy as np
from PIL import Image
import os
import math

# VISUALIZER
# Converts binary streams to images to detect visual patterns.

FILES = [
    "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/cross_constraint_mining/layer5_full_stream.bin",
    "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_A.der",
    "/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/candidate_B.der",
    "decrypted.bin" # if it exists
]

def visualize():
    print("🎨 VISUALIZING ARTIFACTS...")
    
    for fpath in FILES:
        if not os.path.exists(fpath): continue
        
        name = os.path.basename(fpath)
        with open(fpath, "rb") as f:
            data = f.read()
            
        size = len(data)
        # Calculate square side
        side = int(math.ceil(math.sqrt(size)))
        
        # Pad data
        padded = data + b'\x00' * (side*side - size)
        
        # Create Image
        arr = np.frombuffer(padded, dtype=np.uint8).reshape((side, side))
        img = Image.fromarray(arr)
        
        out_path = f"/Users/lukashertle/Developer/projects/qubic-academic-docs/outputs/{name}_viz.png"
        img.save(out_path)
        print(f"[*] Saved visualization: {out_path} ({side}x{side})")

if __name__ == "__main__":
    visualize()
