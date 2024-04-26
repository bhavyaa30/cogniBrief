// Import required modules
const express = require('express');
const path=require("path");
const bcrypt=require("bcrypt");
const collection=require("./config");
const multer = require('multer');
const upload = multer({ dest: 'uploads/' });
const nodemailer = require('nodemailer');
const mongoose=require("mongoose");
const connect=mongoose.connect("mongodb://localhost:27017/userInfo");

const session = require("express-session");
// Initialize Express application
const app=express();
app.use(session({
    secret: 'secret', // Replace 'secret' with your desired session secret
    resave: false,
    saveUninitialized: true
}));

const requireLogin = (req, res, next) => {
    if (req.session.user) {
        // If user is logged in, proceed to the next middleware
        next();
    } else {
        // If user is not logged in, redirect to the login page
        res.redirect('/login');
    }
};

// Middleware configurations
app.use(express.json());
app.use(express.urlencoded({extended:false}));
app.set('view engine','ejs');
app.use(express.static("public"));

// Define user schema
const userSchema = new mongoose.Schema({
    email: String,
});
const User = mongoose.model('User', userSchema);

// Route definitions
app.get("/", requireLogin,(req,res)=>{
    res.render("home");
});

app.get("/home", requireLogin,(req,res)=>{
    res.render("home");
});
app.get("/signup",(req,res)=>{
    res.render("signup");
})
app.get("/FAQ", requireLogin,(req,res)=>{
    res.render("FAQ");
})
app.get("/login",(req,res)=>{
    res.render("login");
})
app.get("/aboutus", requireLogin,(req,res)=>{
    res.render("aboutus");
})
app.get("/createblog",(req,res)=>{
    res.redirect("http://127.0.0.1:7000"); 
})



app.get("/createsummary", requireLogin, (req, res) => {
    res.redirect("http://127.0.0.1:5000"); // Redirect to the specified URL
});


app.get("/privacy", requireLogin,(req,res)=>{
    res.render("privacy");
})
app.get("/review", requireLogin,(req,res)=>{
    res.render("review");
})
app.get("/dashboard", requireLogin,(req,res)=>{
    res.render("dashboard");
})
app.get("/viewsummary", requireLogin,(req,res)=>{
    res.render("viewsummary");
})


// Route for processing video form
app.post('/process_video', requireLogin, (req, res) => {
    // Process the video link
    const videoLink = req.body.video_link;
    // Here, you would generate the summary for the video
    // For demonstration purposes, let's just echo back the video link
    const summary = `Summary for video link: ${videoLink}`;
    res.send(summary);
});

// Route for processing text form
app.post('/process_text', requireLogin,async (req, res) => {
    // Process the URL
    const url = req.body.url;
    // Here, you would generate the summary for the text
    // For demonstration purposes, let's just echo back the URL
    // const summary = `Summary for URL: ${url}`;
    // res.send(summary);
    const summary = new Summary({
        type: 'text',
        content: url
    });
    await summary.save();
    res.send(summary);
});

// Route for processing audio form
app.post('/process_audio', requireLogin,upload.single('audio_file'), (req, res) => {
    // Process the uploaded audio file
    const audioFile = req.file;
    // Here, you would generate the summary for the audio file
    // For demonstration purposes, let's just echo back the filename
    const summary = `Summary for audio file: ${audioFile.filename}`;
    res.send(summary);
});
//register user
app.post("/signup",async (req,res)=>{
    const data={
        name:req.body.username,
        email:req.body.email,
        password:req.body.password
    }
    
    const existingUser=await collection.findOne({name:data.name});
    if(existingUser){
        res.send("user already exist please choose different username ");
    }
    else{
        //hash the password using bcrypt 
        const saltRounds=10;//number of salt round for bcrypt
        const hashedPassword=await bcrypt.hash(data.password,saltRounds);
        data.password=hashedPassword; //replace the hashed password with original password


        const userdata=await collection.insertMany(data);
        console.log(userdata);
        res.render("login")
        }
    
})
//login user
app.post("/login",async (req,res)=>{
    try{
        const check=await collection.findOne({name:req.body.username});
        if(!check){
            return res.send("user name con not found");
        }
        const isPasswordMatch=await bcrypt.compare(req.body.password,check.password);
        if(isPasswordMatch)
        {
            req.session.user = check;
           return res.render("home");
        }
        else{
           return req.send("wrong password");
        }
    }catch{
        return res.send("wrong  detail");
    }
     
    
});
app.get("/logout", (req, res) => {
    // Destroy session upon logout
    req.session.destroy(err => {
        if (err) {
            console.error('Error destroying session:', err);
        }
        res.redirect("/login"); // Redirect to home page after logout
    });
});
app.get('/dashboard',(req,res)=>{
    if(req.session.user)
    {
        res.render("dashboard",{user:req.session.user})
    }else{
        res.send("/login");
    }
})

const port=3000;
app.listen(port,()=>{
   console.log(`server running on port:${port}`);

})