#!/usr/bin/env python3
"""
Fixed Python monitor for DeepStream Pose Classification shared memory data
Sends individual detections with robot info to server for proper database storage
"""

import struct
import time
import sys
import signal
import json
import base64
import uuid
import requests
import cv2
import numpy as np
from datetime import datetime
from ctypes import *
import threading
from threading import Thread, Lock
import queue

# Shared memory constants (must match C header)
MAX_PERSONS = 10
MAX_JOINTS = 34
MAX_POSE_CLASSES = 6
SHM_KEY = 12345

# Pose class enumeration (matching actual model classes)
POSE_CLASSES = {
    0: "sitting_down",
    1: "getting_up",
    2: "sitting",
    3: "standing",
    4: "walking",
    5: "jumping"
}

# Duplicate detection filter with per-class cooldowns
class DuplicateFilter:
    def __init__(self, default_cooldown=60.0):
        """
        Initialize duplicate filter with configurable per-class cooldowns
        
        Args:
            default_cooldown: Default cooldown time in seconds (1 minute)
        """
        self.default_cooldown = default_cooldown
        
        # Per-class cooldown configuration (in seconds)
        self.class_cooldowns = {
            0: 30.0,   # sitting_down - shorter cooldown for transition poses
            1: 30.0,   # getting_up - shorter cooldown for transition poses  
            2: 120.0,  # sitting - longer cooldown for stable poses
            3: 120.0,  # standing - longer cooldown for stable poses
            4: 60.0,   # walking - medium cooldown
            5: 45.0,   # jumping - shorter cooldown for action poses
        }
        
        # Track last detection time per person per class
        # Structure: {person_id: {class_id: last_detection_time}}
        self.last_detections = {}
        
        # Cleanup old entries periodically
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
        self.max_person_age = 600    # 10 minutes
    
    def should_send_detection(self, person_id, pose_class, confidence_threshold=0.8):
        """
        Check if detection should be sent based on duplicate filtering rules
        
        Args:
            person_id: Unique identifier for the person
            pose_class: Pose class ID (0-5)
            confidence_threshold: Minimum confidence to consider sending
            
        Returns:
            bool: True if detection should be sent, False if filtered as duplicate
        """
        current_time = time.time()
        
        # Periodic cleanup of old entries
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time
        
        # Get cooldown period for this class
        cooldown = self.class_cooldowns.get(pose_class, self.default_cooldown)
        
        # Initialize person tracking if not exists
        if person_id not in self.last_detections:
            self.last_detections[person_id] = {}
        
        # Check if we have a recent detection for this person and class
        person_detections = self.last_detections[person_id]
        
        if pose_class in person_detections:
            last_detection_time = person_detections[pose_class]
            time_since_last = current_time - last_detection_time
            
            if time_since_last < cooldown:
                # Too recent, filter as duplicate
                return False
        
        # Update last detection time for this person and class
        person_detections[pose_class] = current_time
        return True
    
    def _cleanup_old_entries(self, current_time):
        """Remove old detection entries to prevent memory growth"""
        persons_to_remove = []
        
        for person_id, person_detections in self.last_detections.items():
            # Find the most recent detection for this person
            if person_detections:
                most_recent = max(person_detections.values())
                if current_time - most_recent > self.max_person_age:
                    persons_to_remove.append(person_id)
            else:
                persons_to_remove.append(person_id)
        
        # Remove old entries
        for person_id in persons_to_remove:
            del self.last_detections[person_id]
    
    def get_cooldown_for_class(self, pose_class):
        """Get the cooldown period for a specific pose class"""
        return self.class_cooldowns.get(pose_class, self.default_cooldown)
    
    def set_class_cooldown(self, pose_class, cooldown_seconds):
        """Set cooldown period for a specific pose class"""
        self.class_cooldowns[pose_class] = cooldown_seconds
    
    def get_stats(self):
        """Get filtering statistics"""
        total_persons = len(self.last_detections)
        total_class_entries = sum(len(detections) for detections in self.last_detections.values())
        
        return {
            "tracked_persons": total_persons,
            "total_class_entries": total_class_entries,
            "class_cooldowns": self.class_cooldowns.copy(),
            "last_cleanup": self.last_cleanup
        }

