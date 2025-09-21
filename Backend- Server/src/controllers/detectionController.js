const Robot = require('../models/Robot');
const { sendSuccess, sendError, sendServerError } = require('../utils/response');

// @desc    Receive detection data from robot units
// @route   POST /api/robots/detections
// @access  Public (robots authenticate in production)
const receiveDetections = async (req, res) => {
  try {
    console.log('\n===  DETECTION ENDPOINT HIT ===');
    console.log(' REQUEST METHOD:', req.method);
    console.log(' REQUEST URL:', req.originalUrl);
    console.log(' REQUEST HEADERS:', JSON.stringify(req.headers, null, 2));
    console.log(' REQUEST BODY TYPE:', typeof req.body);
    console.log(' REQUEST BODY SIZE:', JSON.stringify(req.body).length, 'bytes');
    console.log(' FULL REQUEST BODY:', JSON.stringify(req.body, null, 2));
    
    console.log(' ROBOT DATA: Detection data received');
    console.log(' ROBOT DATA: Unit ID:', req.body.unit_id);
    console.log(' ROBOT DATA: Detection count:', req.body.detections?.length || 0);

    const {
      unit_id,
      unit_name,
      rtsp_uris,
      timestamp,
      detections
    } = req.body;
    
    console.log(' PARSED DATA:');
    console.log('  - unit_id:', unit_id);
    console.log('  - unit_name:', unit_name);
    console.log('  - rtsp_uris:', rtsp_uris);
    console.log('  - timestamp:', timestamp);
    console.log('  - detections array length:', detections?.length || 0);

    // Validate required fields
    if (!unit_id || !unit_name || !detections) {
      console.log(' ROBOT DATA: Missing required fields');
      return sendError(res, 'Missing required fields: unit_id, unit_name, detections', 400);
    }

    // Validate detections array
    if (!Array.isArray(detections) || detections.length === 0) {
      console.log(' ROBOT DATA: Invalid detections array');
      return sendError(res, 'Detections must be a non-empty array', 400);
    }

    // Find or create robot
    console.log(' DATABASE: Searching for robot with unit_id:', unit_id);
    let robot = await Robot.findByUnitId(unit_id);
    
    if (!robot) {
      console.log('DATABASE: Robot not found, creating new robot unit');
      console.log('DATABASE: New robot data:', {
        unit_id,
        unit_name,
        rtsp_uris: rtsp_uris || [],
        status: 'online'
      });
      
      robot = new Robot({
        unit_id,
        unit_name,
        rtsp_uris: rtsp_uris || [],
        status: 'online',
        last_seen: new Date(),
        detections: []
      });
      
      console.log('DATABASE: Robot object created, about to save...');
    } else {
      console.log(' DATABASE: Found existing robot:', {
        id: robot._id,
        unit_id: robot.unit_id,
        unit_name: robot.unit_name,
        existing_detections: robot.detections.length
      });
      
      // Update robot info
      robot.unit_name = unit_name;
      robot.rtsp_uris = rtsp_uris || robot.rtsp_uris;
      robot.last_seen = new Date();
      robot.status = 'online';
      
      console.log(' DATABASE: Updated robot info');
    }

    // Validate each detection
    const validatedDetections = [];
    for (let i = 0; i < detections.length; i++) {
      const detection = detections[i];
      
      // Validate required detection fields
      if (!detection.timestamp || !detection.action_type || 
          detection.confidence === undefined || detection.person_id === undefined ||
          detection.frame_number === undefined || !detection.normalized_bbox) {
        console.log(` ROBOT DATA: Invalid detection at index ${i}`);
        continue; // Skip invalid detections rather than rejecting entire batch
      }

      // Validate action_type
      const validActions = ['sitting_down', 'getting_up', 'sitting', 'standing', 'walking', 'jumping', 'unknown'];
      if (!validActions.includes(detection.action_type)) {
        console.log(` ROBOT DATA: Invalid action_type: ${detection.action_type}`);
        detection.action_type = 'unknown'; // Default to unknown
      }

      // Validate confidence range
      if (detection.confidence < 0 || detection.confidence > 1) {
        console.log(` ROBOT DATA: Invalid confidence: ${detection.confidence}`);
        continue;
      }

      // Validate bounding box
      const bbox = detection.normalized_bbox;
      if (!bbox || bbox.x < 0 || bbox.x > 1 || bbox.y < 0 || bbox.y > 1 ||
          bbox.width < 0 || bbox.width > 1 || bbox.height < 0 || bbox.height > 1) {
        console.log(` ROBOT DATA: Invalid bounding box at index ${i}`);
        continue;
      }

      // Convert timestamp to Date object
      detection.timestamp = new Date(detection.timestamp);

      validatedDetections.push(detection);
    }

    if (validatedDetections.length === 0) {
      console.log(' ROBOT DATA: No valid detections found');
      return sendError(res, 'No valid detections found in batch', 400);
    }

    // Add detections to robot
    console.log(' DATABASE: About to add detections to robot...');
    console.log(' DATABASE: Validated detections count:', validatedDetections.length);
    console.log(' DATABASE: Sample detection:', validatedDetections[0]);
    
    const saveResult = await robot.addDetections(validatedDetections);
    
    console.log(' DATABASE: Save operation completed');
    console.log(' DATABASE: Save result:', !!saveResult);
    console.log(' DATABASE: Robot after save - total detections:', robot.detections.length);
    console.log(' DATABASE: Robot ID after save:', robot._id);

    console.log(' ROBOT DATA: Successfully saved robot detections');
    console.log(` ROBOT DATA: Saved ${validatedDetections.length}/${detections.length} detections`);

    // Get robot statistics
    const stats = robot.getStats();

    // Log detection summary
    console.log(' ROBOT DATA: Detection summary:', {
      unit_id,
      unit_name,
      total_detections: stats.total_detections,
      action_counts: stats.action_counts,
      avg_confidence: stats.avg_confidence.toFixed(3)
    });

    sendSuccess(res, 'Robot detection data processed successfully', {
      unit_id,
      unit_name,
      processed_detections: validatedDetections.length,
      total_detections: detections.length,
      stats
    });

  } catch (error) {
    console.error(' ROBOT DATA: Error processing robot detections:', error);
    console.error(' ROBOT DATA: Error type:', error.constructor.name);
    console.error(' ROBOT DATA: Error message:', error.message);
    console.error(' ROBOT DATA: Error stack:', error.stack);
    
    if (error.name === 'ValidationError') {
      console.error(' VALIDATION ERROR: Details:', error.errors);
    }
    
    if (error.name === 'MongoError' || error.name === 'MongooseError') {
      console.error(' DATABASE ERROR: Code:', error.code);
      console.error(' DATABASE ERROR: Details:', error.codeName);
    }
    
    sendServerError(res, 'Error processing robot detection data');
  }
};

