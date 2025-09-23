# Robot Detection API

This API handles detection data from DeepStream Pose Classification robots. It provides endpoints for receiving, storing, and querying pose detection data.

## Overview

The DeepStream Pose Classification system monitors camera feeds and detects human poses/actions. When significant actions are detected (sitting, standing, walking, etc.), the system sends detection packages to this API for storage and analysis.

## API Endpoints

### 1. Receive Detection Data
**POST** `/api/detections`

Receives detection packages from robot units.

**Request Body:**
```json
{
  "package_id": "unique-package-identifier",
  "unit_id": "jetson_unit_01",
  "unit_name": "Jetson Pose Detection Unit",
  "rtsp_uris": ["rtsp://camera1.local/stream", "rtsp://camera2.local/stream"],
  "timestamp": "2025-09-20T22:00:00.000Z",
  "detection_count": 2,
  "detections": [
    {
      "timestamp": "2025-09-20T22:00:00.000Z",
      "action_type": "sitting_down",
      "confidence": 0.85,
      "person_id": 123,
      "frame_number": 5467,
      "normalized_bbox": {
        "x": 0.25,
        "y": 0.30,
        "width": 0.20,
        "height": 0.40,
        "confidence": 0.92
      },
      "thumbnail": "base64-encoded-image-data",
      "tracking_info": {
        "is_tracked": true,
        "tracking_age": 45
      },
      "pose_scores": {
        "sitting_down": 0.85,
        "getting_up": 0.05,
        "sitting": 0.03,
        "standing": 0.02,
        "walking": 0.03,
        "jumping": 0.02
      }
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Detection package processed successfully",
  "data": {
    "package_id": "unique-package-identifier",
    "unit_id": "jetson_unit_01",
    "processed_detections": 2,
    "total_detections": 2,
    "stats": {
      "total_detections": 2,
      "action_counts": {
        "sitting_down": 1,
        "walking": 1
      },
      "avg_confidence": 0.83
    }
  }
}
```

### 2. Get Detection Data by Unit
**GET** `/api/detections/:unitId`

Retrieves detection data for a specific robot unit. Requires authentication.

**Query Parameters:**
- `hours` (optional): Time range in hours (default: 24)
- `limit` (optional): Maximum number of packages to return (default: 100)
- `action_type` (optional): Filter by specific action type

**Example:** `GET /api/detections/jetson_unit_01?hours=12&action_type=sitting_down`

### 3. Get Detection Summary
**GET** `/api/detections/:unitId/summary`

Get aggregated statistics for a unit. Requires authentication.

**Query Parameters:**
- `hours` (optional): Time range in hours (default: 24)

### 4. Get Active Units
**GET** `/api/detections/units/active`

Get list of all robot units that have sent data recently. Requires authentication.

**Query Parameters:**
- `hours` (optional): Time range to consider "active" (default: 24)

### 5. Mark Package as Processed
**PUT** `/api/detections/:packageId/processed`

Mark a detection package as processed. Requires authentication.

## Action Types

The system recognizes these human pose/action types:

- `sitting_down` - Person transitioning from standing to sitting
- `getting_up` - Person transitioning from sitting to standing  
- `sitting` - Person in seated position
- `standing` - Person in standing position
- `walking` - Person walking/moving
- `jumping` - Person jumping or in jumping motion
- `unknown` - Unrecognized action/pose

## Duplicate Detection

The API automatically handles duplicate packages using the `package_id` field. If the same package ID is sent multiple times, subsequent submissions will be ignored with a "duplicate" status.

## Data Validation

All incoming detection data is validated for:

- Required fields presence
- Data type correctness
- Value range validation (confidences 0-1, normalized coordinates 0-1)
- Valid action types
- Proper timestamp formats

Invalid detections within a package are filtered out rather than rejecting the entire package.

## Testing

Use the provided test script to verify the API:

```bash
# Test locally
node test-detection-api.js

# Test against production
node test-detection-api.js --server https://corabackend.onrender.com

# Or with environment variable
SERVER_URL=https://corabackend.onrender.com node test-detection-api.js
```

## Robot Integration

The DeepStream Pose Classification Python script should:

1. Generate unique package IDs (UUID recommended)
2. Send detection packages to `POST /api/detections`
3. Include all required fields in the request body
4. Handle HTTP errors gracefully with retry logic
5. Use the duplicate filtering system to avoid spam

## Security Considerations

**For Production:**

1. **Authentication**: The robot endpoints should use API keys or JWT tokens
2. **Rate Limiting**: Implement per-unit rate limiting  
3. **Input Sanitization**: Additional validation for thumbnails and metadata
4. **HTTPS Only**: Ensure all communication uses HTTPS
5. **Network Security**: Restrict access to detection endpoints by IP/network

## Database Schema

Detection packages are stored in MongoDB with the following structure:

- `package_id`: Unique identifier for the package
- `unit_id`: Robot unit identifier
- `unit_name`: Human-readable unit name
- `rtsp_uris`: Array of camera stream URIs
- `timestamp`: Package creation timestamp
- `detection_count`: Number of detections in package
- `detections`: Array of individual detection objects
- `processed`: Boolean flag for processing status
- `createdAt`, `updatedAt`: Automatic timestamps

Indexes are created on frequently queried fields for optimal performance.