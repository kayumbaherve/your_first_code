"""
Room Scanning API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import aiofiles
import uuid
import os
from pathlib import Path
import logging

from database.connection import get_db
from database.models import RoomScan, User, Room
from modules.room_scanner import RoomScanner
from core.config import settings
from api.auth import get_current_user
from schemas.scanning import (
    RoomScanCreate, RoomScanResponse, RoomAnalysisResponse,
    ScanStatusResponse, MultiImageScanCreate
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize room scanner
room_scanner = RoomScanner()


@router.post("/upload", response_model=RoomScanResponse)
async def upload_room_image(
    file: UploadFile = File(...),
    room_id: Optional[int] = Form(None),
    scan_type: str = Form("single_image"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze a room image
    
    Args:
        file: Image file to analyze
        room_id: Optional room ID to associate with scan
        scan_type: Type of scan (single_image, multi_image, 360)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Room scan response with analysis results
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension {file_extension} not allowed"
            )
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = Path(settings.UPLOAD_DIR) / unique_filename
        
        # Ensure upload directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Create room scan record
        room_scan = RoomScan(
            user_id=current_user.id,
            room_id=room_id,
            scan_type=scan_type,
            original_image_path=str(file_path),
            processing_status="pending"
        )
        
        db.add(room_scan)
        db.commit()
        db.refresh(room_scan)
        
        # Start analysis in background (in production, use Celery or similar)
        try:
            # Perform room analysis
            analysis_results = room_scanner.analyze_room_image(str(file_path))
            
            # Update scan record with results
            room_scan.detected_objects = analysis_results.get("detected_objects", [])
            room_scan.room_dimensions = analysis_results.get("room_dimensions", {})
            room_scan.color_palette = analysis_results.get("color_palette", {})
            room_scan.lighting_analysis = analysis_results.get("lighting_analysis", {})
            room_scan.style_analysis = analysis_results.get("style_analysis", {})
            room_scan.confidence_scores = analysis_results.get("confidence_scores", {})
            room_scan.processing_status = "completed"
            
            db.commit()
            
            logger.info(f"Room scan {room_scan.id} completed successfully")
            
        except Exception as analysis_error:
            logger.error(f"Analysis failed for scan {room_scan.id}: {analysis_error}")
            room_scan.processing_status = "failed"
            room_scan.error_message = str(analysis_error)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Image analysis failed"
            )
        
        return RoomScanResponse(
            id=room_scan.id,
            scan_type=room_scan.scan_type,
            processing_status=room_scan.processing_status,
            original_image_path=room_scan.original_image_path,
            analysis_results=analysis_results,
            created_at=room_scan.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading room image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process image upload"
        )


@router.get("/results/{scan_id}", response_model=RoomAnalysisResponse)
async def get_scan_results(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get room scan analysis results
    
    Args:
        scan_id: ID of the room scan
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Detailed analysis results
    """
    try:
        # Get room scan
        room_scan = db.query(RoomScan).filter(
            RoomScan.id == scan_id,
            RoomScan.user_id == current_user.id
        ).first()
        
        if not room_scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room scan not found"
            )
        
        # Compile analysis results
        analysis_results = {
            "room_dimensions": room_scan.room_dimensions or {},
            "detected_objects": room_scan.detected_objects or [],
            "color_palette": room_scan.color_palette or {},
            "lighting_analysis": room_scan.lighting_analysis or {},
            "style_analysis": room_scan.style_analysis or {},
            "confidence_scores": room_scan.confidence_scores or {}
        }
        
        return RoomAnalysisResponse(
            scan_id=room_scan.id,
            processing_status=room_scan.processing_status,
            analysis_results=analysis_results,
            processing_time=room_scan.processing_time,
            error_message=room_scan.error_message,
            created_at=room_scan.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scan results"
        )


@router.get("/status/{scan_id}", response_model=ScanStatusResponse)
async def get_scan_status(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get processing status of a room scan
    
    Args:
        scan_id: ID of the room scan
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Current processing status
    """
    try:
        room_scan = db.query(RoomScan).filter(
            RoomScan.id == scan_id,
            RoomScan.user_id == current_user.id
        ).first()
        
        if not room_scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room scan not found"
            )
        
        return ScanStatusResponse(
            scan_id=room_scan.id,
            status=room_scan.processing_status,
            progress_percentage=100 if room_scan.processing_status == "completed" else 
                               0 if room_scan.processing_status == "pending" else 50,
            estimated_time_remaining=0 if room_scan.processing_status in ["completed", "failed"] else 30,
            error_message=room_scan.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scan status"
        )


@router.post("/multi-image", response_model=RoomScanResponse)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    room_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze multiple room images for better reconstruction
    
    Args:
        files: List of image files
        room_id: Optional room ID to associate with scan
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Room scan response with combined analysis
    """
    try:
        if len(files) > 10:  # Limit number of images
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 images allowed per multi-image scan"
            )
        
        uploaded_files = []
        
        # Process each file
        for file in files:
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} must be an image"
                )
            
            # Save file
            file_extension = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = Path(settings.UPLOAD_DIR) / unique_filename
            
            content = await file.read()
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            uploaded_files.append(str(file_path))
        
        # Create room scan record for multi-image scan
        room_scan = RoomScan(
            user_id=current_user.id,
            room_id=room_id,
            scan_type="multi_image",
            original_image_path=uploaded_files[0],  # Primary image
            image_metadata={"additional_images": uploaded_files[1:]},
            processing_status="pending"
        )
        
        db.add(room_scan)
        db.commit()
        db.refresh(room_scan)
        
        # Analyze all images and combine results
        try:
            combined_analysis = {}
            individual_analyses = []
            
            for file_path in uploaded_files:
                analysis = room_scanner.analyze_room_image(file_path)
                individual_analyses.append(analysis)
            
            # Combine analyses (simplified - in practice, use more sophisticated fusion)
            combined_analysis = individual_analyses[0]  # Use first as base
            
            # Average confidence scores
            if len(individual_analyses) > 1:
                avg_confidence = {}
                for key in combined_analysis.get("confidence_scores", {}):
                    scores = [a.get("confidence_scores", {}).get(key, 0) for a in individual_analyses]
                    avg_confidence[key] = sum(scores) / len(scores)
                combined_analysis["confidence_scores"] = avg_confidence
            
            # Update scan record
            room_scan.detected_objects = combined_analysis.get("detected_objects", [])
            room_scan.room_dimensions = combined_analysis.get("room_dimensions", {})
            room_scan.color_palette = combined_analysis.get("color_palette", {})
            room_scan.lighting_analysis = combined_analysis.get("lighting_analysis", {})
            room_scan.style_analysis = combined_analysis.get("style_analysis", {})
            room_scan.confidence_scores = combined_analysis.get("confidence_scores", {})
            room_scan.processing_status = "completed"
            
            db.commit()
            
            return RoomScanResponse(
                id=room_scan.id,
                scan_type=room_scan.scan_type,
                processing_status=room_scan.processing_status,
                original_image_path=room_scan.original_image_path,
                analysis_results=combined_analysis,
                created_at=room_scan.created_at
            )
            
        except Exception as analysis_error:
            logger.error(f"Multi-image analysis failed: {analysis_error}")
            room_scan.processing_status = "failed"
            room_scan.error_message = str(analysis_error)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Multi-image analysis failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing multi-image upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process multi-image upload"
        )


