const express = require('express');
const { body, param, query } = require('express-validator');
const router = express.Router();

const {
  receiveDetections,
  getDetectionsByUnit,
  getDetectionSummary,
  getActiveUnits
} = require('../controllers/detectionController');

const auth = require('../middleware/auth');

// Validation middleware for robot detection data
const robotDetectionValidation = [
  body('unit_id')
    .notEmpty()
    .withMessage('Unit ID is required')
    .isLength({ min: 3, max: 50 })
    .withMessage('Unit ID must be between 3 and 50 characters'),
  
  body('unit_name')
    .notEmpty()
    .withMessage('Unit name is required')
    .isLength({ min: 3, max: 100 })
    .withMessage('Unit name must be between 3 and 100 characters'),
  
  body('detections')
    .isArray({ min: 1 })
    .withMessage('Detections must be a non-empty array'),
  
  body('detections.*.timestamp')
    .notEmpty()
    .withMessage('Detection timestamp is required'),
  
  body('detections.*.action_type')
    .notEmpty()
    .withMessage('Action type is required')
    .isIn(['sitting_down', 'getting_up', 'sitting', 'standing', 'walking', 'jumping', 'unknown'])
    .withMessage('Invalid action type'),
  
  body('detections.*.confidence')
    .isFloat({ min: 0, max: 1 })
    .withMessage('Confidence must be between 0 and 1'),
  
  body('detections.*.person_id')
    .isInt({ min: 0 })
    .withMessage('Person ID must be a non-negative integer'),
  
  body('detections.*.frame_number')
    .isInt({ min: 0 })
    .withMessage('Frame number must be a non-negative integer'),
  
  body('detections.*.normalized_bbox.x')
    .isFloat({ min: 0, max: 1 })
    .withMessage('Bounding box x must be between 0 and 1'),
  
  body('detections.*.normalized_bbox.y')
    .isFloat({ min: 0, max: 1 })
    .withMessage('Bounding box y must be between 0 and 1'),
  
  body('detections.*.normalized_bbox.width')
    .isFloat({ min: 0, max: 1 })
    .withMessage('Bounding box width must be between 0 and 1'),
  
  body('detections.*.normalized_bbox.height')
    .isFloat({ min: 0, max: 1 })
    .withMessage('Bounding box height must be between 0 and 1'),
  
  body('detections.*.normalized_bbox.confidence')
    .isFloat({ min: 0, max: 1 })
    .withMessage('Bounding box confidence must be between 0 and 1')
];

// Unit ID validation
const unitIdValidation = [
  param('unitId')
    .notEmpty()
    .withMessage('Unit ID is required')
    .isLength({ min: 3, max: 50 })
    .withMessage('Unit ID must be between 3 and 50 characters')
];



// Query parameter validation for time range
const timeRangeValidation = [
  query('hours')
    .optional()
    .isInt({ min: 1, max: 8760 }) // Max 1 year
    .withMessage('Hours must be between 1 and 8760 (1 year)'),
  
  query('limit')
    .optional()
    .isInt({ min: 1, max: 1000 })
    .withMessage('Limit must be between 1 and 1000'),
  
  query('action_type')
    .optional()
    .isIn(['sitting_down', 'getting_up', 'sitting', 'standing', 'walking', 'jumping', 'unknown'])
    .withMessage('Invalid action type filter')
];

// Validation error handler middleware
const handleValidationErrors = (req, res, next) => {
  const { validationResult } = require('express-validator');
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    console.log(' VALIDATION FAILED:');
    console.log(' VALIDATION ERRORS:', JSON.stringify(errors.array(), null, 2));
    console.log(' REQUEST BODY WAS:', JSON.stringify(req.body, null, 2));
    
    return res.status(400).json({
      success: false,
      message: 'Validation failed',
      errors: errors.array()
    });
  }
  
  console.log(' VALIDATION PASSED');
  next();
};

// @route   POST /api/detections
// @desc    Receive detection data from robot units
// @access  Public (secured with API key in production)
router.post('/', robotDetectionValidation, (req, res, next) => {
  console.log('\n ROUTE HIT: POST /api/detections');
  console.log(' ROUTE: Request method:', req.method);
  console.log(' ROUTE: Request path:', req.path);
  console.log(' ROUTE: Request originalUrl:', req.originalUrl);
  console.log(' ROUTE: Request baseUrl:', req.baseUrl);
  console.log(' ROUTE: Content-Type:', req.get('Content-Type'));
  console.log(' ROUTE: Body exists:', !!req.body);
  console.log(' ROUTE: Proceeding to validation...');
  next();
}, handleValidationErrors, receiveDetections);

// @route   GET /api/detections/active
// @desc    Get all active robot units
// @access  Private
router.get('/active', auth, timeRangeValidation, (req, res, next) => {
  console.log(' ROUTE HIT: GET /api/detections/active');
  next();
}, getActiveUnits);

// @route   GET /api/detections/:unitId
// @desc    Get detection data for a specific robot unit
// @access  Private
router.get('/:unitId', auth, unitIdValidation, timeRangeValidation, (req, res, next) => {
  console.log(' ROUTE HIT: GET /api/detections/:unitId');
  next();
}, getDetectionsByUnit);

// @route   GET /api/detections/:unitId/summary
// @desc    Get detection summary statistics for a robot unit
// @access  Private
router.get('/:unitId/summary', auth, unitIdValidation, timeRangeValidation, (req, res, next) => {
  console.log(' ROUTE HIT: GET /api/detections/:unitId/summary');
  next();
}, getDetectionSummary);

module.exports = router;