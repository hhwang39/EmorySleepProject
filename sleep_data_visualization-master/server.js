var bodyParser = require("body-parser");
var csv = require("csv");
var parse = require("csv-parse");
var express = require("express");
var formidable = require("formidable");
var fs = require("fs");
var app = express();

//TODO arrows to scroll through data (multiple steps/sizes)
//TODO improve data processing
//TODO bluetooth data transfer

var currentFile = '';
var selectionMap = [];


// parse application/x-www-form-urlencoded
app.use(bodyParser.urlencoded({ extended: false }));

// parse application/json
app.use(bodyParser.json());

// Endpoint to return csv as parsed array
app.get('/api/parse_csv', function(req, res) {
  if (currentFile === '') {
    console.log('$$$$$$$');
    res.redirect('/uploads.html');
    res.end();
  } else {
    fs.readFile(currentFile, function(err, data) {
      if (err) throw err;

      // Parse data
      parse(data, function(err, output) {
        if (err) throw err;

        output[0][4] = 'Annotation Line';

        for (var i = 1; i < output.length; i++) {
          for (var j = 0; j < output[i].length; j++) {
            if (j == 0) {
              // Make the first column represent every 0.1 second
              output[i][j] = Number( (i * 0.1).toFixed(1) );
              output[i][4] = Number( 2 );
            } else {
              // Last 3 columns are accelerometer data (XYZ)
              output[i][j] = Number( output[i][j] );
            }
          }
        }
        console.log(output.length + ' values have been parsed');
        res.send(output);
      });
    });
  }
});

//
app.post('/api/addSelection', function(req, res) {
  console.log(req.body);
  console.log(JSON.parse(req.body));
  var selection = req.body.array;
  if (selection) {
    // Check if there is already an entry
    if (selectionMap[currentFile]) {
      var index = selectionMap[currentFile].selections.length;
      selectionMap[currentFile].selections[index] = selection;
    } else {
      var index = selectionMap.length;
      selectionMap[index] = {
        'file': currentFile,
        'selections': [selection]
      };
    }
    res.status(200);
  } else {
    res.send('No selection data');
  }
  console.log('SELECTION::' + selection);
});

// Endpoint to return selections
app.get('/api/getSelections', function(req, res) {

});

// Endpoint to upload file
app.post('/api/fileupload', function(req, res) {
  var form = new formidable.IncomingForm();
  form.parse(req, function (err, fields, files) {
    var oldpath = files.filetoupload.path;
    var newpath = oldpath + files.filetoupload.name;
    console.log(newpath);
    fs.rename(oldpath, newpath, function (err) {
      if (err) throw err;
      // res.write('File uploaded and moved!');
      currentFile = newpath;
      res.redirect('/index.html');
      res.end();
    });
  });
});

//serve static file (index.html, images, css)
app.use(express.static(__dirname + '/public'));

var port = process.env.PORT || 3000;
app.listen(port, function() {
    console.log("To view your app, open this link in your browser: http://localhost:" + port);
});
