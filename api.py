# api.py - Zapier Webhook Endpoint for APS Pipeline
from flask import Flask, request, jsonify, send_file
from pathlib import Path
import pandas as pd
import sys
import os
from datetime import datetime
import tempfile

# Add engine directory to path
ENGINE_DIR = Path(__file__).parent / "engine"
sys.path.insert(0, str(ENGINE_DIR))

from aps_normalize import normalize_and_score
from aps_healthcheck import health_check
from aps_render import render_pdf

app = Flask(__name__)

# Configuration
OUTPUT_DIR = Path(__file__).parent / "APS_Market_Intelligence_Live"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_DIR = Path(tempfile.gettempdir()) / "aps_temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_endpoint():
    """Simple health check"""
    return jsonify({
        "status": "healthy",
        "service": "APS Pipeline API",
        "timestamp": datetime.now().isoformat()
    })

# Main processing endpoint
@app.route('/api/v1/process', methods=['POST'])
def process_csv():
    """
    Process uploaded CSV file and return PDF + scored CSV
    
    Expected input:
    - Method: POST
    - Content-Type: multipart/form-data
    - Field: 'file' (CSV file)
    
    Returns:
    - JSON with download links for PDF and CSV
    """
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "error": "No file provided",
                "message": "Please upload a CSV file using 'file' field"
            }), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                "error": "No file selected",
                "message": "Please select a file to upload"
            }), 400
        
        # Check if file is CSV
        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                "error": "Invalid file type",
                "message": "Only CSV files are supported"
            }), 400
        
        # Generate unique filename based on timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = Path(file.filename).stem
        safe_name = f"{base_name}_{timestamp}"
        
        # Save uploaded file temporarily
        temp_csv_path = TEMP_DIR / f"{safe_name}.csv"
        file.save(temp_csv_path)
        
        # Read and process CSV
        df = pd.read_csv(temp_csv_path, dtype=str, keep_default_na=False)
        
        if len(df) == 0:
            return jsonify({
                "error": "Empty CSV file",
                "message": "The uploaded CSV file contains no data"
            }), 400
        
        # Normalize and score
        df = normalize_and_score(df)
        
        # Health check
        hc = health_check(df)
        
        # Calculate overall quality
        quality_check = hc.get('18_Overall_Quality', {})
        quality_status = quality_check.get('status', 'UNKNOWN')
        quality_score = quality_check.get('value', 'N/A')
        
        # Save scored CSV
        scored_csv_path = OUTPUT_DIR / f"{safe_name}_scored.csv"
        df.to_csv(scored_csv_path, index=False, encoding='utf-8')
        
        # Generate PDF
        pdf_path = OUTPUT_DIR / f"{safe_name}_DEMO.pdf"
        render_pdf(df, pdf_path)
        
        # Clean up temporary file
        temp_csv_path.unlink(missing_ok=True)
        
        # Prepare response
        response = {
            "status": "success",
            "message": "CSV processed successfully",
            "input_records": len(df),
            "quality_status": quality_status,
            "quality_score": quality_score,
            "files": {
                "pdf": {
                    "filename": f"{safe_name}_DEMO.pdf",
                    "path": str(pdf_path),
                    "download_url": f"/api/v1/download/pdf/{safe_name}_DEMO.pdf"
                },
                "scored_csv": {
                    "filename": f"{safe_name}_scored.csv",
                    "path": str(scored_csv_path),
                    "download_url": f"/api/v1/download/csv/{safe_name}_scored.csv"
                }
            },
            "health_check_summary": {
                "total_checks": len(hc),
                "passed": sum(1 for c in hc.values() if c.get('status') == 'PASS'),
                "warnings": sum(1 for c in hc.values() if c.get('status') == 'WARN'),
                "failed": sum(1 for c in hc.values() if c.get('status') == 'FAIL')
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({
            "error": "Processing failed",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Download PDF endpoint
@app.route('/api/v1/download/pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    """Download generated PDF file"""
    try:
        pdf_path = OUTPUT_DIR / filename
        
        if not pdf_path.exists():
            return jsonify({
                "error": "File not found",
                "message": f"PDF file '{filename}' does not exist"
            }), 404
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({
            "error": "Download failed",
            "message": str(e)
        }), 500

# Download CSV endpoint
@app.route('/api/v1/download/csv/<filename>', methods=['GET'])
def download_csv(filename):
    """Download scored CSV file"""
    try:
        csv_path = OUTPUT_DIR / filename
        
        if not csv_path.exists():
            return jsonify({
                "error": "File not found",
                "message": f"CSV file '{filename}' does not exist"
            }), 404
        
        return send_file(
            csv_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({
            "error": "Download failed",
            "message": str(e)
        }), 500

# Process by file path (for Zapier file path trigger)
@app.route('/api/v1/process-path', methods=['POST'])
def process_by_path():
    """
    Process CSV file by providing file path
    
    Expected input:
    - Method: POST
    - Content-Type: application/json
    - Body: {"csv_path": "/path/to/file.csv"}
    
    Returns:
    - JSON with download links
    """
    
    try:
        data = request.get_json()
        
        if not data or 'csv_path' not in data:
            return jsonify({
                "error": "Missing csv_path",
                "message": "Please provide csv_path in request body"
            }), 400
        
        csv_path = Path(data['csv_path'])
        
        if not csv_path.exists():
            return jsonify({
                "error": "File not found",
                "message": f"CSV file not found at: {csv_path}"
            }), 404
        
        # Process CSV
        df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
        df = normalize_and_score(df)
        hc = health_check(df)
        
        # Generate output files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = csv_path.stem
        safe_name = f"{base_name}_{timestamp}"
        
        scored_csv_path = OUTPUT_DIR / f"{safe_name}_scored.csv"
        df.to_csv(scored_csv_path, index=False, encoding='utf-8')
        
        pdf_path = OUTPUT_DIR / f"{safe_name}_DEMO.pdf"
        render_pdf(df, pdf_path)
        
        quality_check = hc.get('18_Overall_Quality', {})
        
        return jsonify({
            "status": "success",
            "message": "CSV processed successfully",
            "input_records": len(df),
            "quality_status": quality_check.get('status', 'UNKNOWN'),
            "quality_score": quality_check.get('value', 'N/A'),
            "files": {
                "pdf": {
                    "filename": f"{safe_name}_DEMO.pdf",
                    "path": str(pdf_path),
                    "download_url": f"/api/v1/download/pdf/{safe_name}_DEMO.pdf"
                },
                "scored_csv": {
                    "filename": f"{safe_name}_scored.csv",
                    "path": str(scored_csv_path),
                    "download_url": f"/api/v1/download/csv/{safe_name}_scored.csv"
                }
            },
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": "Processing failed",
            "message": str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# Run server
if __name__ == '__main__':
    print("=" * 60)
    print("APS Pipeline API Server Starting...")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print("  GET  /health                    - Health check")
    print("  POST /api/v1/process            - Upload & process CSV")
    print("  POST /api/v1/process-path       - Process CSV by file path")
    print("  GET  /api/v1/download/pdf/<fn>  - Download PDF")
    print("  GET  /api/v1/download/csv/<fn>  - Download CSV")
    print("\nServer running on: http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)