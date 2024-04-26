const { strict } = require("assert");

// Import required modules
const mongoose=require("mongoose");

// Connect to MongoDB database
const connect=mongoose.connect("mongodb://localhost:27017/userInfo");

// Connection success and error handling
connect.then(()=>{
    console.log("Database connected")
})
.catch(()=>{
    console.log("database can not be connected");
});

// Define schema for user login information
const LoginSchema=new mongoose.Schema({
    name:{
        type:String,
        required:true,
        unique:true
    },
    email:{
        type:String,
        required:true
    },
    password:{
        type:String,
        required:true
    }
});

// Define schema for articles
const articleSchema = new mongoose.Schema({
    username:{
        type: String,
        required: true
    },
    title:{
        type: String
    },
    content: {
        type: String,
        required: true
    },
    createdAt:{
        type: Date,
        default: Date.now
    },
    slug:{
        type: String,
        required: true,
        unique: true
    
    },
    sanitizedHTML:{
        type: String,
        required: true
    }
})

// Create a model for user collection
const collection=new mongoose.model("users",LoginSchema);

// Export article model and user collection model
module.exports = mongoose.model('Article',articleSchema)
module.exports=collection;