// @desc    Get detection data for a specific robot unit
// @route   GET /api/robots/:unitId/detections
// @access  Private (requires authentication)
const getDetectionsByUnit = async (req, res) => {
  try {
    const { unitId } = req.params;
    const { hours = 24, limit = 100, action_type } = req.query;

    console.log(` ROBOT QUERY: Getting detections for unit ${unitId}`);

    // Find robot by unit_id
    const robot = await Robot.findByUnitId(unitId);
    if (!robot) {
      console.log(` ROBOT QUERY: Robot unit ${unitId} not found`);
      return sendError(res, 'Robot unit not found', 404);
    }

    // Calculate time filter
    const since = new Date(Date.now() - parseInt(hours) * 60 * 60 * 1000);
    
    // Get detections using robot method
    let detections = robot.getDetectionsByTimeRange(since, new Date(), action_type);
    
    // Apply limit
    if (limit && limit > 0) {
      detections = detections.slice(0, parseInt(limit));
    }

    // Calculate statistics
    let totalConfidence = 0;
    const actionCounts = {};

    detections.forEach(det => {
      totalConfidence += det.confidence;
      
      if (!actionCounts[det.action_type]) {
        actionCounts[det.action_type] = 0;
      }
      actionCounts[det.action_type]++;
    });

    const avgConfidence = detections.length > 0 ? totalConfidence / detections.length : 0;

    console.log(` ROBOT QUERY: Found ${detections.length} detections for robot ${unitId}`);

    sendSuccess(res, 'Robot detection data retrieved successfully', {
      unit_id: unitId,
      unit_name: robot.unit_name,
      rtsp_uris: robot.rtsp_uris,
      total_detections: detections.length,
      avg_confidence: avgConfidence,
      action_counts: actionCounts,
      detections
    });

  } catch (error) {
    console.error(' ROBOT QUERY: Error getting robot detections:', error);
    sendServerError(res, 'Error retrieving robot detection data');
  }
};

