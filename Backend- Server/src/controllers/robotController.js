const Robot = require('../models/Robot');
const User = require('../models/User');
const { sendSuccess, sendError, sendServerError } = require('../utils/response');
const { validationResult } = require('express-validator');

// @desc    Get all robots for a user
// @route   GET /api/robots
// @access  Private
const getRobots = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    // Build query for autonomous robots (no owner concept)
    let query = {};

    // Add status filter if provided
    if (req.query.status) {
      query.status = req.query.status;
    }

    const robots = await Robot.find(query)
      .sort({ last_seen: -1 })
      .skip(skip)
      .limit(limit)
      .lean();

    // Add computed fields for frontend compatibility
    const robotsWithStats = robots.map(robot => ({
      ...robot,
      _id: robot.unit_id, // Use unit_id as _id for frontend compatibility
      packages_count: robot.detections?.length || 0,
      total_detections: robot.detections?.length || 0,
      units_count: 1 // For compatibility with frontend expectations
    }));

    const total = await Robot.countDocuments(query);

    sendSuccess(res, 'Robots retrieved successfully', {
      robots: robotsWithStats,
      pagination: {
        currentPage: page,
        totalPages: Math.ceil(total / limit),
        totalRobots: total,
        hasNext: page < Math.ceil(total / limit),
        hasPrev: page > 1
      }
    });

  } catch (error) {
    console.error('Get robots error:', error);
    sendServerError(res, 'Error fetching robots');
  }
};

// @desc    Get single robot
// @route   GET /api/robots/:id
// @access  Private
const getRobot = async (req, res) => {
  try {
    // Look up robot by unit_id (which is used as _id in frontend)
    const robot = await Robot.findByUnitId(req.params.id);
    
    if (!robot) {
      return sendError(res, 'Robot not found', 404);
    }

    // Add computed fields and format for frontend
    const robotWithStats = {
      ...robot.toObject(),
      _id: robot.unit_id, // Use unit_id as _id for frontend compatibility  
      packages_count: robot.detections?.length || 0,
      total_detections: robot.detections?.length || 0,
      recent_detections: robot.recent_detections,
      is_active: robot.is_active
    };

    sendSuccess(res, 'Robot retrieved successfully', { robot: robotWithStats });

  } catch (error) {
    console.error('Get robot error:', error);
    sendServerError(res, 'Error fetching robot');
  }
};

// @desc    Create new robot
// @route   POST /api/robots
// @access  Private
const createRobot = async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, errors.array()[0].msg, 400);
    }

    const robotData = {
      ...req.body,
      owner: req.user.id
    };

    const robot = await Robot.create(robotData);
    await robot.populate('owner', 'name email');

    sendSuccess(res, 'Robot created successfully', { robot }, 201);

  } catch (error) {
    console.error('Create robot error:', error);
    
    if (error.code === 11000) {
      return sendError(res, 'Robot ID already exists', 400);
    }
    
    sendServerError(res, 'Error creating robot');
  }
};

// @desc    Update robot
// @route   PUT /api/robots/:id
// @access  Private
const updateRobot = async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, errors.array()[0].msg, 400);
    }

    let query = { _id: req.params.id };
    
    // Non-admin users can only update their own robots
    if (req.user.role !== 'admin') {
      query.owner = req.user.id;
    }

    const robot = await Robot.findOneAndUpdate(
      query,
      { ...req.body },
      { new: true, runValidators: true }
    ).populate('owner', 'name email');
    
    if (!robot) {
      return sendError(res, 'Robot not found or not authorized', 404);
    }

    sendSuccess(res, 'Robot updated successfully', { robot });

  } catch (error) {
    console.error('Update robot error:', error);
    sendServerError(res, 'Error updating robot');
  }
};

// @desc    Delete robot
// @route   DELETE /api/robots/:id
// @access  Private
const deleteRobot = async (req, res) => {
  try {
    let query = { _id: req.params.id };
    
    // Non-admin users can only delete their own robots
    if (req.user.role !== 'admin') {
      query.owner = req.user.id;
    }

    const robot = await Robot.findOneAndDelete(query);
    
    if (!robot) {
      return sendError(res, 'Robot not found or not authorized', 404);
    }

    sendSuccess(res, 'Robot deleted successfully');

  } catch (error) {
    console.error('Delete robot error:', error);
    sendServerError(res, 'Error deleting robot');
  }
};

