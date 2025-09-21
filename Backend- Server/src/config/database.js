// Istiaq Hossain
const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    let mongoURI = process.env.NODE_ENV === 'production' 
      ? process.env.MONGODB_URI_PROD 
      : process.env.MONGODB_URI;

    console.log('DATABASE: Attempting to connect...');
    console.log('DATABASE: Environment:', process.env.NODE_ENV || 'development');
    console.log('DATABASE: Using URI:', mongoURI ? 'URI found' : 'URI missing');

    // Replace password variable if DB_PASSWORD is set
    if (process.env.DB_PASSWORD) {
      mongoURI = mongoURI.replace('${DB_PASSWORD}', process.env.DB_PASSWORD);
      console.log('DATABASE: Password variable replaced');
    }

    const conn = await mongoose.connect(mongoURI);

    console.log(`DATABASE: MongoDB Connected: ${conn.connection.host}`);
    console.log(`DATABASE: Database name: ${conn.connection.name}`);
    console.log(`DATABASE: Connection ready state: ${conn.connection.readyState}`);

    // Log collections
    const collections = await conn.connection.db.listCollections().toArray();
    console.log('DATABASE: Available collections:', collections.map(c => c.name));

  } catch (error) {
    console.error('DATABASE: Connection error:', error.message);
    console.error('DATABASE: Error details:', error);
    process.exit(1);
  }
};

module.exports = connectDB;