// @desc    Get robot detection summary statistics
// @route   GET /api/robots/:unitId/summary
// @access  Private
const getDetectionSummary = async (req, res) => {
  try {
    const { unitId } = req.params;
    const { hours = 24 } = req.query;

    console.log(` ROBOT SUMMARY: Getting summary for unit ${unitId} (last ${hours} hours)`);

    // Find robot by unit_id
    const robot = await Robot.findByUnitId(unitId);
    if (!robot) {
      console.log(` ROBOT SUMMARY: Robot unit ${unitId} not found`);
      return sendError(res, 'Robot unit not found', 404);
    }

    // Get robot statistics
    const stats = robot.getStats();

    console.log(` ROBOT SUMMARY: Generated summary for robot ${unitId}`);

    sendSuccess(res, 'Robot detection summary retrieved successfully', {
      unit_id: unitId,
      unit_name: robot.unit_name,
      rtsp_uris: robot.rtsp_uris,
      status: robot.status,
      last_seen: robot.last_seen,
      time_range_hours: parseInt(hours),
      stats
    });

  } catch (error) {
    console.error(' ROBOT SUMMARY: Error getting robot summary:', error);
    sendServerError(res, 'Error retrieving robot detection summary');
  }
};

// @desc    Get all active robot units
// @route   GET /api/robots/active
// @access  Private
const getActiveUnits = async (req, res) => {
  try {
    const { hours = 24 } = req.query;
    const minutesThreshold = parseInt(hours) * 60;

    console.log(` ACTIVE ROBOTS: Getting robots active in last ${hours} hours`);

    // Get active robots using static method
    const activeRobots = await Robot.getActiveRobots(minutesThreshold);

    // Format response data
    const units = activeRobots.map(robot => ({
      unit_id: robot.unit_id,
      unit_name: robot.unit_name,
      status: robot.status,
      last_seen: robot.last_seen,
      is_active: robot.is_active,
      total_detections: robot.stats_cache.total_detections,
      last_24h_detections: robot.stats_cache.last_24h_detections,
      most_common_action: robot.stats_cache.most_common_action,
      avg_confidence: robot.stats_cache.avg_confidence,
      rtsp_uris: robot.rtsp_uris,
      location: robot.location
    }));

    console.log(` ACTIVE ROBOTS: Found ${units.length} active robot units`);

    sendSuccess(res, 'Active robot units retrieved successfully', {
      time_range_hours: parseInt(hours),
      units_count: units.length,
      units
    });

  } catch (error) {
    console.error(' ACTIVE ROBOTS: Error getting active robots:', error);
    sendServerError(res, 'Error retrieving active robot units');
  }
};

module.exports = {
  receiveDetections,
  getDetectionsByUnit,
  getDetectionSummary,
  getActiveUnits
};