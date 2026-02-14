/*
    The Server to Serve the React App
    ---------------------------------
*/

const path = require('path');
const dotenv = require('dotenv')
const result = dotenv.config( { path: path.join(__dirname, '..', '.env') } );
if (result.error) {
    throw result.error;
};

const express = require('express');

const app = express();
const port = process.env.PORT || 3000;
const basePath = process.env.PUBLIC_URL || '/';


app.use(
    basePath,
    express.static(path.join(__dirname, '..', 'build'))
);


app.get(`${basePath}{*path}`, (request, response) => {
    response.sendFile(path.join(__dirname, '..', 'build', 'index.html'));
});


app.listen(port, () => {
    if (process.platform === 'win32') {
        console.clear();
    };
    console.log(`Server is Running on Port ${port}!`);
});