// @desc    Add detection to robot
// @route   POST /api/robots/:id/detections
// @access  Private
const addDetection = async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, errors.array()[0].msg, 400);
    }

    let query = { _id: req.params.id };
    
    // Non-admin users can only add detections to their own robots
    if (req.user.role !== 'admin') {
      query.owner = req.user.id;
    }

    const robot = await Robot.findOne(query);
    
    if (!robot) {
      return sendError(res, 'Robot not found or not authorized', 404);
    }

    await robot.addDetection(req.body);

    sendSuccess(res, 'Detection added successfully', { 
      detectionId: robot.detections[robot.detections.length - 1]._id,
      totalDetections: robot.detections.length 
    }, 201);

  } catch (error) {
    console.error('Add detection error:', error);
    sendServerError(res, 'Error adding detection');
  }
};

// @desc    Get robot detections
// @route   GET /api/robots/:id/detections
// @access  Private
const getDetections = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const skip = (page - 1) * limit;

    let query = { _id: req.params.id };
    
    // Non-admin users can only see detections from their own robots
    if (req.user.role !== 'admin') {
      query.owner = req.user.id;
    }

    const robot = await Robot.findOne(query);
    
    if (!robot) {
      return sendError(res, 'Robot not found or not authorized', 404);
    }

    // Sort detections by timestamp (newest first) and paginate
    const sortedDetections = robot.detections
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(skip, skip + limit);

    const total = robot.detections.length;

    sendSuccess(res, 'Detections retrieved successfully', {
      detections: sortedDetections,
      pagination: {
        currentPage: page,
        totalPages: Math.ceil(total / limit),
        totalDetections: total,
        hasNext: page < Math.ceil(total / limit),
        hasPrev: page > 1
      }
    });

  } catch (error) {
    console.error('Get detections error:', error);
    sendServerError(res, 'Error fetching detections');
  }
};

// @desc    Add RTSP stream to robot
// @route   POST /api/robots/:id/streams
// @access  Private
const addRtspStream = async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return sendError(res, errors.array()[0].msg, 400);
    }

    let query = { _id: req.params.id };
    
    // Non-admin users can only add streams to their own robots
    if (req.user.role !== 'admin') {
      query.owner = req.user.id;
    }

    const robot = await Robot.findOne(query);
    
    if (!robot) {
      return sendError(res, 'Robot not found or not authorized', 404);
    }

    await robot.addRtspStream(req.body);

    sendSuccess(res, 'RTSP stream added successfully', { 
      streamId: robot.rtspStreams[robot.rtspStreams.length - 1]._id,
      totalStreams: robot.rtspStreams.length 
    }, 201);

  } catch (error) {
    console.error('Add RTSP stream error:', error);
    sendServerError(res, 'Error adding RTSP stream');
  }
};

// @desc    Update robot health status
// @route   PUT /api/robots/:id/health
// @access  Private
const updateHealth = async (req, res) => {
  try {
    let query = { _id: req.params.id };
    
    // Non-admin users can only update health for their own robots
    if (req.user.role !== 'admin') {
      query.owner = req.user.id;
    }

    const robot = await Robot.findOne(query);
    
    if (!robot) {
      return sendError(res, 'Robot not found or not authorized', 404);
    }

    await robot.updateHealth(req.body);

    sendSuccess(res, 'Robot health updated successfully', { 
      health: robot.health 
    });

  } catch (error) {
    console.error('Update health error:', error);
    sendServerError(res, 'Error updating robot health');
  }
};

// @desc    Clean up database inconsistencies
// @route   POST /api/robots/cleanup
// @access  Admin only
const cleanupDatabase = async (req, res) => {
  try {
    console.log('ADMIN: Database cleanup requested');
    
    const result = await Robot.cleanupDatabase();
    
    console.log('ADMIN: Database cleanup completed:', result);
    
    sendSuccess(res, 'Database cleanup completed successfully', result);

  } catch (error) {
    console.error('Database cleanup error:', error);
    sendServerError(res, 'Error during database cleanup');
  }
};

module.exports = {
  getRobots,
  getRobot,
  createRobot,
  updateRobot,
  deleteRobot,
  addDetection,
  getDetections,
  addRtspStream,
  updateHealth,
  cleanupDatabase
};