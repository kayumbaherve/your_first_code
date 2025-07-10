"""
Pydantic schemas for room scanning API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class ScanType(str, Enum):
    """Enum for scan types"""
    SINGLE_IMAGE = "single_image"
    MULTI_IMAGE = "multi_image"
    PANORAMA_360 = "360"


class ProcessingStatus(str, Enum):
    """Enum for processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RoomScanCreate(BaseModel):
    """Schema for creating a room scan"""
    room_id: Optional[int] = None
    scan_type: ScanType = ScanType.SINGLE_IMAGE
    
    class Config:
        use_enum_values = True


class MultiImageScanCreate(BaseModel):
    """Schema for multi-image scan creation"""
    room_id: Optional[int] = None
    image_count: int = Field(..., ge=2, le=10, description="Number of images (2-10)")
    
    @validator('image_count')
    def validate_image_count(cls, v):
        if v < 2 or v > 10:
            raise ValueError('Image count must be between 2 and 10')
        return v


class ColorInfo(BaseModel):
    """Schema for color information"""
    hex: str = Field(..., regex=r'^#[0-9A-Fa-f]{6}$')
    rgb: List[int] = Field(..., min_items=3, max_items=3)
    hsv: List[float] = Field(..., min_items=3, max_items=3)
    percentage: float = Field(..., ge=0, le=100)
    color_name: str


class ColorPalette(BaseModel):
    """Schema for color palette analysis"""
    dominant_colors: List[ColorInfo]
    color_harmony: str
    temperature: str


class RoomDimensions(BaseModel):
    """Schema for room dimensions"""
    estimated_length: float = Field(..., ge=0, description="Room length in meters")
    estimated_width: float = Field(..., ge=0, description="Room width in meters")
    estimated_height: float = Field(..., ge=0, description="Room height in meters")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    method: str = Field(..., description="Method used for estimation")
    vanishing_points: Optional[List[List[int]]] = None
    human_scale_detected: bool = False


class DetectedObject(BaseModel):
    """Schema for detected objects in room"""
    class_name: str = Field(..., alias="class")
    confidence: float = Field(..., ge=0, le=1)
    bbox: List[int] = Field(..., min_items=4, max_items=4, description="Bounding box [x, y, width, height]")
    center: List[int] = Field(..., min_items=2, max_items=2, description="Center point [x, y]")
    
    class Config:
        allow_population_by_field_name = True


class LightingAnalysis(BaseModel):
    """Schema for lighting analysis"""
    overall_brightness: float = Field(..., ge=0, le=255)
    lighting_level: str
    contrast_ratio: float = Field(..., ge=0)
    brightness_distribution: str
    potential_light_sources: int = Field(..., ge=0)
    natural_light_detected: bool


class StyleAnalysis(BaseModel):
    """Schema for style analysis"""
    primary_style: str
    confidence: float = Field(..., ge=0, le=1)
    style_scores: Dict[str, float]
    style_indicators: List[str]


class ConfidenceScores(BaseModel):
    """Schema for confidence scores"""
    overall: float = Field(..., ge=0, le=1)
    dimensions: float = Field(..., ge=0, le=1)
    objects: float = Field(..., ge=0, le=1)
    colors: float = Field(..., ge=0, le=1)
    lighting: float = Field(..., ge=0, le=1)
    style: float = Field(..., ge=0, le=1)


class AnalysisResults(BaseModel):
    """Schema for complete analysis results"""
    room_dimensions: RoomDimensions
    detected_objects: List[DetectedObject]
    color_palette: ColorPalette
    lighting_analysis: LightingAnalysis
    style_analysis: StyleAnalysis
    confidence_scores: ConfidenceScores
    wall_analysis: Optional[Dict[str, Any]] = None
    floor_analysis: Optional[Dict[str, Any]] = None
    ceiling_analysis: Optional[Dict[str, Any]] = None
    spatial_layout: Optional[Dict[str, Any]] = None


class RoomScanResponse(BaseModel):
    """Schema for room scan response"""
    id: int
    scan_type: str
    processing_status: str
    original_image_path: str
    analysis_results: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RoomAnalysisResponse(BaseModel):
    """Schema for detailed analysis response"""
    scan_id: int
    processing_status: ProcessingStatus
    analysis_results: Dict[str, Any]
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        use_enum_values = True


class ScanStatusResponse(BaseModel):
    """Schema for scan status response"""
    scan_id: int
    status: ProcessingStatus
    progress_percentage: int = Field(..., ge=0, le=100)
    estimated_time_remaining: int = Field(..., ge=0, description="Seconds remaining")
    error_message: Optional[str] = None
    
    class Config:
        use_enum_values = True


class DimensionEstimateRequest(BaseModel):
    """Schema for dimension estimation request"""
    reference_object_height: Optional[float] = Field(None, gt=0, description="Height in meters")
    reference_object_type: Optional[str] = None
    manual_measurements: Optional[Dict[str, float]] = None


class DimensionEstimateResponse(BaseModel):
    """Schema for dimension estimation response"""
    success: bool
    updated_dimensions: Optional[RoomDimensions] = None
    improvement: Optional[str] = None
    message: Optional[str] = None
    current_dimensions: Optional[RoomDimensions] = None


class ScanHistoryFilter(BaseModel):
    """Schema for scan history filtering"""
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)
    room_id: Optional[int] = None
    scan_type: Optional[ScanType] = None
    status: Optional[ProcessingStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class ScanDeleteResponse(BaseModel):
    """Schema for scan deletion response"""
    success: bool
    message: str
    deleted_files: Optional[List[str]] = None


class ImageMetadata(BaseModel):
    """Schema for image metadata"""
    format: Optional[str] = None
    mode: Optional[str] = None
    size: Optional[List[int]] = None
    exif: Optional[Dict[str, Any]] = None
    file_size: Optional[int] = None
    upload_timestamp: Optional[datetime] = None


class ScanStatistics(BaseModel):
    """Schema for scan statistics"""
    total_scans: int
    completed_scans: int
    failed_scans: int
    average_processing_time: float
    most_common_style: str
    average_room_size: float
    success_rate: float = Field(..., ge=0, le=1)


class BatchScanRequest(BaseModel):
    """Schema for batch scan processing"""
    scan_ids: List[int] = Field(..., min_items=1, max_items=50)
    operation: str = Field(..., regex=r'^(reprocess|delete|export)$')
    parameters: Optional[Dict[str, Any]] = None


class BatchScanResponse(BaseModel):
    """Schema for batch scan response"""
    success: bool
    processed_count: int
    failed_count: int
    results: List[Dict[str, Any]]
    errors: List[str]


class ScanExportRequest(BaseModel):
    """Schema for scan export request"""
    scan_ids: List[int] = Field(..., min_items=1)
    export_format: str = Field(..., regex=r'^(json|csv|pdf)$')
    include_images: bool = False
    include_analysis: bool = True
    include_metadata: bool = True


class ScanExportResponse(BaseModel):
    """Schema for scan export response"""
    success: bool
    export_url: Optional[str] = None
    file_size: Optional[int] = None
    expires_at: Optional[datetime] = None
    message: Optional[str] = None