@router.post("/dimensions", response_model=dict)
async def estimate_room_dimensions(
    scan_id: int,
    reference_object_height: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Re-estimate room dimensions with additional reference information
    
    Args:
        scan_id: ID of the room scan
        reference_object_height: Known height of reference object in meters
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated dimension estimates
    """
    try:
        room_scan = db.query(RoomScan).filter(
            RoomScan.id == scan_id,
            RoomScan.user_id == current_user.id
        ).first()
        
        if not room_scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room scan not found"
            )
        
        # Re-analyze with reference information
        # This would use the reference object height to improve dimension estimates
        current_dimensions = room_scan.room_dimensions or {}
        
        if reference_object_height:
            # Recalculate dimensions using reference object
            # This is simplified - real implementation would re-process the image
            scale_factor = reference_object_height / 1.7  # Assume 1.7m default human height
            
            updated_dimensions = {
                "estimated_length": current_dimensions.get("estimated_length", 4) * scale_factor,
                "estimated_width": current_dimensions.get("estimated_width", 3.5) * scale_factor,
                "estimated_height": current_dimensions.get("estimated_height", 2.7) * scale_factor,
                "confidence": min(current_dimensions.get("confidence", 0.5) + 0.2, 0.9),
                "method": "reference_object_calibration"
            }
            
            # Update database
            room_scan.room_dimensions = updated_dimensions
            db.commit()
            
            return {
                "success": True,
                "updated_dimensions": updated_dimensions,
                "improvement": "Dimensions updated using reference object"
            }
        
        return {
            "success": False,
            "message": "No reference information provided",
            "current_dimensions": current_dimensions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error estimating room dimensions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to estimate room dimensions"
        )


@router.get("/history", response_model=List[RoomScanResponse])
async def get_scan_history(
    limit: int = 10,
    offset: int = 0,
    room_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's room scan history
    
    Args:
        limit: Maximum number of scans to return
        offset: Number of scans to skip
        room_id: Optional filter by room ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of room scans
    """
    try:
        query = db.query(RoomScan).filter(RoomScan.user_id == current_user.id)
        
        if room_id:
            query = query.filter(RoomScan.room_id == room_id)
        
        scans = query.order_by(RoomScan.created_at.desc()).offset(offset).limit(limit).all()
        
        scan_responses = []
        for scan in scans:
            analysis_results = {
                "room_dimensions": scan.room_dimensions or {},
                "detected_objects": scan.detected_objects or [],
                "color_palette": scan.color_palette or {},
                "lighting_analysis": scan.lighting_analysis or {},
                "style_analysis": scan.style_analysis or {},
                "confidence_scores": scan.confidence_scores or {}
            }
            
            scan_responses.append(RoomScanResponse(
                id=scan.id,
                scan_type=scan.scan_type,
                processing_status=scan.processing_status,
                original_image_path=scan.original_image_path,
                analysis_results=analysis_results,
                created_at=scan.created_at
            ))
        
        return scan_responses
        
    except Exception as e:
        logger.error(f"Error getting scan history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scan history"
        )


@router.delete("/{scan_id}")
async def delete_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a room scan and associated files
    
    Args:
        scan_id: ID of the room scan to delete
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success confirmation
    """
    try:
        room_scan = db.query(RoomScan).filter(
            RoomScan.id == scan_id,
            RoomScan.user_id == current_user.id
        ).first()
        
        if not room_scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room scan not found"
            )
        
        # Delete associated files
        try:
            if room_scan.original_image_path and os.path.exists(room_scan.original_image_path):
                os.remove(room_scan.original_image_path)
            
            # Delete additional images if multi-image scan
            if room_scan.image_metadata and "additional_images" in room_scan.image_metadata:
                for img_path in room_scan.image_metadata["additional_images"]:
                    if os.path.exists(img_path):
                        os.remove(img_path)
        except Exception as file_error:
            logger.warning(f"Error deleting files for scan {scan_id}: {file_error}")
        
        # Delete database record
        db.delete(room_scan)
        db.commit()
        
        return {"success": True, "message": "Room scan deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete room scan"
        )

