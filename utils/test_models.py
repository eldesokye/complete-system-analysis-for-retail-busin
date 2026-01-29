import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Importing VisitorData...")
from database.models import VisitorData
print("Importing SectionAnalytics...")
from database.models import SectionAnalytics
print("Importing HeatmapData...")

