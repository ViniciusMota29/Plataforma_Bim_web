"""
AI Service for image analysis using SwinDeepLab model
Adapted from the existing analisar_rede.py
"""
import os
import sys
import cv2
import torch
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from albumentations.pytorch import ToTensorV2
from albumentations import Normalize, Compose

# Add parent directory to path to import swin_model
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "PonteInspecao.lib"))

try:
    from swin_model import SwinDeepLab
except ImportError:
    SwinDeepLab = None
    print("Warning: SwinDeepLab model not found. AI analysis will not work.")


def analyze_image_with_ai(image_paths: List[str], settings) -> Dict[str, Any]:
    """
    Analyze images using SwinDeepLab model
    Returns detection results with masks and heatmaps
    """
    if SwinDeepLab is None:
        raise ImportError("SwinDeepLab model not available")
    
    # Load model
    model_path = Path(settings.AI_MODEL_PATH)
    if not model_path.exists():
        # Try relative path
        model_path = Path(__file__).parent.parent.parent.parent / "PonteInspecao.lib" / "best_deeplab_lr0.0001_bs4_fold2.pth"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _ = load_model(str(model_path), device)
    
    # Create output directory
    output_dir = Path(settings.UPLOAD_DIR) / "results" / "ai_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process images
    detections = []
    all_confidences = []
    
    val_transform = Compose([
        Normalize(),
        ToTensorV2()
    ])
    
    for img_path in image_paths:
        # Load image
        img = cv2.imread(img_path)
        if img is None:
            continue
        
        # Preprocess
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (settings.AI_IMAGE_SIZE, settings.AI_IMAGE_SIZE))
        tensor = val_transform(image=image_resized)['image'].unsqueeze(0).to(device)
        
        # Inference
        with torch.no_grad():
            pred = model(tensor)
            prob = torch.sigmoid(pred)[0, 0].cpu().numpy()
        
        # Calculate confidence (percentage of pixels above threshold)
        confidence = float(np.mean(prob > settings.AI_THRESHOLD))
        all_confidences.append(confidence)
        
        # Create mask
        mask = (prob > settings.AI_THRESHOLD).astype(np.uint8) * 255
        mask_resized = cv2.resize(mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
        
        # Create heatmap
        prob_map = (prob * 255).astype(np.uint8)
        prob_resized = cv2.resize(prob_map, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
        heatmap = cv2.applyColorMap(prob_resized, cv2.COLORMAP_JET)
        
        # Save results
        img_name = Path(img_path).stem
        mask_path = output_dir / f"mask_{img_name}.png"
        heatmap_path = output_dir / f"heatmap_{img_name}.png"
        
        cv2.imwrite(str(mask_path), mask_resized)
        cv2.imwrite(str(heatmap_path), heatmap)
        
        # Draw contours on original
        result_img = img.copy()
        contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(result_img, contours, -1, (0, 0, 255), 2)
        
        result_path = output_dir / f"result_{img_name}.jpg"
        cv2.imwrite(str(result_path), result_img)
        
        detections.append({
            "image_path": img_path,
            "confidence": confidence,
            "has_detection": confidence > 0.1,  # At least 10% of pixels detected
            "mask_path": str(mask_path),
            "heatmap_path": str(heatmap_path),
            "result_path": str(result_path)
        })
    
    avg_confidence = np.mean(all_confidences) if all_confidences else 0.0
    
    return {
        "success": True,
        "detections": detections,
        "confidence": float(avg_confidence),
        "mask_path": str(detections[0]["mask_path"]) if detections else None,
        "heatmap_path": str(detections[0]["heatmap_path"]) if detections else None,
        "result_path": str(detections[0]["result_path"]) if detections else None
    }


def load_model(model_path: str, device: str):
    """Load SwinDeepLab model"""
    checkpoint = torch.load(model_path, map_location=device)
    
    if isinstance(checkpoint, dict):
        if 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        elif 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
        else:
            state_dict = checkpoint
    else:
        state_dict = checkpoint
    
    model = SwinDeepLab().to(device)
    
    try:
        model.load_state_dict(state_dict, strict=True)
    except RuntimeError:
        model.load_state_dict(state_dict, strict=False)
    
    model.eval()
    return model, device

