"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Core schemas for the UMKM business prediction app

class SalesRecord(BaseModel):
    """
    Historical sales records
    Collection: "salesrecord"
    """
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    revenue: float = Field(..., ge=0, description="Daily revenue")
    units: Optional[int] = Field(None, ge=0, description="Units sold (optional)")
    note: Optional[str] = Field(None, description="Optional note")

class Prediction(BaseModel):
    """
    Predictions made by the system
    Collection: "prediction"
    """
    method: str = Field(..., description="Forecasting method, e.g., 'sma' | 'ema'")
    window: int = Field(..., ge=1, le=90, description="Window size used by the method")
    input_points: List[float] = Field(..., description="Historical revenue points used for prediction")
    predicted_value: float = Field(..., ge=0, description="Predicted next revenue value")

class Profile(BaseModel):
    """
    UMKM profile info
    Collection: "profile"
    """
    business_name: str = Field(..., description="UMKM name")
    owner_name: str = Field(..., description="Owner name")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    address: Optional[str] = Field(None, description="Business address")
    category: Optional[str] = Field(None, description="Business category, e.g., F&B")
    description: Optional[str] = Field(None, description="Short business description")

# Example schemas kept for reference (not used directly by app but safe to keep)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
