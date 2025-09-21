# CORA Robot API Testing

The CORA backend now includes a comprehensive Robot model with the following features:

##  Robot Model Features

### Core Robot Information
- **robotId**: Unique identifier (format: CORA-XXXX)
- **name**: Human-readable robot name
- **model**: Robot hardware model
- **version**: Hardware, software, and firmware versions
- **status**: online, offline, maintenance, error, deploying
- **location**: GPS coordinates and zone information
- **owner**: Reference to User who owns the robot

### RTSP Streams Array
Each robot can have multiple RTSP streams with:
- **id**: Stream identifier
- **name**: Stream name
- **url**: RTSP URL (validated format)
- **isActive**: Stream status
- **quality**: low, medium, high, ultra
- **resolution**: width/height
- **frameRate**: FPS setting

### Detections Array
Each detection includes:
- **id**: Detection identifier
- **timestamp**: When detection occurred
- **objectType**: person, vehicle, animal, object, anomaly, other
- **confidence**: 0-1 confidence score
- **boundingBox**: x, y, width, height coordinates
- **location**: GPS coordinates of detection
- **imageUrl**: Optional image URL
- **metadata**: Additional detection data

### Health Monitoring
- **batteryLevel**: 0-100%
- **temperature**: Current temperature
- **cpuUsage**: 0-100%
- **memoryUsage**: 0-100%
- **diskUsage**: 0-100%
- **networkStatus**: connected, disconnected, limited
- **lastHealthCheck**: Timestamp

##  API Endpoints

All robot endpoints require authentication (JWT token).

### Robot Management
- `GET /api/robots` - Get all robots for user
- `POST /api/robots` - Create new robot
- `GET /api/robots/:id` - Get specific robot
- `PUT /api/robots/:id` - Update robot
- `DELETE /api/robots/:id` - Delete robot

### Robot Record Detections (Individual Robot Management)
- `GET /api/robots/:id/detections` - Get robot detections by MongoDB ID (paginated)
- `POST /api/robots/:id/detections` - Add single detection to robot by MongoDB ID

### Robot Unit Detections (Unit Data Processing)
- `POST /api/robots/detections` - Receive batch detection data from robot units
- `GET /api/robots/detections/active` - Get all active robot units
- `GET /api/robots/detections/:unitId` - Get detection data for specific robot unit
- `GET /api/robots/detections/:unitId/summary` - Get detection summary for robot unit

### Streams
- `POST /api/robots/:id/streams` - Add RTSP stream

### Health
- `PUT /api/robots/:id/health` - Update health status

##  Example Usage

### Create a Robot
```bash
curl -X POST http://localhost:5002/api/robots \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "robotId": "CORA-001A",
    "name": "Security Bot Alpha",
    "model": "CORA-X1",
    "location": {
      "name": "Main Entrance",
      "coordinates": {
        "latitude": 40.7128,
        "longitude": -74.0060
      },
      "zone": "Building A"
    },
    "status": "online"
  }'
```

### Add Single Detection (to Robot Record)
```bash
curl -X POST http://localhost:5002/api/robots/ROBOT_MONGO_ID/detections \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": "det_001",
    "objectType": "person",
    "confidence": 0.89,
    "boundingBox": {
      "x": 100,
      "y": 150,
      "width": 200,
      "height": 300
    },
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }'
```

### Submit Robot Unit Detection Data (Batch Processing)
```bash
curl -X POST http://localhost:5002/api/robots/detections \
  -H "Content-Type: application/json" \
  -d '{
    "unit_id": "CORA-001A",
    "unit_name": "Security Bot Alpha",
    "rtsp_uris": ["rtsp://192.168.1.100:554/stream"],
    "detections": [
      {
        "timestamp": "2023-10-15T10:30:00Z",
        "action_type": "sitting_down",
        "confidence": 0.89,
        "person_id": 1,
        "frame_number": 12345,
        "normalized_bbox": {
          "x": 0.1,
          "y": 0.15,
          "width": 0.2,
          "height": 0.3,
          "confidence": 0.85
        }
      }
    ]
  }'
```

### Add RTSP Stream
```bash
curl -X POST http://localhost:5002/api/robots/ROBOT_ID/streams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "id": "stream_001",
    "name": "Front Camera",
    "url": "rtsp://192.168.1.100:554/stream",
    "quality": "high",
    "resolution": {
      "width": 1920,
      "height": 1080
    },
    "frameRate": 30
  }'
```

##  Security Features

- **User-based access**: Users can only manage their own robots (unless admin)
- **Input validation**: All inputs are validated and sanitized
- **MongoDB injection protection**: Using Mongoose with proper validation
- **Rate limiting**: Prevents API abuse
- **JWT authentication**: Secure token-based authentication

##  Advanced Features

- **Geospatial queries**: Find robots by location using MongoDB's geospatial features
- **Auto-cleanup**: Detections are automatically limited to prevent excessive storage
- **Virtual properties**: Calculated fields like `isOnline`, `detectionCount`
- **Instance methods**: Helper methods for adding detections, updating health
- **Indexes**: Optimized database queries for better performance

##  Server Status

The server is now running on **http://localhost:5002** with:
- MongoDB Atlas connection 
- User authentication   
- Robot model and APIs 
- All validation and security features 

Ready to handle CORA robot data!