# Server communication configuration
class ServerConfig:
    def __init__(self, server_url=None, unit_id=None, unit_name=None, rtsp_uris=None, 
                 send_thumbnails=True, send_interval=1.0, batch_size=10, retry_attempts=3, timeout=5.0):
        self.server_url = server_url or "https://corabackend.onrender.com/api/detections"
        self.unit_id = unit_id or "JETSON_001"
        self.unit_name = unit_name or "DeepStream Pose Classifier"
        # Default to file input - can be overridden with --rtsp-uris argument
        self.rtsp_uris = rtsp_uris or ["file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_walk.mov"]
        self.send_thumbnails = send_thumbnails
        self.send_interval = send_interval
        self.batch_size = batch_size
        self.retry_attempts = retry_attempts
        self.timeout = timeout

class Joint3D(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float), 
        ("z", c_float),
        ("confidence", c_float),
        ("visible", c_bool)
    ]

class Joint2D(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("confidence", c_float),
        ("visible", c_bool)
    ]

class BoundingBox(Structure):
    _fields_ = [
        ("left", c_float),
        ("top", c_float),
        ("width", c_float),
        ("height", c_float),
        ("confidence", c_float)
    ]

class PersonDetection(Structure):
    _fields_ = [
        ("person_id", c_uint32),
        ("timestamp_us", c_uint64),
        ("frame_number", c_uint32),
        ("bbox", BoundingBox),
        ("joints_2d", Joint2D * MAX_JOINTS),
        ("joints_3d", Joint3D * MAX_JOINTS),
        ("pose_class", c_uint32),
        ("pose_confidence", c_float),
        ("pose_scores", c_float * MAX_POSE_CLASSES),
        ("is_tracked", c_bool),
        ("tracking_age", c_uint32),
        ("has_2d_pose", c_bool),
        ("has_3d_pose", c_bool),
        ("has_classification", c_bool),
        ("reserved", c_uint8 * 64)
    ]

class SharedMemoryData(Structure):
    _fields_ = [
        ("timestamp_us", c_uint64),
        ("frame_number", c_uint32),
        ("sequence_id", c_uint32),
        ("num_persons", c_uint32),
        ("pipeline_active", c_bool),
        ("fps", c_uint32),
        ("frame_width", c_uint32),
        ("frame_height", c_uint32),
        ("has_thumbnail", c_bool),
        ("thumbnail_width", c_uint32),
        ("thumbnail_height", c_uint32),
        ("thumbnail_size", c_uint32),
        ("current_thumbnail_index", c_uint32),
        ("thumbnail_buffer", (c_uint8 * (320 * 240 * 3)) * 100),  # THUMBNAIL_BUFFER_COUNT * THUMBNAIL_MAX_SIZE
        ("persons", PersonDetection * MAX_PERSONS),
        ("total_frames_processed", c_uint64),
        ("total_persons_detected", c_uint32),
        ("reserved", c_uint8 * 256)
    ]

class DetectionItem:
    """Single detection item for server transmission with robot context"""
    def __init__(self, person_detection, server_config, thumbnail=None):
        self.timestamp = datetime.fromtimestamp(person_detection.timestamp_us / 1000000.0).isoformat()
        self.action_type = POSE_CLASSES.get(person_detection.pose_class, "unknown")
        self.confidence = float(person_detection.pose_confidence)
        self.person_id = int(person_detection.person_id)
        self.frame_number = int(person_detection.frame_number)
        
        # Store robot context
        self.unit_id = server_config.unit_id
        self.unit_name = server_config.unit_name
        self.rtsp_uris = server_config.rtsp_uris.copy()
        
        # Normalized bounding box (0.0 to 1.0)
        self.normalized_bbox = {
            "x": float(person_detection.bbox.left),  # Will be normalized later
            "y": float(person_detection.bbox.top),   # Will be normalized later
            "width": float(person_detection.bbox.width),   # Will be normalized later
            "height": float(person_detection.bbox.height), # Will be normalized later
            "confidence": float(person_detection.bbox.confidence)
        }
        
        # Thumbnail as base64 encoded string
        self.thumbnail = thumbnail if thumbnail else None
        
        # Additional metadata
        self.tracking_info = {
            "is_tracked": bool(person_detection.is_tracked),
            "tracking_age": int(person_detection.tracking_age)
        }
        
        # Pose scores for all classes
        self.pose_scores = {}
        for i in range(MAX_POSE_CLASSES):
            class_name = POSE_CLASSES.get(i, f"class_{i}")
            self.pose_scores[class_name] = float(person_detection.pose_scores[i])
    
    def normalize_bbox(self, frame_width, frame_height):
        """Normalize bounding box coordinates to 0.0-1.0 range"""
        if frame_width > 0 and frame_height > 0:
            self.normalized_bbox["x"] = self.normalized_bbox["x"] / frame_width
            self.normalized_bbox["y"] = self.normalized_bbox["y"] / frame_height  
            self.normalized_bbox["width"] = self.normalized_bbox["width"] / frame_width
            self.normalized_bbox["height"] = self.normalized_bbox["height"] / frame_height
    
    def to_server_format(self):
        """Convert to server expected format: robot info + single detection"""
        return {
            # Robot context - needed to find/create robot
            "unit_id": self.unit_id,
            "unit_name": self.unit_name,
            "rtsp_uris": self.rtsp_uris,
            "timestamp": datetime.now().isoformat(),
            
            # Single detection in array format (server expects array)
            "detections": [{
                "timestamp": self.timestamp,
                "action_type": self.action_type,
                "confidence": self.confidence,
                "person_id": self.person_id,
                "frame_number": self.frame_number,
                "normalized_bbox": self.normalized_bbox,
                "thumbnail": self.thumbnail,
                "tracking_info": self.tracking_info,
                "pose_scores": self.pose_scores
            }]
        }

