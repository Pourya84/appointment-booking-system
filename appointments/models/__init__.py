"""
Models package for the appointments app.
Export all models for easy import from the package.
"""

from .service_type import ServiceType
from .schedule import Schedule
from .appointment import Appointment

__all__ = ["ServiceType", "Schedule", "Appointment"]