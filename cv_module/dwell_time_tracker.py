
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DwellTimeTracker:
    """Tracks how long customers stay in a section"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # Stores active usage: {track_id: {'entry_time': datetime, 'last_seen': datetime}}
        self.active_sessions: Dict[int, Dict] = {}
        
        # Config
        self.max_dropout_seconds = 5.0  # If lost for > 5s, consider session ended
        self.min_dwell_time = 3.0       # Ignore sessions < 3s (noise)
        
    def update(self, objects: List[Dict], section_name: str, date_val, hour):
        """Update tracker with current frame detections"""
        current_time = datetime.now()
        current_track_ids = set()
        
        # Update/Create sessions
        for obj in objects:
            # Only track Persons (class_id 0) and valid track IDs
            if obj['class_id'] == 0 and obj['track_id'] != -1:
                tid = obj['track_id']
                current_track_ids.add(tid)
                
                if tid not in self.active_sessions:
                    # New session
                    self.active_sessions[tid] = {
                        'entry_time': current_time,
                        'last_seen': current_time,
                        'section': section_name
                    }
                else:
                    # Update existing
                    self.active_sessions[tid]['last_seen'] = current_time
                    
        # Check for ended sessions (dropout)
        to_remove = []
        for tid, session in self.active_sessions.items():
            if tid not in current_track_ids:
                time_since_seen = (current_time - session['last_seen']).total_seconds()
                
                if time_since_seen > self.max_dropout_seconds:
                    # Session ended
                    duration = (session['last_seen'] - session['entry_time']).total_seconds()
                    
                    if duration >= self.min_dwell_time:
                        logger.info(f"Customer #{tid} dwell time: {duration:.1f}s in {session['section']}")
                        
                        # Save to DB
                        self.db_manager.insert_dwell_time(
                            track_id=tid,
                            section_name=session['section'],
                            entry_time=session['entry_time'],
                            exit_time=session['last_seen'],
                            duration_seconds=duration,
                            date_val=date_val,
                            hour=hour
                        )
                    
                    to_remove.append(tid)
        
        for tid in to_remove:
            del self.active_sessions[tid]
