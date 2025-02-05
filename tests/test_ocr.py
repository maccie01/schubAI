import httpx
import pytest
from pathlib import Path
import os

OCR_SERVICE_URL = "http://localhost:8081"

@pytest.fixture
def test_image():
    # Create test directory if it doesn't exist
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple test image with text
    image_path = test_dir / "test.png"
    if not image_path.exists():
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a white image
        img = Image.new('RGB', (400, 100), color='white')
        d = ImageDraw.Draw(img)
        
        # Add text
        d.text((10,10), "Perplexica OCR Test", fill='black')
        img.save(image_path)
    
    return image_path

def test_health_check():
    """Test the health check endpoint."""
    response = httpx.get(f"{OCR_SERVICE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_metrics_endpoint():
    """Test the Prometheus metrics endpoint."""
    response = httpx.get(f"{OCR_SERVICE_URL}/metrics")
    assert response.status_code == 200
    assert b"ocr_requests_total" in response.content

def test_ocr_processing(test_image):
    """Test OCR processing with a test image."""
    files = {'file': open(test_image, 'rb')}
    response = httpx.post(f"{OCR_SERVICE_URL}/ocr", files=files)
    assert response.status_code == 200
    
    result = response.json()
    assert "texts" in result
    assert len(result["texts"]) > 0
    assert "Perplexica" in " ".join(result["texts"]) 