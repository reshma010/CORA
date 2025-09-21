const express = require('express');
const { body, param } = require('express-validator');
const {
  getRobots,
  getRobot,
  createRobot,
  updateRobot,
  deleteRobot,
  addDetection,
  getDetections,
  addRtspStream,
  updateHealth
} = require('../controllers/robotController');
const auth = require('../middleware/auth');

const router = express.Router();

// Validation rules
const robotValidation = [
  body('robotId')
    .matches(/^CORA-[A-Z0-9]{4,}$/)
    .withMessage('Robot ID must follow format: CORA-XXXX'),
  body('name')
    .trim()
    .isLength({ min: 2, max: 100 })
    .withMessage('Robot name must be between 2 and 100 characters'),
  body('model')
    .trim()
    .isLength({ min: 1, max: 50 })
    .withMessage('Model is required and cannot exceed 50 characters'),
  body('status')
    .optional()
    .isIn(['online', 'offline', 'maintenance', 'error', 'deploying'])
    .withMessage('Invalid status value')
];

const updateRobotValidation = [
  body('name')
    .optional()
    .trim()
    .isLength({ min: 2, max: 100 })
    .withMessage('Robot name must be between 2 and 100 characters'),
  body('model')
    .optional()
    .trim()
    .isLength({ min: 1, max: 50 })
    .withMessage('Model cannot exceed 50 characters'),
  body('status')
    .optional()
    .isIn(['online', 'offline', 'maintenance', 'error', 'deploying'])
    .withMessage('Invalid status value'),
  body('location.coordinates.latitude')
    .optional()
    .isFloat({ min: -90, max: 90 })
    .withMessage('Latitude must be between -90 and 90'),
  body('location.coordinates.longitude')
    .optional()
    .isFloat({ min: -180, max: 180 })
    .withMessage('Longitude must be between -180 and 180')
];

const detectionValidation = [
  body('id')
    .trim()
    .notEmpty()
    .withMessage('Detection ID is required'),
  body('objectType')
    .isIn(['person', 'vehicle', 'animal', 'object', 'anomaly', 'other'])
    .withMessage('Invalid object type'),
  body('confidence')
    .isFloat({ min: 0, max: 1 })
    .withMessage('Confidence must be between 0 and 1'),
  body('boundingBox.x')
    .isNumeric()
    .withMessage('Bounding box X coordinate is required'),
  body('boundingBox.y')
    .isNumeric()
    .withMessage('Bounding box Y coordinate is required'),
  body('boundingBox.width')
    .isNumeric()
    .withMessage('Bounding box width is required'),
  body('boundingBox.height')
    .isNumeric()
    .withMessage('Bounding box height is required')
];

const rtspStreamValidation = [
  body('id')
    .trim()
    .notEmpty()
    .withMessage('Stream ID is required'),
  body('name')
    .trim()
    .isLength({ min: 1, max: 100 })
    .withMessage('Stream name is required and cannot exceed 100 characters'),
  body('url')
    .matches(/^rtsp:\/\/.+/)
    .withMessage('Must be a valid RTSP URL'),
  body('quality')
    .optional()
    .isIn(['low', 'medium', 'high', 'ultra'])
    .withMessage('Invalid quality setting'),
  body('frameRate')
    .optional()
    .isInt({ min: 1, max: 120 })
    .withMessage('Frame rate must be between 1 and 120 FPS')
];

const mongoIdValidation = [
  param('id')
    .isMongoId()
    .withMessage('Invalid robot ID format')
];

// Apply auth middleware to all routes
router.use(auth);

// @route   GET /api/robots
// @desc    Get all robots for authenticated user
// @access  Private
router.get('/', getRobots);

// @route   POST /api/robots
// @desc    Create a new robot
// @access  Private
router.post('/', robotValidation, createRobot);

// @route   GET /api/robots/:id
// @desc    Get single robot by ID
// @access  Private
router.get('/:id', mongoIdValidation, getRobot);

// @route   PUT /api/robots/:id
// @desc    Update robot information
// @access  Private
router.put('/:id', [...mongoIdValidation, ...updateRobotValidation], updateRobot);

// @route   DELETE /api/robots/:id
// @desc    Delete robot
// @access  Private
router.delete('/:id', mongoIdValidation, deleteRobot);

// @route   GET /api/robots/:id/detections
// @desc    Get detections for a specific robot
// @access  Private
router.get('/:id/detections', mongoIdValidation, getDetections);

// @route   POST /api/robots/:id/detections
// @desc    Add new detection to robot
// @access  Private
router.post('/:id/detections', [...mongoIdValidation, ...detectionValidation], addDetection);

// @route   POST /api/robots/:id/streams
// @desc    Add RTSP stream to robot
// @access  Private
router.post('/:id/streams', [...mongoIdValidation, ...rtspStreamValidation], addRtspStream);

// @route   PUT /api/robots/:id/health
// @desc    Update robot health status
// @access  Private
router.put('/:id/health', mongoIdValidation, updateHealth);

module.exports = router;