class PoseMonitor:
    def __init__(self, server_config=None):
        self.running = True
        self.shm_id = None
        self.shm_data = None
        self.last_sequence_id = 0
        
        # Server communication setup
        self.server_config = server_config
        self.detection_queue = queue.Queue() if server_config else None
        self.send_thread = None
        
        # Statistics
        self.stats = {
            "total_detections": 0,
            "sent_packages": 0,
            "send_errors": 0,
            "filtered_duplicates": 0,
            "last_send_time": None
        }
        
        # Duplicate filtering with per-class cooldowns
        self.duplicate_filter = DuplicateFilter()
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        print(f"\nReceived signal {signum}, shutting down...")
        self.running = False
    
    def connect_shared_memory(self):
        """Connect to the shared memory segment"""
        try:
            import sysv_ipc
            
            # Connect to existing shared memory
            self.shm = sysv_ipc.SharedMemory(SHM_KEY)
            print(f"Connected to shared memory (ID: {self.shm.id})")
            return True
            
        except ImportError:
            print("Error: sysv_ipc module not found. Install with: pip install sysv_ipc")
            return False
        except sysv_ipc.ExistentialError:
            print(f"Error: Shared memory with key {SHM_KEY} not found. Make sure DeepStream app is running.")
            return False
        except Exception as e:
            print(f"Error connecting to shared memory: {e}")
            return False
    
    def read_detection_data(self):
        """Read detection data from shared memory"""
        try:
            # Read raw data from shared memory
            raw_data = self.shm.read()
            
            # Parse into structure
            data = SharedMemoryData.from_buffer_copy(raw_data)
            return data
            
        except Exception as e:
            print(f"Error reading shared memory: {e}")
            return None
    
    def print_detection_summary(self, data):
        """Print a summary of detection data"""
        print(f"\n=== Frame {data.frame_number} (Seq: {data.sequence_id}) ===")
        print(f"Timestamp: {data.timestamp_us} us")
        print(f"Persons detected: {data.num_persons}")
        print(f"Pipeline active: {data.pipeline_active}")
        print(f"FPS: {data.fps}")
        print(f"Frame size: {data.frame_width}x{data.frame_height}")
        print(f"Total frames processed: {data.total_frames_processed}")
        
        # Show filtering statistics if server communication is enabled
        if self.server_config:
            filter_stats = self.duplicate_filter.get_stats()
            print(f"Server Stats: {self.stats['total_detections']} sent, "
                  f"{self.stats['filtered_duplicates']} filtered, "
                  f"{filter_stats['tracked_persons']} tracked persons")
        
        for i in range(min(data.num_persons, MAX_PERSONS)):
            person = data.persons[i]
            pose_name = POSE_CLASSES.get(person.pose_class, "unknown")
            
            print(f"  Person {i+1}:")
            print(f"    ID: {person.person_id}")
            print(f"    Pose: {pose_name} (confidence: {person.pose_confidence:.3f})")
            print(f"    Bbox: ({person.bbox.left:.1f}, {person.bbox.top:.1f}) "
                  f"{person.bbox.width:.1f}x{person.bbox.height:.1f} "
                  f"(conf: {person.bbox.confidence:.3f})")
            print(f"    Tracked: {person.is_tracked} (age: {person.tracking_age})")
            print(f"    Has 2D pose: {person.has_2d_pose}")
            print(f"    Has 3D pose: {person.has_3d_pose}")
            print(f"    Has classification: {person.has_classification}")
            
            # Show pose classification scores
            if person.has_classification:
                print("    Pose scores:")
                for j in range(MAX_POSE_CLASSES):
                    if person.pose_scores[j] > 0.01:  # Only show significant scores
                        class_name = POSE_CLASSES.get(j, f"class_{j}")
                        print(f"      {class_name}: {person.pose_scores[j]:.3f}")
    
    def print_joint_data(self, person, joint_type="2d"):
        """Print detailed joint data for a person"""
        joints = person.joints_2d if joint_type == "2d" else person.joints_3d
        
        print(f"    {joint_type.upper()} Joints:")
        joint_names = [
            "pelvis", "left_hip", "right_hip", "torso", "left_knee", "right_knee",
            "neck", "left_ankle", "right_ankle", "left_big_toe", "right_big_toe",
            "left_small_toe", "right_small_toe", "left_heel", "right_heel", "nose",
            "left_eye", "right_eye", "left_ear", "right_ear", "left_shoulder",
            "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist",
            "left_pinky_knuckle", "right_pinky_knuckle", "left_middle_tip", "right_middle_tip",
            "left_thumb_tip", "right_thumb_tip", "left_index_tip", "right_index_tip"
        ]
        
        for i, joint in enumerate(joints[:len(joint_names)]):
            if joint.visible and joint.confidence > 0.1:
                name = joint_names[i] if i < len(joint_names) else f"joint_{i}"
                if joint_type == "2d":
                    print(f"      {name}: ({joint.x:.1f}, {joint.y:.1f}) conf: {joint.confidence:.3f}")
                else:
                    print(f"      {name}: ({joint.x:.3f}, {joint.y:.3f}, {joint.z:.3f}) conf: {joint.confidence:.3f}")
    
    def monitor_loop(self, detailed=False, update_rate=2.0):
        """Main monitoring loop"""
        print("Starting pose detection monitor...")
        print("Press Ctrl+C to exit")
        
        if not self.connect_shared_memory():
            return False
        
        # Start server communication if configured
        if self.server_config:
            self.start_server_communication()
        
        last_update_time = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Read detection data
                data = self.read_detection_data()
                if data is None:
                    time.sleep(0.1)
                    continue
                
                # Check if data has been updated
                if data.sequence_id != self.last_sequence_id:
                    self.last_sequence_id = data.sequence_id
                    
                    # Send detections to server if configured
                    if self.server_config and data.num_persons > 0:
                        # Generate thumbnail from shared memory data
                        thumbnail_data = self.generate_thumbnail(data)
                        
                        for i in range(data.num_persons):
                            person = data.persons[i]
                            # Add detection to server queue with thumbnail data
                            self.add_detection_for_server(person, data.frame_width, data.frame_height, thumbnail_data)
                    
                    # Print summary at specified rate
                    if current_time - last_update_time >= (1.0 / update_rate):
                        self.print_detection_summary(data)
                        
                        # Print detailed joint data if requested
                        if detailed and data.num_persons > 0:
                            person = data.persons[0]  # Show first person
                            if person.has_2d_pose:
                                self.print_joint_data(person, "2d")
                            if person.has_3d_pose:
                                self.print_joint_data(person, "3d")
                        
                        last_update_time = current_time
                
                time.sleep(0.01)  # Small sleep to prevent excessive CPU usage
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(1)
        
        print("Monitor stopped")
        return True

    def start_server_communication(self):
        """Start the server communication thread"""
        if not self.server_config:
            print("No server configuration provided")
            return False
            
        if self.send_thread and self.send_thread.is_alive():
            print("Server communication thread already running")
            return False
            
        self.send_thread = threading.Thread(target=self._server_send_loop, daemon=True)
        self.send_thread.start()
        print(f"Started server communication to {self.server_config.server_url}")
        return True
    
    def _server_send_loop(self):
        """Server communication thread loop - sends individual detections"""
        while self.running:
            try:
                # Check for new detections with timeout
                try:
                    detection_item = self.detection_queue.get(timeout=1.0)
                    self._send_individual_detection(detection_item)
                    self.detection_queue.task_done()
                except queue.Empty:
                    pass
                    
            except Exception as e:
                print(f"Error in server send loop: {e}")
                time.sleep(1)
    
    def _send_individual_detection(self, detection_item):
        """Send individual detection to server with robot context"""
        try:
            # Convert to server format
            detection_data = detection_item.to_server_format()
            
            for attempt in range(self.server_config.retry_attempts):
                try:
                    response = requests.post(
                        self.server_config.server_url,
                        json=detection_data,  # Use json parameter for proper content-type
                        timeout=self.server_config.timeout
                    )
                    
                    if response.status_code in [200, 201]:  # Accept both 200 and 201
                        self.stats["sent_packages"] += 1
                        self.stats["last_send_time"] = datetime.now().isoformat()
                        print(f"Successfully sent detection: Robot {detection_item.unit_id} - Person {detection_item.person_id} - {detection_item.action_type} (conf: {detection_item.confidence:.3f})")
                        break
                    else:
                        print(f"Server responded with status {response.status_code}: {response.text}")
                        if attempt == self.server_config.retry_attempts - 1:
                            self.stats["send_errors"] += 1
                        
                except requests.exceptions.RequestException as e:
                    print(f"Network error for detection {detection_item.unit_id}-{detection_item.person_id} (attempt {attempt + 1}): {e}")
                    if attempt == self.server_config.retry_attempts - 1:
                        self.stats["send_errors"] += 1
                    time.sleep(1)  # Wait before retry
                        
        except Exception as e:
            print(f"Error sending individual detection: {e}")
            self.stats["send_errors"] += 1
    
    def add_detection_for_server(self, person_detection, frame_width=1920, frame_height=1080, thumbnail_data=None):
        """Add a detection to the server queue with duplicate filtering"""
        if not self.server_config or not self.detection_queue:
            return
            
        try:
            # Apply duplicate filtering
            should_send = self.duplicate_filter.should_send_detection(
                person_detection.person_id,
                person_detection.pose_class,
                person_detection.pose_confidence
            )
            
            if not should_send:
                self.stats["filtered_duplicates"] += 1
                return
            
            # Create detection item with robot context
            detection_item = DetectionItem(person_detection, self.server_config, thumbnail_data)
            
            # Normalize bounding box coordinates
            detection_item.normalize_bbox(frame_width, frame_height)
            
            # Add to queue
            self.detection_queue.put(detection_item)
            self.stats["total_detections"] += 1
            
            # Log detection with cooldown info
            pose_name = POSE_CLASSES.get(person_detection.pose_class, "unknown")
            cooldown = self.duplicate_filter.get_cooldown_for_class(person_detection.pose_class)
            print(f"Queued detection: Robot {self.server_config.unit_id} - Person {person_detection.person_id} - {pose_name} "
                  f"(conf: {person_detection.pose_confidence:.3f}, cooldown: {cooldown}s)")
            
        except Exception as e:
            print(f"Error adding detection to server queue: {e}")
    
    def generate_thumbnail(self, shared_data):
        """Generate base64 thumbnail from shared memory frame data"""
        if not self.server_config.send_thumbnails:
            return None
            
        try:
            if not shared_data.has_thumbnail or shared_data.thumbnail_size == 0:
                return None
                
            # Get the most recent thumbnail from the circular buffer
            current_index = (shared_data.current_thumbnail_index - 1) % 100  # THUMBNAIL_BUFFER_COUNT
            if current_index < 0:
                current_index = 99
                
            # Extract thumbnail data from shared memory circular buffer
            thumbnail_bytes = bytes(shared_data.thumbnail_buffer[current_index][:shared_data.thumbnail_size])
            
            # Convert raw RGB data to a simple encoded format
            # For a proper implementation, you'd convert RGB to JPEG/PNG
            # For now, we'll encode the raw data as base64
            return base64.b64encode(thumbnail_bytes).decode('utf-8')
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
    
    def get_stats(self):
        """Get communication statistics"""
        return self.stats.copy()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor DeepStream Pose Classification shared memory")
    parser.add_argument("--detailed", "-d", action="store_true", help="Show detailed joint data")
    parser.add_argument("--rate", "-r", type=float, default=2.0, help="Update rate in Hz (default: 2.0)")
    
    # Server configuration options
    parser.add_argument("--server-url", default="https://corabackend.onrender.com/api/detections", help="Server URL for sending detection data")
    parser.add_argument("--unit-id", default="jetson_unit_01", help="Unit identifier")
    parser.add_argument("--unit-name", default="Jetson Pose Detection Unit", help="Unit display name")
    parser.add_argument("--rtsp-uris", nargs='*', default=[], help="RTSP URIs for this unit")
    parser.add_argument("--send-thumbnails", action="store_true", help="Send thumbnails with detections")
    parser.add_argument("--send-interval", type=float, default=5.0, help="Send interval in seconds")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for sending detections")
    
    # Duplicate filtering options
    parser.add_argument("--cooldown-sitting-down", type=float, default=30.0, help="Cooldown for sitting_down poses (seconds)")
    parser.add_argument("--cooldown-getting-up", type=float, default=30.0, help="Cooldown for getting_up poses (seconds)")  
    parser.add_argument("--cooldown-sitting", type=float, default=120.0, help="Cooldown for sitting poses (seconds)")
    parser.add_argument("--cooldown-standing", type=float, default=120.0, help="Cooldown for standing poses (seconds)")
    parser.add_argument("--cooldown-walking", type=float, default=60.0, help="Cooldown for walking poses (seconds)")
    parser.add_argument("--cooldown-jumping", type=float, default=45.0, help="Cooldown for jumping poses (seconds)")
    parser.add_argument("--default-cooldown", type=float, default=60.0, help="Default cooldown for unknown poses (seconds)")
    
    args = parser.parse_args()
    
    # Always create server configuration with default URL
    server_config = ServerConfig(
        server_url=args.server_url,
        unit_id=args.unit_id,
        unit_name=args.unit_name,
        rtsp_uris=args.rtsp_uris,
        send_thumbnails=args.send_thumbnails,
        send_interval=args.send_interval,
        batch_size=args.batch_size
    )
    print(f"Server configuration:")
    print(f"  URL: {server_config.server_url}")
    print(f"  Unit: {server_config.unit_id} ({server_config.unit_name})")
    print(f"  RTSP URIs: {server_config.rtsp_uris}")
    print(f"  Send thumbnails: {server_config.send_thumbnails}")
    print(f"  Send interval: {server_config.send_interval}s")
    print(f"  Batch size: {server_config.batch_size}")
    
    monitor = PoseMonitor(server_config)
    
    # Configure cooldown periods for server communication
    monitor.duplicate_filter.set_class_cooldown(0, args.cooldown_sitting_down)
    monitor.duplicate_filter.set_class_cooldown(1, args.cooldown_getting_up)
    monitor.duplicate_filter.set_class_cooldown(2, args.cooldown_sitting)
    monitor.duplicate_filter.set_class_cooldown(3, args.cooldown_standing)
    monitor.duplicate_filter.set_class_cooldown(4, args.cooldown_walking)
    monitor.duplicate_filter.set_class_cooldown(5, args.cooldown_jumping)
    monitor.duplicate_filter.default_cooldown = args.default_cooldown
    
    print(f"\n⏱️  Duplicate filtering cooldowns:")
    for class_id, class_name in POSE_CLASSES.items():
        cooldown = monitor.duplicate_filter.get_cooldown_for_class(class_id)
        print(f"  {class_name}: {cooldown}s")
    
    try:
        monitor.monitor_loop(detailed=args.detailed, update_rate=args.rate)
    finally:
        print(f"\nServer communication statistics:")
        stats = monitor.get_stats()
        filter_stats = monitor.duplicate_filter.get_stats()
        print(f"  Total detections sent: {stats['total_detections']}")
        print(f"  Filtered duplicates: {stats['filtered_duplicates']}")
        print(f"  Sent packages: {stats['sent_packages']}")
        print(f"  Send errors: {stats['send_errors']}")
        print(f"  Tracked persons: {filter_stats['tracked_persons']}")
        print(f"  Last send: {stats['last_send_time']}")

if __name__ == "__main__":
    main()