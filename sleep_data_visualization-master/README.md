# Sleep Data Visualization

[Project description](http://ece4012y2017.ece.gatech.edu/fall/sd17f22/)

# Getting Started

This app runs using NodeJS. To run this app yourself follow these steps:
1. [Install NodeJS](https://nodejs.org/en/download/)
2. Clone the repository
3. Ensure you are in the root directory of the repository
4. From the command line type: ```npm install```
5. Then type ```npm start```
6. The app should now be running
7. To view the app open your broswer and navigate to [localhost:3000](http://localhost:3000)

# Application Structure

Currently the application is separated into 2 main components: front end (HTML/Javascript) and backend (NodeJS Express Server). The files in the /public directory contain the HTML and Javascript to render the charts and display the data. The server.js file contains the backend to render the HTML files as well as handle backend processes such as modifying or parsing the data rendered by the charts.

The charts are created using [Google Charts API](https://developers.google.com/chart/). 

There are sample data csv files that can be rendered in the root directory of the repository.
