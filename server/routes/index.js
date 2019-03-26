var express = require('express');
var router = express.Router();
const mongoose = require('mongoose');

const mongo_url = `${process.env.MONGO_URL}/${process.env.MONGO_DB_NAME}?authSource=admin`; 
mongoose.connect(mongo_url,
		 {useNewUrlParser: true});

var dogSchema = new mongoose.Schema({
    title: String,
    canines: [[String, String, Number]],
    img_url: String
});

const Dog = mongoose.model('dog', dogSchema);

router.get('/api/dogs', function(req, res, next) {
    Dog.find({}, (err, docs) => {
	if (err) {
	    throw new Error(err);
	} else {
	    res.send(docs)
	};
    });
});

module.exports = router;
