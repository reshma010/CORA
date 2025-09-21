#ifndef SHARED_MEMORY_H
#define SHARED_MEMORY_H

#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/types.h>
#include <semaphore.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_PERSONS 10
#define MAX_JOINTS 34
#define MAX_POSE_CLASSES 6
#define SHM_KEY 12345
#define SEM_NAME "/pose_detection_sem"

// Thumbnail settings
#define THUMBNAIL_MAX_WIDTH 320
#define THUMBNAIL_MAX_HEIGHT 240
#define THUMBNAIL_MAX_SIZE (THUMBNAIL_MAX_WIDTH * THUMBNAIL_MAX_HEIGHT * 3) // RGB format
#define THUMBNAIL_BUFFER_COUNT 100  // Number of thumbnail frames to buffer

// Pose classification labels (matching actual model classes)
typedef enum {
    POSE_SITTING_DOWN = 0,
    POSE_GETTING_UP = 1,
    POSE_SITTING = 2,
    POSE_STANDING = 3,
    POSE_WALKING = 4,
    POSE_JUMPING = 5
} PoseClass;

// 3D joint structure
typedef struct {
    float x, y, z;          // 3D coordinates
    float confidence;       // Joint confidence score
    bool visible;           // Joint visibility
} Joint3D;

// 2D joint structure
typedef struct {
    float x, y;             // 2D coordinates
    float confidence;       // Joint confidence score
    bool visible;           // Joint visibility
} Joint2D;

// Bounding box structure
typedef struct {
    float left, top, width, height;
    float confidence;
} BoundingBox;

// Person detection structure
typedef struct {
    uint32_t person_id;                    // Unique person ID from tracker
    uint64_t timestamp_us;                 // Timestamp in microseconds
    uint32_t frame_number;                 // Frame number
    
    // Bounding box
    BoundingBox bbox;
    
    // 2D pose joints (34 joints)
    Joint2D joints_2d[MAX_JOINTS];
    
    // 3D pose joints (34 joints)
    Joint3D joints_3d[MAX_JOINTS];
    
    // Pose classification
    PoseClass pose_class;
    float pose_confidence;
    float pose_scores[MAX_POSE_CLASSES];   // Confidence scores for all classes
    
    // Tracking information
    bool is_tracked;
    uint32_t tracking_age;                 // Number of frames tracked
    
    // Valid flags
    bool has_2d_pose;
    bool has_3d_pose;
    bool has_classification;
    
    // Reserved for future use
    uint8_t reserved[64];
} PersonDetection;

// Shared memory data structure
typedef struct {
    // Header information
    uint64_t timestamp_us;                 // Latest update timestamp
    uint32_t frame_number;                 // Current frame number
    uint32_t sequence_id;                  // Sequence counter for data integrity
    uint32_t num_persons;                  // Number of detected persons
    
    // Pipeline status
    bool pipeline_active;
    uint32_t fps;                          // Current FPS
    
    // Camera info
    uint32_t frame_width;
    uint32_t frame_height;
    
    // Thumbnail data - circular buffer for multiple frames
    bool has_thumbnail;
    uint32_t thumbnail_width;
    uint32_t thumbnail_height;
    uint32_t thumbnail_size;  // Actual size of thumbnail data in bytes
    uint32_t current_thumbnail_index;  // Current write position in circular buffer
    uint8_t thumbnail_buffer[THUMBNAIL_BUFFER_COUNT][THUMBNAIL_MAX_SIZE];
    
    // Person detections
    PersonDetection persons[MAX_PERSONS];
    
    // Statistics
    uint64_t total_frames_processed;
    uint32_t total_persons_detected;
    
    // Reserved for future use
    uint8_t reserved[256];
} SharedMemoryData;

// Shared memory manager structure
typedef struct {
    int shm_id;
    SharedMemoryData *data;
    sem_t *semaphore;
    bool initialized;
} SharedMemoryManager;

// Function prototypes
bool shm_init(SharedMemoryManager *shm_mgr);
void shm_cleanup(SharedMemoryManager *shm_mgr);
bool shm_write_detection_data(SharedMemoryManager *shm_mgr, const PersonDetection *detections, 
                             uint32_t num_detections, uint32_t frame_number, uint64_t timestamp);
bool shm_read_detection_data(SharedMemoryManager *shm_mgr, SharedMemoryData *output_data);
void shm_lock(SharedMemoryManager *shm_mgr);
void shm_unlock(SharedMemoryManager *shm_mgr);

#endif // SHARED_MEMORY_H