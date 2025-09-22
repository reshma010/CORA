# DeepStream Pose Detection Server Communication

This document describes the server communication functionality for the DeepStream Pose Classification application.

## Overview

The pose monitor now supports sending detection data to a remote server via HTTP POST requests. Detection data is packaged with unit information and sent in configurable batches.

## Data Format

### Detection Package Structure
```json
{
  "package_id": "uuid-string",
  "unit_id": "jetson_pose_01", 
  "unit_name": "Jetson Xavier NX Pose Detection",
  "rtsp_uris": ["rtsp://camera1/stream", "rtsp://camera2/stream"],
  "timestamp": "2024-01-15T10:30:45.123456",
  "detection_count": 3,
  "detections": [
    {
      "timestamp": "2024-01-15T10:30:45.100000",
      "action_type": "walking",
      "confidence": 0.892,
      "person_id": 12,
      "frame_number": 1234,
      "normalized_bbox": {
        "x": 0.345,
        "y": 0.123, 
        "width": 0.234,
        "height": 0.567,
        "confidence": 0.95
      },
      "thumbnail": "base64-encoded-image-data",
      "tracking_info": {
        "is_tracked": true,
        "tracking_age": 45
      },
      "pose_scores": {
        "sitting_down": 0.02,
        "getting_up": 0.01,
        "sitting": 0.03,
        "standing": 0.05,
        "walking": 0.892,
        "jumping": 0.008
      }
    }
  ]
}
```

### Pose Classes
- `sitting_down`: Person transitioning from standing to sitting
- `getting_up`: Person transitioning from sitting to standing  
- `sitting`: Person in seated position
- `standing`: Person in standing position
- `walking`: Person in motion/walking
- `jumping`: Person jumping or in energetic motion

## Usage

### Basic Monitoring (No Server)
```bash
python3 pose_monitor.py --detailed --rate 1.0
```

### With Server Communication
```bash
# Start test server (in separate terminal)
python3 test_server.py --port 8080

# Start monitor with server
python3 pose_monitor.py \
  --server-url http://localhost:8080 \
  --unit-id jetson_pose_01 \
  --unit-name "Jetson Xavier NX Pose Detection" \
  --rtsp-uris rtsp://camera1/stream rtsp://camera2/stream \
  --send-thumbnails \
  --send-interval 3.0 \
  --batch-size 5 \
  --detailed \
  --rate 2.0
```

## Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--server-url` | HTTP/HTTPS endpoint for detection data | None |
| `--unit-id` | Unique identifier for this detection unit | "jetson_unit_01" |
| `--unit-name` | Human-readable name for this unit | "Jetson Pose Detection Unit" |
| `--rtsp-uris` | RTSP streams associated with this unit | [] |
| `--send-thumbnails` | Include base64 encoded thumbnails | False |
| `--send-interval` | Minimum seconds between transmissions | 5.0 |
| `--batch-size` | Detections to batch before sending | 10 |
| `--detailed` | Show detailed joint information | False |
| `--rate` | Display update rate in Hz | 2.0 |

## Server Implementation

### Endpoint Requirements
- **Method**: POST
- **Content-Type**: application/json
- **Body**: Detection package JSON (see format above)

### Expected Response
```json
{
  "status": "success", 
  "received_count": 3
}
```

### Error Handling
- Automatic retry with exponential backoff
- Configurable retry attempts (default: 3)
- Network timeout protection (default: 30s)
- Failed transmission logging

## Dependencies

### Python Packages
```bash
pip install requests numpy opencv-python sysv_ipc
```

### System Requirements
- DeepStream 6.x with pose classification pipeline
- System V shared memory support
- Network connectivity for server communication

## Architecture

```
DeepStream App  ->  Shared Memory  ->  Python Monitor  ->  HTTP Server
                       |                 | 
                 Person Detections  Detection Package
                 Joint Data        Unit Information  
                 Pose Classes      Batch Processing
```

## Performance Notes

- Shared memory read rate: ~25-26 FPS
- Detection processing: Real-time
- Server transmission: Batched (configurable)
- Memory usage: ~50MB for Python monitor
- Network bandwidth: ~1-10KB per detection (without thumbnails)

## Testing

Use the included test server to verify functionality:
```bash
# Terminal 1: Start test server
python3 test_server.py --port 8080

# Terminal 2: Run DeepStream app (if not running)
cd /home/jetson/v1DeepStreamPose
./app/deepstream-pose-classification-app -c configs/deepstream_pose_classification_config.yaml

# Terminal 3: Start monitor with server
python3 scripts/pose_monitor.py --server-url http://localhost:8080 --detailed

# Terminal 4: Check server logs for received data
```

## Troubleshooting

### Common Issues

1. **Import sysv_ipc error**: Install with `pip install sysv_ipc`
2. **Shared memory not found**: Ensure DeepStream app is running first
3. **Server connection failed**: Check URL and network connectivity
4. **No detections sent**: Verify pose detections are being generated

### Debugging

Enable detailed logging by running with verbose output:
```bash
python3 pose_monitor.py --server-url http://localhost:8080 --detailed --rate 0.5
```

Check shared memory status:
```bash
ipcs -m  # List shared memory segments
ipcs -s  # List semaphores
```

## Security Considerations

- Use HTTPS for production servers
- Implement authentication at server endpoint  
- Validate detection data on server side
- Consider rate limiting to prevent abuse
- Monitor network traffic for sensitive deployments