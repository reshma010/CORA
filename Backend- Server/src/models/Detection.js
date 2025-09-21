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

// Detection package schema (what the robot sends)
const detectionPackageSchema = new mongoose.Schema({
  package_id: {
    type: String,
    required: true,
    unique: true
  },
  unit_id: {
    type: String,
    required: true,
    index: true
  },
  unit_name: {
    type: String,
    required: true
  },
  rtsp_uris: [{
    type: String
  }],
  timestamp: {
    type: Date,
    required: true
  },
  detection_count: {
    type: Number,
    required: true,
    min: 0
  },
  detections: [detectionSchema],
  processed: {
    type: Boolean,
    default: false
  },
  processed_at: {
    type: Date,
    default: null
  }
}, {
  timestamps: true
});

// Indexes for efficient querying
detectionPackageSchema.index({ unit_id: 1, timestamp: -1 });
detectionPackageSchema.index({ 'detections.action_type': 1 });
detectionPackageSchema.index({ 'detections.timestamp': -1 });
detectionPackageSchema.index({ processed: 1 });

// Virtual for getting recent detections
detectionPackageSchema.virtual('recent_detections').get(function() {
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
  return this.detections.filter(det => new Date(det.timestamp) > oneHourAgo);
});

// Method to get detection statistics
detectionPackageSchema.methods.getStats = function() {
  const stats = {
    total_detections: this.detections.length,
    action_counts: {},
    avg_confidence: 0,
    confidence_distribution: { low: 0, medium: 0, high: 0 }
  };

  let totalConfidence = 0;
  
  this.detections.forEach(detection => {
    // Count actions
    if (!stats.action_counts[detection.action_type]) {
      stats.action_counts[detection.action_type] = 0;
    }
    stats.action_counts[detection.action_type]++;
    
    // Sum confidence for average
    totalConfidence += detection.confidence;
    
    // Confidence distribution
    if (detection.confidence < 0.5) {
      stats.confidence_distribution.low++;
    } else if (detection.confidence < 0.8) {
      stats.confidence_distribution.medium++;
    } else {
      stats.confidence_distribution.high++;
    }
  });

  if (this.detections.length > 0) {
    stats.avg_confidence = totalConfidence / this.detections.length;
  }

  return stats;
};

// Static method to get recent detections by unit
detectionPackageSchema.statics.getRecentByUnit = function(unitId, hours = 24) {
  const since = new Date(Date.now() - hours * 60 * 60 * 1000);
  return this.find({
    unit_id: unitId,
    timestamp: { $gte: since }
  }).sort({ timestamp: -1 });
};

// Static method to get detection summary
detectionPackageSchema.statics.getDetectionSummary = async function(unitId, hours = 24) {
  const since = new Date(Date.now() - hours * 60 * 60 * 1000);
  
  const pipeline = [
    {
      $match: {
        unit_id: unitId,
        timestamp: { $gte: since }
      }
    },
    {
      $unwind: '$detections'
    },
    {
      $group: {
        _id: '$detections.action_type',
        count: { $sum: 1 },
        avg_confidence: { $avg: '$detections.confidence' },
        max_confidence: { $max: '$detections.confidence' },
        min_confidence: { $min: '$detections.confidence' }
      }
    },
    {
      $sort: { count: -1 }
    }
  ];

  return this.aggregate(pipeline);
};

module.exports = mongoose.model('DetectionPackage', detectionPackageSchema);