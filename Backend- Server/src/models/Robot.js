const mongoose = require('mongoose');

// Individual detection schema
const detectionSchema = new mongoose.Schema({
  timestamp: {
    type: Date,
    required: true
  },
  action_type: {
    type: String,
    enum: ['sitting_down', 'getting_up', 'sitting', 'standing', 'walking', 'jumping', 'unknown'],
    required: true
  },
  confidence: {
    type: Number,
    required: true,
    min: 0,
    max: 1
  },
  person_id: {
    type: Number,
    required: true
  },
  frame_number: {
    type: Number,
    required: true
  },
  normalized_bbox: {
    x: { type: Number, required: true, min: 0, max: 1 },
    y: { type: Number, required: true, min: 0, max: 1 },
    width: { type: Number, required: true, min: 0, max: 1 },
    height: { type: Number, required: true, min: 0, max: 1 },
    confidence: { type: Number, required: true, min: 0, max: 1 }
  },
  thumbnail: {
    type: String, // Base64 encoded image
    default: null
  },
  tracking_info: {
    is_tracked: { type: Boolean, default: false },
    tracking_age: { type: Number, default: 0 }
  },
  pose_scores: {
    sitting_down: { type: Number, default: 0 },
    getting_up: { type: Number, default: 0 },
    sitting: { type: Number, default: 0 },
    standing: { type: Number, default: 0 },
    walking: { type: Number, default: 0 },
    jumping: { type: Number, default: 0 }
  }
});

// Robot schema - represents a physical robot unit
const robotSchema = new mongoose.Schema({
  unit_id: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  unit_name: {
    type: String,
    required: true
  },
  rtsp_uris: [{
    type: String
  }],
  status: {
    type: String,
    enum: ['online', 'offline', 'error'],
    default: 'offline'
  },
  last_seen: {
    type: Date,
    default: Date.now
  },
  location: {
    type: String,
    default: 'Unknown'
  },
  // Array of detection data - stores all detections for this robot
  detections: [detectionSchema],
  // Metadata about the robot
  metadata: {
    model: { type: String, default: 'Unknown' },
    firmware_version: { type: String, default: 'Unknown' },
    ip_address: { type: String, default: null },
    mac_address: { type: String, default: null }
  },
  // Statistics cache for performance
  stats_cache: {
    total_detections: { type: Number, default: 0 },
    last_24h_detections: { type: Number, default: 0 },
    most_common_action: { type: String, default: 'unknown' },
    avg_confidence: { type: Number, default: 0 },
    last_updated: { type: Date, default: Date.now }
  }
}, {
  timestamps: true
});

// Indexes for efficient querying
robotSchema.index({ unit_id: 1 });
robotSchema.index({ status: 1 });
robotSchema.index({ last_seen: -1 });
robotSchema.index({ 'detections.timestamp': -1 });
robotSchema.index({ 'detections.action_type': 1 });

// Virtual for getting recent detections (last 24 hours)
robotSchema.virtual('recent_detections').get(function() {
  const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
  return this.detections.filter(det => new Date(det.timestamp) > twentyFourHoursAgo);
});

// Virtual for determining if robot is active (seen in last 5 minutes)
robotSchema.virtual('is_active').get(function() {
  const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
  return this.last_seen > fiveMinutesAgo;
});

// Method to add new detection data
robotSchema.methods.addDetection = function(detectionData) {
  this.detections.push(detectionData);
  this.last_seen = new Date();
  this.status = 'online';
  
  // Update stats cache
  this.updateStatsCache();
  
  return this.save();
};

// Method to add multiple detections from a data package
robotSchema.methods.addDetections = function(detectionsArray) {
  detectionsArray.forEach(detection => {
    this.detections.push(detection);
  });
  
  this.last_seen = new Date();
  this.status = 'online';
  
  // Update stats cache
  this.updateStatsCache();
  
  return this.save();
};

// Method to update statistics cache
robotSchema.methods.updateStatsCache = function() {
  const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
  const recentDetections = this.detections.filter(det => new Date(det.timestamp) > twentyFourHoursAgo);
  
  // Calculate statistics
  const actionCounts = {};
  let totalConfidence = 0;
  
  recentDetections.forEach(detection => {
    if (!actionCounts[detection.action_type]) {
      actionCounts[detection.action_type] = 0;
    }
    actionCounts[detection.action_type]++;
    totalConfidence += detection.confidence;
  });
  
  // Find most common action
  let mostCommonAction = 'unknown';
  let maxCount = 0;
  
  Object.entries(actionCounts).forEach(([action, count]) => {
    if (count > maxCount) {
      maxCount = count;
      mostCommonAction = action;
    }
  });
  
  // Update cache
  this.stats_cache = {
    total_detections: this.detections.length,
    last_24h_detections: recentDetections.length,
    most_common_action: mostCommonAction,
    avg_confidence: recentDetections.length > 0 ? totalConfidence / recentDetections.length : 0,
    last_updated: new Date()
  };
};

// Method to get detection statistics
robotSchema.methods.getStats = function() {
  const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
  
  const allDetections = this.detections;
  const last24hDetections = allDetections.filter(det => new Date(det.timestamp) > twentyFourHoursAgo);
  const lastHourDetections = allDetections.filter(det => new Date(det.timestamp) > oneHourAgo);
  
  const stats = {
    total_detections: allDetections.length,
    last_24h_detections: last24hDetections.length,
    last_hour_detections: lastHourDetections.length,
    action_counts: {},
    hourly_breakdown: {},
    avg_confidence: 0,
    confidence_distribution: { low: 0, medium: 0, high: 0 }
  };

  let totalConfidence = 0;
  
  last24hDetections.forEach(detection => {
    // Count actions
    if (!stats.action_counts[detection.action_type]) {
      stats.action_counts[detection.action_type] = 0;
    }
    stats.action_counts[detection.action_type]++;
    
    // Calculate confidence stats
    totalConfidence += detection.confidence;
    
    if (detection.confidence < 0.6) {
      stats.confidence_distribution.low++;
    } else if (detection.confidence < 0.8) {
      stats.confidence_distribution.medium++;
    } else {
      stats.confidence_distribution.high++;
    }
    
    // Hourly breakdown
    const hour = new Date(detection.timestamp).getHours();
    if (!stats.hourly_breakdown[hour]) {
      stats.hourly_breakdown[hour] = 0;
    }
    stats.hourly_breakdown[hour]++;
  });

  stats.avg_confidence = last24hDetections.length > 0 ? totalConfidence / last24hDetections.length : 0;
  
  return stats;
};

// Method to get detections by time range
robotSchema.methods.getDetectionsByTimeRange = function(startTime, endTime, actionType = null) {
  let detections = this.detections.filter(det => {
    const detTime = new Date(det.timestamp);
    return detTime >= startTime && detTime <= endTime;
  });
  
  if (actionType) {
    detections = detections.filter(det => det.action_type === actionType);
  }
  
  return detections.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
};

// Static method to get all active robots
robotSchema.statics.getActiveRobots = function(minutesThreshold = 5) {
  const thresholdTime = new Date(Date.now() - minutesThreshold * 60 * 1000);
  return this.find({ last_seen: { $gte: thresholdTime } }).sort({ last_seen: -1 });
};

// Static method to get robot by unit_id
robotSchema.statics.findByUnitId = function(unitId) {
  return this.findOne({ unit_id: unitId });
};

// Pre-save middleware to update stats cache
robotSchema.pre('save', function(next) {
  if (this.isModified('detections')) {
    this.updateStatsCache();
  }
  next();
});

const Robot = mongoose.model('Robot', robotSchema);

module.exports = Robot;