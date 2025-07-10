"""
Database models for the AI Interior Design Assistant
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import uuid


class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User preferences
    preferred_style = Column(String)  # modern, traditional, minimalist, etc.
    budget_range = Column(String)     # low, medium, high
    color_preferences = Column(JSON)  # Array of preferred colors
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    room_scans = relationship("RoomScan", back_populates="user")


class Project(Base):
    """Project model for managing interior design projects"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Project metadata
    project_type = Column(String)  # residential, commercial, etc.
    total_area = Column(Float)     # in square meters
    budget = Column(Float)
    status = Column(String, default="planning")  # planning, in_progress, completed
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    rooms = relationship("Room", back_populates="project")


class Room(Base):
    """Room model for individual room data"""
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    room_type = Column(String, nullable=False)  # living_room, bedroom, kitchen, etc.
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Room dimensions
    length = Column(Float)  # in meters
    width = Column(Float)   # in meters
    height = Column(Float)  # in meters
    area = Column(Float)    # calculated area
    
    # Room characteristics
    natural_light = Column(String)  # low, medium, high
    ceiling_type = Column(String)   # flat, vaulted, etc.
    floor_type = Column(String)     # hardwood, carpet, tile, etc.
    wall_color = Column(String)
    
    # Relationships
    project = relationship("Project", back_populates="rooms")
    room_scans = relationship("RoomScan", back_populates="room")
    furniture_items = relationship("FurnitureItem", back_populates="room")
    design_recommendations = relationship("DesignRecommendation", back_populates="room")


class RoomScan(Base):
    """Room scan model for storing scan results and analysis"""
    __tablename__ = "room_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    scan_type = Column(String, nullable=False)  # single_image, multi_image, 360
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Original image data
    original_image_path = Column(String, nullable=False)
    image_metadata = Column(JSON)  # EXIF data, camera info, etc.
    
    # Analysis results
    detected_objects = Column(JSON)     # Objects detected in the room
    room_dimensions = Column(JSON)      # Estimated dimensions
    color_palette = Column(JSON)       # Extracted color palette
    lighting_analysis = Column(JSON)   # Lighting conditions
    style_analysis = Column(JSON)      # Detected design style
    confidence_scores = Column(JSON)   # Confidence for each analysis
    
    # Processing status
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_time = Column(Float)  # Processing time in seconds
    error_message = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="room_scans")
    room = relationship("Room", back_populates="room_scans")


class FurnitureItem(Base):
    """Furniture item model for 3D objects and staging"""
    __tablename__ = "furniture_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # sofa, table, chair, etc.
    subcategory = Column(String)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 3D Model data
    model_path = Column(String)         # Path to 3D model file
    texture_path = Column(String)       # Path to texture files
    thumbnail_path = Column(String)     # Preview image
    
    # Physical properties
    dimensions = Column(JSON)           # width, height, depth
    materials = Column(JSON)            # Material properties
    colors = Column(JSON)               # Available colors
    price = Column(Float)
    brand = Column(String)
    
    # Positioning in room
    position = Column(JSON)             # x, y, z coordinates
    rotation = Column(JSON)             # rotation angles
    scale = Column(JSON)                # scale factors
    
    # Metadata
    style_tags = Column(JSON)           # modern, vintage, etc.
    room_compatibility = Column(JSON)   # Compatible room types
    is_custom = Column(Boolean, default=False)
    
    # Relationships
    room = relationship("Room", back_populates="furniture_items")


class DesignRecommendation(Base):
    """AI-generated design recommendations"""
    __tablename__ = "design_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    recommendation_type = Column(String, nullable=False)  # furniture, color, layout, style
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Recommendation data
    title = Column(String, nullable=False)
    description = Column(Text)
    confidence_score = Column(Float)
    priority = Column(Integer, default=1)  # 1=high, 2=medium, 3=low
    
    # Recommendation content
    recommended_items = Column(JSON)    # List of recommended furniture/colors/etc.
    reasoning = Column(Text)            # AI explanation for recommendation
    estimated_cost = Column(Float)
    implementation_difficulty = Column(String)  # easy, medium, hard
    
    # User feedback
    user_rating = Column(Integer)       # 1-5 stars
    user_feedback = Column(Text)
    is_implemented = Column(Boolean, default=False)
    
    # Relationships
    room = relationship("Room", back_populates="design_recommendations")


class VirtualStaging(Base):
    """Virtual staging results and configurations"""
    __tablename__ = "virtual_stagings"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Original and staged images
    original_image_path = Column(String, nullable=False)
    staged_image_path = Column(String)
    preview_image_path = Column(String)
    
    # Staging configuration
    staging_style = Column(String)      # modern, traditional, etc.
    furniture_list = Column(JSON)       # List of added furniture
    lighting_adjustments = Column(JSON) # Lighting modifications
    color_adjustments = Column(JSON)    # Color corrections
    
    # Processing info
    processing_status = Column(String, default="pending")
    processing_time = Column(Float)
    quality_settings = Column(JSON)
    
    # Metadata
    is_public = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)


class StyleTemplate(Base):
    """Pre-defined style templates for quick application"""
    __tablename__ = "style_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    style_category = Column(String, nullable=False)  # modern, traditional, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Template configuration
    color_palette = Column(JSON)        # Primary colors for this style
    furniture_preferences = Column(JSON) # Preferred furniture types
    material_preferences = Column(JSON) # Wood, metal, fabric preferences
    lighting_preferences = Column(JSON) # Lighting style preferences
    
    # Template metadata
    popularity_score = Column(Float, default=0.0)
    is_premium = Column(Boolean, default=False)
    preview_image_path = Column(String)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)

