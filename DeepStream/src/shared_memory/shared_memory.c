#include "shared_memory.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/time.h>
#include <fcntl.h>

// Get current timestamp in microseconds
static uint64_t get_timestamp_us() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec * 1000000 + tv.tv_usec;
}

bool shm_init(SharedMemoryManager *shm_mgr) {
    if (!shm_mgr) {
        fprintf(stderr, "SharedMemoryManager pointer is NULL\n");
        return false;
    }
    
    // Initialize structure
    memset(shm_mgr, 0, sizeof(SharedMemoryManager));
    
    // Try to get existing shared memory segment first
    int existing_shm_id = shmget(SHM_KEY, 0, 0);
    if (existing_shm_id != -1) {
        // Check if existing segment has the right size
        struct shmid_ds shm_info;
        if (shmctl(existing_shm_id, IPC_STAT, &shm_info) == 0) {
            if (shm_info.shm_segsz < sizeof(SharedMemoryData)) {
                printf("Existing shared memory segment is too small (%lu bytes), removing it...\n", 
                       shm_info.shm_segsz);
                // Remove the old segment
                shmctl(existing_shm_id, IPC_RMID, NULL);
            }
        }
    }
    
    // Create or get shared memory segment with correct size
    shm_mgr->shm_id = shmget(SHM_KEY, sizeof(SharedMemoryData), IPC_CREAT | 0666);
    if (shm_mgr->shm_id == -1) {
        fprintf(stderr, "Failed to create shared memory: %s\n", strerror(errno));
        return false;
    }
    
    // Attach to shared memory
    shm_mgr->data = (SharedMemoryData *)shmat(shm_mgr->shm_id, NULL, 0);
    if (shm_mgr->data == (SharedMemoryData *)-1) {
        fprintf(stderr, "Failed to attach to shared memory: %s\n", strerror(errno));
        return false;
    }
    
    // Initialize semaphore for synchronization
    shm_mgr->semaphore = sem_open(SEM_NAME, O_CREAT, 0666, 1);
    if (shm_mgr->semaphore == SEM_FAILED) {
        fprintf(stderr, "Failed to create semaphore: %s\n", strerror(errno));
        shmdt(shm_mgr->data);
        return false;
    }
    
    // Initialize shared memory data (only if this is the first process)
    shm_lock(shm_mgr);
    if (shm_mgr->data->sequence_id == 0) {
        memset(shm_mgr->data, 0, sizeof(SharedMemoryData));
        shm_mgr->data->timestamp_us = get_timestamp_us();
        shm_mgr->data->pipeline_active = false;
        printf("Initialized shared memory data structure\n");
    }
    shm_unlock(shm_mgr);
    
    shm_mgr->initialized = true;
    printf("Shared memory initialized successfully (ID: %d)\n", shm_mgr->shm_id);
    return true;
}

void shm_cleanup(SharedMemoryManager *shm_mgr) {
    if (!shm_mgr || !shm_mgr->initialized) {
        return;
    }
    
    // Detach from shared memory
    if (shm_mgr->data) {
        shmdt(shm_mgr->data);
        shm_mgr->data = NULL;
    }
    
    // Close semaphore
    if (shm_mgr->semaphore != SEM_FAILED) {
        sem_close(shm_mgr->semaphore);
        // Note: We don't unlink the semaphore here as other processes might be using it
        // sem_unlink(SEM_NAME); // Only call this when shutting down all processes
    }
    
    shm_mgr->initialized = false;
    printf("Shared memory cleaned up\n");
}

void shm_lock(SharedMemoryManager *shm_mgr) {
    if (shm_mgr && shm_mgr->semaphore != SEM_FAILED) {
        sem_wait(shm_mgr->semaphore);
    }
}

void shm_unlock(SharedMemoryManager *shm_mgr) {
    if (shm_mgr && shm_mgr->semaphore != SEM_FAILED) {
        sem_post(shm_mgr->semaphore);
    }
}

bool shm_write_detection_data(SharedMemoryManager *shm_mgr, const PersonDetection *detections,
                             uint32_t num_detections, uint32_t frame_number, uint64_t timestamp) {
    if (!shm_mgr || !shm_mgr->initialized || !shm_mgr->data) {
        fprintf(stderr, "Shared memory not initialized\n");
        return false;
    }
    
    if (num_detections > MAX_PERSONS) {
        fprintf(stderr, "Too many detections (%d), max is %d\n", num_detections, MAX_PERSONS);
        num_detections = MAX_PERSONS;
    }
    
    shm_lock(shm_mgr);
    
    // Update header information
    shm_mgr->data->timestamp_us = timestamp ? timestamp : get_timestamp_us();
    shm_mgr->data->frame_number = frame_number;
    shm_mgr->data->sequence_id++;
    shm_mgr->data->num_persons = num_detections;
    shm_mgr->data->pipeline_active = true;
    shm_mgr->data->total_frames_processed++;
    
    // Copy detection data
    if (detections && num_detections > 0) {
        memcpy(shm_mgr->data->persons, detections, sizeof(PersonDetection) * num_detections);
        shm_mgr->data->total_persons_detected += num_detections;
    }
    
    // Clear unused detection slots
    if (num_detections < MAX_PERSONS) {
        memset(&shm_mgr->data->persons[num_detections], 0, 
               sizeof(PersonDetection) * (MAX_PERSONS - num_detections));
    }
    
    shm_unlock(shm_mgr);
    
    return true;
}

bool shm_read_detection_data(SharedMemoryManager *shm_mgr, SharedMemoryData *output_data) {
    if (!shm_mgr || !shm_mgr->initialized || !shm_mgr->data || !output_data) {
        return false;
    }
    
    shm_lock(shm_mgr);
    memcpy(output_data, shm_mgr->data, sizeof(SharedMemoryData));
    shm_unlock(shm_mgr);
    
    return true;
}

// Utility function to convert pose class enum to string
const char* pose_class_to_string(PoseClass pose_class) {
    switch (pose_class) {
        case POSE_SITTING_DOWN: return "sitting_down";
        case POSE_GETTING_UP: return "getting_up";
        case POSE_SITTING: return "sitting";
        case POSE_STANDING: return "standing";
        case POSE_WALKING: return "walking";
        case POSE_JUMPING: return "jumping";
        default: return "unknown";
    }
}

// Utility function to print detection data (for debugging)
void print_detection_data(const SharedMemoryData *data) {
    printf("=== Detection Data ===\n");
    printf("Timestamp: %lu us\n", data->timestamp_us);
    printf("Frame: %u\n", data->frame_number);
    printf("Sequence: %u\n", data->sequence_id);
    printf("Persons: %u\n", data->num_persons);
    printf("Pipeline Active: %s\n", data->pipeline_active ? "Yes" : "No");
    printf("FPS: %u\n", data->fps);
    printf("Frame Size: %ux%u\n", data->frame_width, data->frame_height);
    
    for (uint32_t i = 0; i < data->num_persons && i < MAX_PERSONS; i++) {
        const PersonDetection *person = &data->persons[i];
        printf("Person %u: ID=%u, Pose=%s (%.2f), Tracked=%s\n",
               i, person->person_id, pose_class_to_string(person->pose_class),
               person->pose_confidence, person->is_tracked ? "Yes" : "No");
    }
    printf("===================\n");
}