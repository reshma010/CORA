const User = require('../models/User');
const { sendSuccess, sendError, sendServerError } = require('../utils/response');

// @desc    Get all users (admin only)
// @route   GET /api/users
// @access  Private/Admin
const getUsers = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    const users = await User.find()
      .select('-password')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);

    const total = await User.countDocuments();

    sendSuccess(res, 'Users retrieved successfully', {
      users,
      pagination: {
        currentPage: page,
        totalPages: Math.ceil(total / limit),
        totalUsers: total,
        hasNext: page < Math.ceil(total / limit),
        hasPrev: page > 1
      }
    });

  } catch (error) {
    console.error('Get users error:', error);
    sendServerError(res, 'Error fetching users');
  }
};

// @desc    Get single user
// @route   GET /api/users/:id
// @access  Private
const getUser = async (req, res) => {
  try {
    const user = await User.findById(req.params.id).select('-password');
    
    if (!user) {
      return sendError(res, 'User not found', 404);
    }

    sendSuccess(res, 'User retrieved successfully', { user });

  } catch (error) {
    console.error('Get user error:', error);
    sendServerError(res, 'Error fetching user');
  }
};

// @desc    Update user profile
// @route   PUT /api/users/:id
// @access  Private
const updateUser = async (req, res) => {
  try {
    const { name, email } = req.body;
    const userId = req.params.id;

    // Check if user is updating their own profile or is admin
    if (req.user.id !== userId && req.user.role !== 'admin') {
      return sendError(res, 'Not authorized to update this profile', 403);
    }

    const user = await User.findById(userId);
    
    if (!user) {
      return sendError(res, 'User not found', 404);
    }

    // Update fields
    if (name) user.name = name;
    if (email) user.email = email;

    await user.save();

    sendSuccess(res, 'User updated successfully', {
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
        isActive: user.isActive
      }
    });

  } catch (error) {
    console.error('Update user error:', error);
    sendServerError(res, 'Error updating user');
  }
};

// @desc    Delete user (admin only)
// @route   DELETE /api/users/:id
// @access  Private/Admin
const deleteUser = async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    
    if (!user) {
      return sendError(res, 'User not found', 404);
    }

    await User.findByIdAndDelete(req.params.id);

    sendSuccess(res, 'User deleted successfully');

  } catch (error) {
    console.error('Delete user error:', error);
    sendServerError(res, 'Error deleting user');
  }
};

module.exports = {
  getUsers,
  getUser,
  updateUser,
  deleteUser
};