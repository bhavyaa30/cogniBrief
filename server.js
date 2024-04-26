const express = require('express')
const articleRouter = require("./routes/articles")
const Article = require('./models/article')
const mongoose = require('mongoose')
const methodOverride = require('method-override')
const app = express()

// Connect to MongoDB
mongoose.connect('mongodb://localhost/CreateBlog')

// Set the view engine to EJS
app.set('view engine', 'ejs')

// Middleware to parse URL-encoded bodies
app.use(express.urlencoded({extended: false}))

// Middleware to override HTTP methods
app.use(methodOverride('_method'))

// Route for the homepage
app.get('/', async(req, res) => {
    const articles =await Article.find().sort({ createdAt:'desc'})
    res.render('articles/index', { articles: articles })
})

// Route for redirecting to home
app.get("/home",(req,res)=>{
    res.redirect("http://127.0.0.1:3000/home");
})

// Route for the dashboard
app.get("/dashboard",(req,res)=>{
    // res.redirect("http://127.0.0.1:5000");
    res.render("dashboard");
})
app.use('/articles', articleRouter)


// Start the server on port 7000
const port=7000;
app.listen(port,()=>{
   console.log(`server running on port:${port}`);

})